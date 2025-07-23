# Artifacts Workflowtemplate

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/artifacts-workflowtemplate.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import ContainerNode, ContainerSet, WorkflowTemplate
    from hera.workflows.models import (
        ArchiveStrategy,
        Artifact,
        EmptyDirVolumeSource,
        HTTPArtifact,
        Inputs,
        NoneStrategy,
        Outputs,
        S3Artifact,
        Volume,
        VolumeMount,
    )

    with WorkflowTemplate(
        api_version="argoproj.io/v1alpha1",
        kind="WorkflowTemplate",
        annotations={
            "workflows.argoproj.io/description": "This example shows how to produce different types of artifact.\n"
        },
        name="artifacts",
        entrypoint="main",
    ) as w:
        with ContainerSet(
            inputs=Inputs(
                artifacts=[
                    Artifact(
                        http=HTTPArtifact(
                            url="https://datahub.io/core/global-temp/r/annual.csv",
                        ),
                        name="temps",
                        path="/in/annual.csv",
                    )
                ],
            ),
            name="main",
            outputs=Outputs(
                artifacts=[
                    Artifact(
                        archive=ArchiveStrategy(
                            none=NoneStrategy(),
                        ),
                        name="text-file",
                        path="/out/hello.txt",
                        s3=S3Artifact(
                            key="hello.txt",
                        ),
                    ),
                    Artifact(
                        archive=ArchiveStrategy(
                            none=NoneStrategy(),
                        ),
                        name="json-file",
                        path="/out/hello.json",
                        s3=S3Artifact(
                            key="hello.json",
                        ),
                    ),
                    Artifact(
                        archive=ArchiveStrategy(
                            none=NoneStrategy(),
                        ),
                        name="css-file",
                        path="/out/assets/styles.css",
                        s3=S3Artifact(
                            key="styles.css",
                        ),
                    ),
                    Artifact(
                        archive=ArchiveStrategy(
                            none=NoneStrategy(),
                        ),
                        name="malicious-file",
                        path="/out/malicious.html",
                        s3=S3Artifact(
                            key="malicious.html",
                        ),
                    ),
                    Artifact(
                        archive=ArchiveStrategy(
                            none=NoneStrategy(),
                        ),
                        name="report",
                        path="/out",
                        s3=S3Artifact(
                            key="report/",
                        ),
                    ),
                    Artifact(
                        name="tgz-file",
                        path="/out/hello.txt",
                        s3=S3Artifact(
                            key="file.tgz",
                        ),
                    ),
                    Artifact(
                        name="tgz-dir",
                        path="/out",
                        s3=S3Artifact(
                            key="dir.tgz",
                        ),
                    ),
                ],
            ),
            volumes=[
                Volume(
                    empty_dir=EmptyDirVolumeSource(),
                    name="in",
                ),
                Volume(
                    empty_dir=EmptyDirVolumeSource(),
                    name="out",
                ),
            ],
            volume_mounts=[
                VolumeMount(
                    mount_path="/in",
                    name="in",
                ),
                VolumeMount(
                    mount_path="/out",
                    name="out",
                ),
            ],
        ) as invocator:
            ContainerNode(
                image="argoproj/argosay:v2",
                name="setup",
                args=["mkdir -p /out/assets\n"],
                command=["sh", "-c"],
            )
            ContainerNode(
                image="remuslazar/gnuplot",
                name="gnuplot",
                args=[
                    "-e",
                    "set xlabel 'Year'; set ylabel 'Mean';\nset grid;\nset datafile separator ',';\nset term png size 600,400;\nset output '/out/assets/global-temp.png';\nplot '/in/annual.csv' every 2::0 skip 1 using 2:3 title 'Global Temperature' with lines linewidth 2;\n",
                ],
                dependencies=["setup"],
            )
            ContainerNode(
                image="argoproj/argosay:v2",
                name="main",
                args=[
                    "cowsay \"hello world\" > /out/hello.txt\n\ncat > /out/hello.json <<EOF\n{\"hello\": {\"world\": true}} \nEOF\n\necho '* {font-family: sans-serif}' > /out/assets/styles.css\n\ncat > /out/index.html <<EOF\n<html>\n  <head>\n    <link rel='stylesheet' href='assets/styles.css' type='text/css'/>\n  </head>\n  <body>\n    <h1>Global Temperature</h1>\n    <img src='assets/global-temp.png'/>\n  </body>\n</html>\nEOF\n\ncat > /out/malicious.html <<EOF\n<html>\n  <body>\n    <script>alert(1)</script>\n    <p>This page attempts to run a script that shows an alert, but the Argo Server UI Content-Security-Policy will prevent that.</p>\n    <p>To check, open your Web Console and see that \"Blocked script execution ... because the document's frame is sandboxed.\" (or similar) is printed.</p>\n  </body>\n</html>\nEOF\n"
                ],
                command=["sh", "-c"],
                dependencies=["setup"],
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: WorkflowTemplate
    metadata:
      name: artifacts
      annotations:
        workflows.argoproj.io/description: |
          This example shows how to produce different types of artifact.
    spec:
      entrypoint: main
      templates:
      - name: main
        volumes:
        - name: in
          emptyDir: {}
        - name: out
          emptyDir: {}
        containerSet:
          containers:
          - name: setup
            image: argoproj/argosay:v2
            args:
            - |
              mkdir -p /out/assets
            command:
            - sh
            - -c
          - name: gnuplot
            image: remuslazar/gnuplot
            args:
            - -e
            - |
              set xlabel 'Year'; set ylabel 'Mean';
              set grid;
              set datafile separator ',';
              set term png size 600,400;
              set output '/out/assets/global-temp.png';
              plot '/in/annual.csv' every 2::0 skip 1 using 2:3 title 'Global Temperature' with lines linewidth 2;
            dependencies:
            - setup
          - name: main
            image: argoproj/argosay:v2
            args:
            - "cowsay \"hello world\" > /out/hello.txt\n\ncat > /out/hello.json <<EOF\n\
              {\"hello\": {\"world\": true}} \nEOF\n\necho '* {font-family: sans-serif}'\
              \ > /out/assets/styles.css\n\ncat > /out/index.html <<EOF\n<html>\n  <head>\n\
              \    <link rel='stylesheet' href='assets/styles.css' type='text/css'/>\n\
              \  </head>\n  <body>\n    <h1>Global Temperature</h1>\n    <img src='assets/global-temp.png'/>\n\
              \  </body>\n</html>\nEOF\n\ncat > /out/malicious.html <<EOF\n<html>\n  <body>\n\
              \    <script>alert(1)</script>\n    <p>This page attempts to run a script\
              \ that shows an alert, but the Argo Server UI Content-Security-Policy will\
              \ prevent that.</p>\n    <p>To check, open your Web Console and see that\
              \ \"Blocked script execution ... because the document's frame is sandboxed.\"\
              \ (or similar) is printed.</p>\n  </body>\n</html>\nEOF\n"
            command:
            - sh
            - -c
            dependencies:
            - setup
          volumeMounts:
          - name: in
            mountPath: /in
          - name: out
            mountPath: /out
        inputs:
          artifacts:
          - name: temps
            path: /in/annual.csv
            http:
              url: https://datahub.io/core/global-temp/r/annual.csv
        outputs:
          artifacts:
          - name: text-file
            path: /out/hello.txt
            archive:
              none: {}
            s3:
              key: hello.txt
          - name: json-file
            path: /out/hello.json
            archive:
              none: {}
            s3:
              key: hello.json
          - name: css-file
            path: /out/assets/styles.css
            archive:
              none: {}
            s3:
              key: styles.css
          - name: malicious-file
            path: /out/malicious.html
            archive:
              none: {}
            s3:
              key: malicious.html
          - name: report
            path: /out
            archive:
              none: {}
            s3:
              key: report/
          - name: tgz-file
            path: /out/hello.txt
            s3:
              key: file.tgz
          - name: tgz-dir
            path: /out
            s3:
              key: dir.tgz
    ```

