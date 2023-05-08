"""
# Example on specifying parallelism on the outer DAG and limiting the number of its
# children DAGs to be run at the same time.
#
# As the parallelism of A is 2, only two of the three DAGs (b2, b3, b4) will start
# running after b1 is finished, and the left DAG will run after either one is finished.

apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: parallelism-nested-dag-
spec:
  entrypoint: A
  templates:
  - name: A
    parallelism: 2
    dag:
      tasks:
      - name: b1
        template: B
        arguments:
          parameters:
          - name: msg
            value: "1"
      - name: b2
        template: B
        depends: "b1"
        arguments:
          parameters:
          - name: msg
            value: "2"
      - name: b3
        template: B
        depends: "b1"
        arguments:
          parameters:
          - name: msg
            value: "3"
      - name: b4
        template: B
        depends: "b1"
        arguments:
          parameters:
          - name: msg
            value: "4"
      - name: b5
        template: B
        depends: "b2 && b3 && b4"
        arguments:
          parameters:
          - name: msg
            value: "5"

  - name: B
    inputs:
      parameters:
      - name: msg
    dag:
      tasks:
      - name: c1
        template: one-job
        arguments:
          parameters:
          - name: msg
            value: "{{inputs.parameters.msg}} c1"
      - name: c2
        template: one-job
        depends: "c1"
        arguments:
          parameters:
          - name: msg
            value: "{{inputs.parameters.msg}} c2"
      - name: c3
        template: one-job
        depends: "c1"
        arguments:
          parameters:
          - name: msg
            value: "{{inputs.parameters.msg}} c3"

  - name: one-job
    inputs:
      parameters:
      - name: msg
    container:
      image: alpine
      command: ['/bin/sh', '-c']
      args: ["echo {{inputs.parameters.msg}}; sleep 10"]
"""

from hera.workflows import Workflow, DAG, Parameter, Container

one_job = Container(
    name="one-job",
    inputs=Parameter(name="msg"),
    image="alpine",
    command=["/bin/sh", "-c"],
    args=["echo {{inputs.parameters.msg}}; sleep 10"],
)

with Workflow(generate_name="parallelism-nested-dag-", entrypoint="A") as w:
    with DAG(name="B", inputs=Parameter(name="msg")) as B:
        c1 = one_job(name="c1", arguments={"msg": "{{inputs.parameters.msg}} c1"})
        c2 = one_job(name="c2", arguments={"msg": "{{inputs.parameters.msg}} c2"})
        c3 = one_job(name="c3", arguments={"msg": "{{inputs.parameters.msg}} c3"})
        c1 >> [c2, c3]

    with DAG(name="A", parallelism=2) as A:
        b1 = B(name="b1", arguments={"msg": "1"})
        b2 = B(name="b2", arguments={"msg": "2"})
        b3 = B(name="b3", arguments={"msg": "3"})
        b4 = B(name="b4", arguments={"msg": "4"})
        b5 = B(name="b5", arguments={"msg": "5"})
        b1 >> [b2, b3, b4] >> b5
