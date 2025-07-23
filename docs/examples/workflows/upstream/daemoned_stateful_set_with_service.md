# Daemoned Stateful Set With Service

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/daemoned-stateful-set-with-service.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Resource, Step, Steps, Workflow

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="daemoned-stateful-set-with-service-",
        entrypoint="create-wait-and-test",
        on_exit="delete",
    ) as w:
        with Steps(
            name="create-wait-and-test",
        ) as invocator:
            with invocator.parallel():
                Step(
                    name="create-service",
                    template="create-service",
                )
                Step(
                    name="create-stateful-set",
                    template="create-stateful-set",
                )
            Step(
                name="wait-stateful-set",
                template="wait-stateful-set",
            )
            Step(
                name="test",
                template="test",
            )
        with Steps(
            name="delete",
        ) as invocator:
            with invocator.parallel():
                Step(
                    name="delete-service",
                    template="delete-service",
                )
                Step(
                    name="delete-stateful-set",
                    template="delete-stateful-set",
                )
        Resource(
            name="create-service",
            action="create",
            manifest="apiVersion: v1\nkind: Service\nmetadata:\n  name: nginx\n  labels:\n    app: nginx\nspec:\n  ports:\n    - port: 80\n      name: web\n  clusterIP: None\n  selector:\n    app: nginx\n",
        )
        Resource(
            name="create-stateful-set",
            action="create",
            manifest='apiVersion: apps/v1\nkind: StatefulSet\nmetadata:\n  name: web\nspec:\n  selector:\n    matchLabels:\n      app: nginx # has to match .spec.template.metadata.labels\n  serviceName: "nginx"\n  template:\n    metadata:\n      labels:\n        app: nginx # has to match .spec.selector.matchLabels\n    spec:\n      terminationGracePeriodSeconds: 10\n      containers:\n        - name: nginx\n          image: registry.k8s.io/nginx-slim:0.8\n          ports:\n            - containerPort: 80\n              name: web\n',
        )
        Resource(
            name="wait-stateful-set",
            action="get",
            manifest="apiVersion: apps/v1\nkind: StatefulSet\nmetadata:\n  name: web\n",
            success_condition="status.readyReplicas == 1",
        )
        Container(
            name="test",
            args=["curl nginx"],
            command=["sh", "-c"],
            image="curlimages/curl:latest",
        )
        Resource(
            name="delete-service",
            action="delete",
            flags=["--ignore-not-found"],
            manifest="apiVersion: v1\nkind: Service\nmetadata:\n  name: nginx\n",
        )
        Resource(
            name="delete-stateful-set",
            action="delete",
            flags=["--ignore-not-found"],
            manifest="apiVersion: apps/v1\nkind: StatefulSet\nmetadata:\n  name: web\n",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: daemoned-stateful-set-with-service-
    spec:
      entrypoint: create-wait-and-test
      onExit: delete
      templates:
      - name: create-wait-and-test
        steps:
        - - name: create-service
            template: create-service
          - name: create-stateful-set
            template: create-stateful-set
        - - name: wait-stateful-set
            template: wait-stateful-set
        - - name: test
            template: test
      - name: delete
        steps:
        - - name: delete-service
            template: delete-service
          - name: delete-stateful-set
            template: delete-stateful-set
      - name: create-service
        resource:
          action: create
          manifest: |
            apiVersion: v1
            kind: Service
            metadata:
              name: nginx
              labels:
                app: nginx
            spec:
              ports:
                - port: 80
                  name: web
              clusterIP: None
              selector:
                app: nginx
      - name: create-stateful-set
        resource:
          action: create
          manifest: |
            apiVersion: apps/v1
            kind: StatefulSet
            metadata:
              name: web
            spec:
              selector:
                matchLabels:
                  app: nginx # has to match .spec.template.metadata.labels
              serviceName: "nginx"
              template:
                metadata:
                  labels:
                    app: nginx # has to match .spec.selector.matchLabels
                spec:
                  terminationGracePeriodSeconds: 10
                  containers:
                    - name: nginx
                      image: registry.k8s.io/nginx-slim:0.8
                      ports:
                        - containerPort: 80
                          name: web
      - name: wait-stateful-set
        resource:
          action: get
          manifest: |
            apiVersion: apps/v1
            kind: StatefulSet
            metadata:
              name: web
          successCondition: status.readyReplicas == 1
      - name: test
        container:
          image: curlimages/curl:latest
          args:
          - curl nginx
          command:
          - sh
          - -c
      - name: delete-service
        resource:
          action: delete
          manifest: |
            apiVersion: v1
            kind: Service
            metadata:
              name: nginx
          flags:
          - --ignore-not-found
      - name: delete-stateful-set
        resource:
          action: delete
          manifest: |
            apiVersion: apps/v1
            kind: StatefulSet
            metadata:
              name: web
          flags:
          - --ignore-not-found
    ```

