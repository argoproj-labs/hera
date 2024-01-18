# Wandb Ml Monitoring



This example showcases how to use the `wandb` integration with Hera.

Weights and Biases (wandb) is a tool for tracking machine learning experiments. It can be deployed in the same
K8s cluster that Argo Workflows is running in, or hosted on a remote server. This example showcases how to use
wandb through a Hera script. For more info see: https://docs.wandb.ai/guides

Note that actually running this requires setting up the right secrets that point to your wandb API key and your own
wandb server!


=== "Hera"

    ```python linenums="1"
    import random

    import wandb

    from hera.workflows import DAG, SecretEnv, Workflow, script


    @script(env=SecretEnv(name="WANDB_API_KEY", secret_name="wandb-api-key", secret_key="wandb-api-key"))
    def train_model(project_name: str, learning_rate: float, architecture: str, dataset: str, epochs: int) -> None:
        # start a new wandb run to track this script
        wandb.init(
            # set the wandb project where this run will be logged
            project=project_name,
            # track hyperparameters and run metadata
            config={
                "learning_rate": learning_rate,
                "architecture": architecture,
                "dataset": dataset,
                "epochs": epochs,
            },
        )

        # simulate training
        epochs = 10
        offset = random.random() / 5
        for epoch in range(2, epochs):
            # mock accuracy and loss
            acc = 1 - 2**-epoch - random.random() / epoch - offset
            loss = 2**-epoch + random.random() / epoch + offset

            # log metrics to wandb
            wandb.log({"acc": acc, "loss": loss})

        # [optional] finish the wandb run, necessary in notebooks
        wandb.finish()


    with Workflow(name="wandb-ml-monitoring", entrypoint="train") as w:
        with DAG(name="train"):
            train_model(
                # `name` refers to the Argo Workflows task that gets automatically created upon invoking `train_model`
                # inside a DAG context. That's because only a Task can be a child of a DAG. Alternatively, you can use
                # Steps, in which case these invocation would create a WorkflowStep!
                name="train-1",
                arguments=dict(
                    project_name="wandb-ml-monitoring",
                    learning_rate=1e-1,
                    architecture="CNN",
                    dataset="MNIST",
                    epochs=10,
                ),
            )
            # here we train another model with different configurations but the same project name so that wandb records
            # training in the same run. Then we can easily compare the runs in the same project to see how our
            # hyperparameter choices lead to different model training performance
            train_model(
                name="train-2",
                arguments=dict(
                    project_name="wandb-ml-monitoring",
                    learning_rate=1e-2,
                    architecture="CNN",
                    dataset="MNIST",
                    epochs=10,
                ),
            )
            # note that you can easily make a hyperparameter search grid by invoking `train_model` inside the loop over
            # the results of `itertools.combinations` or `itertools.product`!
            train_model(
                name="train-3",
                arguments=dict(
                    project_name="wandb-ml-monitoring",
                    learning_rate=1e-3,
                    architecture="CNN",
                    dataset="MNIST",
                    epochs=10,
                ),
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      name: wandb-ml-monitoring
    spec:
      entrypoint: train
      templates:
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: project_name
                value: wandb-ml-monitoring
              - name: learning_rate
                value: '0.1'
              - name: architecture
                value: CNN
              - name: dataset
                value: MNIST
              - name: epochs
                value: '10'
            name: train-1
            template: train-model
          - arguments:
              parameters:
              - name: project_name
                value: wandb-ml-monitoring
              - name: learning_rate
                value: '0.01'
              - name: architecture
                value: CNN
              - name: dataset
                value: MNIST
              - name: epochs
                value: '10'
            name: train-2
            template: train-model
          - arguments:
              parameters:
              - name: project_name
                value: wandb-ml-monitoring
              - name: learning_rate
                value: '0.001'
              - name: architecture
                value: CNN
              - name: dataset
                value: MNIST
              - name: epochs
                value: '10'
            name: train-3
            template: train-model
        name: train
      - inputs:
          parameters:
          - name: project_name
          - name: learning_rate
          - name: architecture
          - name: dataset
          - name: epochs
        name: train-model
        script:
          command:
          - python
          env:
          - name: WANDB_API_KEY
            valueFrom:
              secretKeyRef:
                key: wandb-api-key
                name: wandb-api-key
          image: python:3.8
          source: "import os\nimport sys\nsys.path.append(os.getcwd())\nimport json\n\
            try: architecture = json.loads(r'''{{inputs.parameters.architecture}}''')\n\
            except: architecture = r'''{{inputs.parameters.architecture}}'''\ntry: dataset\
            \ = json.loads(r'''{{inputs.parameters.dataset}}''')\nexcept: dataset = r'''{{inputs.parameters.dataset}}'''\n\
            try: epochs = json.loads(r'''{{inputs.parameters.epochs}}''')\nexcept: epochs\
            \ = r'''{{inputs.parameters.epochs}}'''\ntry: learning_rate = json.loads(r'''{{inputs.parameters.learning_rate}}''')\n\
            except: learning_rate = r'''{{inputs.parameters.learning_rate}}'''\ntry: project_name\
            \ = json.loads(r'''{{inputs.parameters.project_name}}''')\nexcept: project_name\
            \ = r'''{{inputs.parameters.project_name}}'''\n\nwandb.init(project=project_name,\
            \ config={'learning_rate': learning_rate, 'architecture': architecture, 'dataset':\
            \ dataset, 'epochs': epochs})\nepochs = 10\noffset = random.random() / 5\n\
            for epoch in range(2, epochs):\n    acc = 1 - 2 ** (-epoch) - random.random()\
            \ / epoch - offset\n    loss = 2 ** (-epoch) + random.random() / epoch + offset\n\
            \    wandb.log({'acc': acc, 'loss': loss})\nwandb.finish()"
    ```

