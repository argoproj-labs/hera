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

    from hera.workflows import DAG, SecretEnv, Workflow, script


    @script(
        # we use the `runner` constructor so that Hera automatically infers the path to our method, and assembles a
        # container for us, which will run remotely, on Argo / K8s.
        constructor="runner",
        # here we set the environment variable that contains the W&B API key
        env=SecretEnv(name="WANDB_API_KEY", secret_name="wandb-api-key", secret_key="wandb-api-key"),
    )
    def train_model(project_name: str, learning_rate: float, architecture: str, dataset: str, epochs: int) -> None:
        # TODO: move this import outside of the script. It is added here so that `wandb` does not need to be added as a
        #       dependency to Hera
        import wandb

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
            # mock accuracy and loss, this is where you'd actually have a model training
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
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.use_cases.wandb_ml_monitoring:train_model
          command:
          - python
          env:
          - name: WANDB_API_KEY
            valueFrom:
              secretKeyRef:
                key: wandb-api-key
                name: wandb-api-key
          image: python:3.9
          source: '{{inputs.parameters}}'
    ```

