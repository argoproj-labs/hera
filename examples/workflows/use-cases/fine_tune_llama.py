"""This example contains the code and instructions to reproduce the demo presented in the talk titled
"How to fine tune an LLM with Argo Workflows and Hera" KubeCon NA 2023, by Flaviu Vadan and JP Zivalich:
- https://colocatedeventsna2023.sched.com/event/1Rj3z/how-to-train-an-llm-with-argo-workflows-and-hera-jp-zivalich-pipekit-flaviu-vadan-dyno-therapeutics
- https://www.youtube.com/watch?v=nRYf3GkKpss&t=4s&pp=ygURZmxhdml1IHZhZGFuIGxsbXM%3D

This module provides the core workflow scheduling logic that:
1. Spins up the necessary etcd resources for distributed training
2. Created the containers that run the training job using `torchrun`
3. Delete the etcd resources after the training job is done

There are several implicit dependencies in this script:
1. You need a K8s secret called `hf-token` with a field `token` that contains the Huggingface authentication token.
   While not ideal because it's either encoded as plain text or base64 encoded, this is the simplest way to pass the
   token for the talk purposes :) your own infrastructure might have more secure ways to provide this token, such as
   a secret vault that uses a specific service account for authentication/authorization to fetch the token
"""
from random import randint

from hera.workflows import (
    DAG,
    Container,
    EmptyDirVolume,
    FieldEnv,
    Parameter,
    Resource,
    Resources,
    SecretEnv,
    Workflow,
    models as m,
)

"""NUM_NODES dictates the number of nodes that training should run on."""
NUM_NODES = 4

"""`create_ssd_storage_class` defines the K8s storage class required for an ssd that's created dynamically.
 
K8s will create the necessary PersistentVolumeClaim and PersistentVolume resources when a pod requests a volume
rather than when the PVC/PV are _defined_. This helps avoid the risk of pod + volume zone mismatches. Note that this 
was tested in GCP / GKE specifically. If you have a different cloud provider you have to change the `provisioner` 
field.
"""
create_ssd_storage_class = Resource(
    name="create-ssd-storage-class",
    action="create",
    manifest="""
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: ssd
provisioner: kubernetes.io/gce-pd
volumeBindingMode: WaitForFirstConsumer
parameters:
  type: pd-ssd
""",
)

# the etcd load balancer resource exposes the etcd replica set to the outside world and within the cluster. One could
# also experiment with using the ClusterIP service type
create_etcd_load_balancer = Resource(
    name="create-etcd-load-balancer",
    action="create",
    manifest="""
apiVersion: v1
kind: Service
metadata:
  name: etcd-client
spec:
  type: LoadBalancer
  ports:
    - name: etcd-client
      port: 2379
      protocol: TCP
      targetPort: 2379
  selector:
    app: etcd""",
    outputs=Parameter(name="etcd-svc-name", value_from=m.ValueFrom(json_path="metadata.name")),
)

# the etcd stateful set provides 3 replicate of etcd
create_etcd_stateful_set = Resource(
    name="create-etcd-stateful-set",
    action="create",
    manifest="""
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: etcd
  labels:
    app: etcd
spec:
  serviceName: etcd
  selector:
    matchLabels:
      app: etcd
  replicas: 3
  template:
    metadata:
      name: etcd
      labels:
        app: etcd
    spec:
      containers:
        - name: etcd
          image: quay.io/coreos/etcd:latest
          ports:
            - containerPort: 2379
              name: client
            - containerPort: 2380
              name: peer
          volumeMounts:
            - name: data
              mountPath: /var/run/etcd
          command:
            - /bin/sh
            - -c
            - |
              PEERS="etcd-0=http://etcd-0.etcd:2380,etcd-1=http://etcd-1.etcd:2380,etcd-2=http://etcd-2.etcd:2380"
              exec etcd --name ${HOSTNAME} \
                --listen-peer-urls http://0.0.0.0:2380 \
                --listen-client-urls http://0.0.0.0:2379 \
                --advertise-client-urls http://${HOSTNAME}.etcd:2379 \
                --initial-advertise-peer-urls http://${HOSTNAME}:2380 \
                --initial-cluster-token etcd-cluster-1 \
                --initial-cluster ${PEERS} \
                --initial-cluster-state new \
                --data-dir /var/run/etcd/default.etcd
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        storageClassName: ssd
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 1Gi""",
)


"""The delete resource removes the etcd client load balancer and the stateful set.

Useful for cases when you want to dynamically spin up an etcd cluster and then delete it after the client application 
is done.
"""
delete_etcd_resources = Resource(
    name="delete-etcd-pod",
    action="delete",
    flags=["svc/etcd-client", "sts/etcd"],
)

"""Wait for the etcd load balancer to get an IP address.

This is a workaround for the fact that the etcd load balancer does not get an IP address immediately after it is
created. This script will wait until the load balancer has an IP address before exiting and expose the IP via an
output parameter.
"""
wait_for_etcd_ip = Container(
    name="wait-for-etcd-load-balancer-ip",
    image="alpine/k8s:1.23.17",
    command=["bash -c"],
    args=[
        'etcd_ip=""; while [ -z $etcd_ip ]; do echo "Waiting for end point..."; etcd_ip=$(kubectl get svc etcd-client --template="{{range .status.loadBalancer.ingress}}{{.ip}}{{end}}"); [ -z "$etcd_ip" ] && sleep 10; done; echo "End point ready-" && echo $etcd_ip > /etcd-ip;'
    ],
    inputs=Parameter(name="service-name"),
    outputs=Parameter(name="etcd-ip", value_from=m.ValueFrom(path="/etcd-ip")),
)


"""finetune is the main container that runs part of a training job given node configuration."""
finetune = Container(
    name="fine-tune-rank-n",
    env=[
        SecretEnv(name="HF_TOKEN", secret_name="hf-token", secret_key="token"),
        FieldEnv(name="LOCAL_IP", field_path="status.podIP"),
    ],
    # the following is a public image built for the talk. It only contains the files in this repo along with an update
    # to a torch dev / nightly version so that we can use the latest FSDP features and PEFT. Ofc, you can build your
    # own image with the same files and use that instead! See repo linked at the top of the file for more details.
    image="flaviuvadan/kubecon-na-23-finetune-llama2:latest",
    image_pull_policy="Always",
    # https://pytorch.org/docs/stable/elastic/run.html
    command=["torchrun"],
    args=[
        # the number of K8s nodes to use for training. For the talk this was tested on 1 node with 4 GPUs and
        # also tested on 4 nodes with 4 GPUs = 16 GPU training
        "--nnodes",
        NUM_NODES,
        # the number of processes per node / number of GPUs
        "--nproc-per-node",
        NUM_NODES,
        # randezvous backend is the mechanism used to coordinate the training job. etcd-v2 is the recommended one for
        # `nnodes` > 1 while c10d is recommended for single node training. Note, the use of the v2 etcd API must be
        # enabled by the etcd resource
        "--rdzv-backend",
        "etcd-v2",
        # the etcd endpoint is the load balancer service that exposes the etcd pods
        "--rdzv-endpoint",
        "{{inputs.parameters.etcd-ip}}:2379",
        # the rdzv id is a unique identifier for the training job. It's used to coordinate the training job
        "--rdzv-id",
        "{{inputs.parameters.rdvz-id}}",
        # the node rank is the rank of the current node in the training job. It's used to coordinate the training job.
        # Rank 0 is the "main" rank that contains the officially finetuned model whereas the other nodes are "worker"
        # nodes / ranks
        "--node-rank",
        "{{inputs.parameters.node-rank}}",
        # the local address is the IP address of the current node
        "--local-addr",
        "$(LOCAL_IP)",
        # the maximum number of worker group restarts before the whole job fails
        "--max-restarts",
        "3",
        # the actual training job path within the container
        "/kubecon_na_23_llama2_finetune/src/talk/finetune.py",
    ],
    inputs=[
        Parameter(name="rdvz-id"),
        Parameter(name="node-rank"),
        Parameter(name="node-vol"),
        Parameter(name="etcd-ip"),
    ],
    # these were identified empirically / by trial + some online documentation about LLM training
    resources=Resources(cpu_request=8, cpu_limit=12, memory_request="112Gi", memory_limit="120Gi", gpus=4),
    tolerations=[m.Toleration(key="nvidia.com/gpu", operator="Equal", value="present", effect="NoSchedule")],
    node_selector={"cloud.google.com/gke-accelerator": "nvidia-tesla-v100"},
    volumes=[
        # Add an empty dir volume to multi-GPU tasks to enable shared memory communication between GPUs.
        # If this is not set the training job might fail with an error like: `Python bus error`. This is because the
        # job attempts to access the shared memory space of the node for intercommunication, and if Linux catches an
        # invalid  memory access _without_ /dev/shm mounted, then it will manifest as a bus error.
        EmptyDirVolume(name="gpu-comm", size_limit="50Gi", mount_path="/dev/shm"),
    ],
    volume_mounts=[
        # here we use a dynamic volume mount because we expect the workflow to spin up a number of volumes equal to the
        # number of nodes we use for training. If this were to use the `volumes` field it would spin up a single volume
        # in `ReadWriteOnce`, preventing the different nodes to mount the same disk. This would work if you have a
        # network volume with `ReadWriteMany` access mode, though!
        m.VolumeMount(
            mount_path="/kubecon_na_23_llama2_finetune/finetune",
            name="{{inputs.parameters.node-vol}}",
        ),
        # in addition, we set a volume mount for the empty dir volume that we use for communication between GPUs
        m.VolumeMount(mount_path="/dev/shm", name="gpu-comm"),
    ],
)

# the main workflow that schedules:
# 1. etcd resource creation
# 2. Actual training job
# 3. etcd resource deletion
with Workflow(
    generate_name="fine-tune-llm-",
    entrypoint="fine-tune",
    # these volume claim templates are the ones use for dynamically spinning up volumes for the training job, equal
    # to the number of nodes that are created for training
    volume_claim_templates=[
        m.PersistentVolumeClaim(
            metadata=m.ObjectMeta(name=f"rank-{i}"),
            spec=m.PersistentVolumeClaimSpec(
                resources=m.ResourceRequirements(requests={"storage": "20Gi"}, limits={"storage": "20Gi"}),
                # TODO: it's possible to spin up pods in one zone of a region and a disk in another zone of a region!
                #       I recommend setting a `storage_class_name` that specifically tells K8s that it should create
                #       the volumes only when pods actually want to _mount_ a volume! That way the disks are
                #       provisioned in the same zone as the pods are. You will likely need a custom K8s storage class
                #       that uses `volumeBindingMode: WaitForFirstConsumer` :)
                #       see `create_ssd_storage_class` for more details!
                storage_class_name="ssd",
                access_modes=["ReadWriteOnce"],
            ),
        )
        for i in range(0, NUM_NODES)
    ],
) as w:
    # a random ID for the training job. This is used to coordinate the training job and it can be any integer
    rdvz_id = randint(1, 10_000)
    with DAG(name="fine-tune"):
        (
            create_ssd_storage_class()
            >> [
                create_etcd_stateful_set(),
                create_etcd_load_balancer(),
            ]
            >> wait_for_etcd_ip(
                arguments={"service-name": "{{tasks.create-etcd-load-balancer.outputs.parameters.etcd-svc-name}}"}
            )
            >> [
                finetune(
                    name=f"finetune-rank-{i}",
                    arguments={
                        "rdvz-id": rdvz_id,
                        "node-rank": i,
                        "node-vol": f"rank-{i}",
                        "etcd-ip": "{{tasks.wait-for-etcd-load-balancer-ip.outputs.parameters.etcd-ip}}",
                    },
                )
                for i in range(0, NUM_NODES)
            ]
        )

    # clean up the created resources
    with DAG(name="exit") as exit_dag:
        delete_etcd_resources()

    w.on_exit = exit_dag
