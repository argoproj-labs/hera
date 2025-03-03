# Spacy Inference Pipeline



This example showcases how to run multi-step ML pipeline to prepare data and run spacy Named Entity Recognition (NER) model inference within Hera / Argo Workflows!
Step 1: Prepares dataset using Spacy example sentences library and saves dataset the volume path /mnt/data
Step 2: Performs inference on the dataset in the volume path /mnt/data using Spacy Named Entity Recognition (NER) LLM model


=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Resources,
        Steps,
        Volume,
        Workflow,
        models as m,
        script,
    )


    @script(
        image="jupyter/datascience-notebook:latest",
        resources=Resources(cpu_request=0.5, memory_request="1Gi"),
        volume_mounts=[m.VolumeMount(name="data-dir", mount_path="/mnt/data")],
    )
    def data_prep() -> None:
        import json
        import subprocess

        from spacy.lang.en.examples import sentences

        print(subprocess.run("cd /mnt/data && ls -l", shell=True, capture_output=True).stdout.decode())
        """ the used image does not have `spacy` installed, so we need to install it first! """
        subprocess.run(
            ["pip", "install", "spacy"],
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )

        """ dumping spacy example sentences data into a file
            replace this with real dataset """
        with open("/mnt/data/input_data.json", "w") as json_file:
            json.dump(sentences, json_file)
        print("Data preparation completed")
        print(subprocess.run("cd /mnt/data && ls -l", shell=True, capture_output=True).stdout.decode())


    @script(
        image="jupyter/datascience-notebook:latest",
        resources=Resources(cpu_request=0.5, memory_request="1Gi"),
        volume_mounts=[m.VolumeMount(name="data-dir", mount_path="/mnt/data")],
    )
    def inference_spacy() -> None:
        import subprocess

        """ the used image does not have `spacy` installed, so we need to install it first! """
        subprocess.run(
            ["pip", "install", "spacy"],
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        print(subprocess.run("cd /mnt/data && ls -l ", shell=True, capture_output=True).stdout.decode())
        import json
        from typing import List

        import pydantic
        import spacy
        from pydantic import BaseModel
        from spacy.cli import download

        """ download and load spacy model https://spacy.io/models/en#en_core_web_lg """
        spacy_model_name = "en_core_web_lg"
        download(spacy_model_name)
        nlp = spacy.load(spacy_model_name)

        """ build pydantic model """
        print(pydantic.version.version_info())

        class NEROutput(BaseModel):
            input_text: str
            ner_entities: List[str] = []

        ner_output_list: List[NEROutput] = []

        """ read data prepared from previous step data_prep """
        with open("/mnt/data/input_data.json", "r") as json_file:
            input_data = json.load(json_file)
            print(input_data)
            """ iterate each sentence in the data and perform NER """
            for sentence in input_data:
                print("input text: " + sentence)
                doc = nlp(sentence)
                print("output NER:")
                ner_entities: List[str] = []
                for entity in doc.ents:
                    """ Print the entity text and its NER label """
                    ner_entity = entity.text + " is " + entity.label_
                    print(ner_entity)
                    ner_entities.append(ner_entity)
                print("ner_entities = + " + ner_entities)
                ner_output = NEROutput(input_text=sentence, ner_entities=ner_entities)
                ner_output_list.append(dict(ner_output))
            print("ner_output_list = " + ner_output_list)
        print("Inference completed")
        """ save output in a file """
        with open("/mnt/data/output_data.json", "w") as json_file:
            json.dump(ner_output_list, json_file)
        print(subprocess.run("cd /mnt/data && ls -l ", shell=True, capture_output=True).stdout.decode())


    with Workflow(
        generate_name="spacy-inference-pipeline-",
        entrypoint="spacy-inference-pipeline",
        volumes=[Volume(name="data-dir", size="1Gi", mount_path="/mnt/data")],
        service_account_name="hera",
        namespace="argo",
    ) as w:
        with Steps(name="spacy-inference-pipeline") as steps:
            data_prep(name="data-prep")
            inference_spacy(name="inference-spacy")
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: spacy-inference-pipeline-
      namespace: argo
    spec:
      entrypoint: spacy-inference-pipeline
      serviceAccountName: hera
      templates:
      - name: spacy-inference-pipeline
        steps:
        - - name: data-prep
            template: data-prep
        - - name: inference-spacy
            template: inference-spacy
      - name: data-prep
        script:
          image: jupyter/datascience-notebook:latest
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            import subprocess
            from spacy.lang.en.examples import sentences
            print(subprocess.run('cd /mnt/data && ls -l', shell=True, capture_output=True).stdout.decode())
            ' the used image does not have `spacy` installed, so we need to install it first! '
            subprocess.run(['pip', 'install', 'spacy'], stdout=subprocess.PIPE, universal_newlines=True)
            ' dumping spacy example sentences data into a file\n        replace this with real dataset '
            with open('/mnt/data/input_data.json', 'w') as json_file:
                json.dump(sentences, json_file)
            print('Data preparation completed')
            print(subprocess.run('cd /mnt/data && ls -l', shell=True, capture_output=True).stdout.decode())
          command:
          - python
          volumeMounts:
          - name: data-dir
            mountPath: /mnt/data
          resources:
            requests:
              cpu: '0.5'
              memory: 1Gi
      - name: inference-spacy
        script:
          image: jupyter/datascience-notebook:latest
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import subprocess
            ' the used image does not have `spacy` installed, so we need to install it first! '
            subprocess.run(['pip', 'install', 'spacy'], stdout=subprocess.PIPE, universal_newlines=True)
            print(subprocess.run('cd /mnt/data && ls -l ', shell=True, capture_output=True).stdout.decode())
            import json
            from typing import List
            import pydantic
            import spacy
            from pydantic import BaseModel
            from spacy.cli import download
            ' download and load spacy model https://spacy.io/models/en#en_core_web_lg '
            spacy_model_name = 'en_core_web_lg'
            download(spacy_model_name)
            nlp = spacy.load(spacy_model_name)
            ' build pydantic model '
            print(pydantic.version.version_info())

            class NEROutput(BaseModel):
                input_text: str
                ner_entities: List[str] = []
            ner_output_list: List[NEROutput] = []
            ' read data prepared from previous step data_prep '
            with open('/mnt/data/input_data.json', 'r') as json_file:
                input_data = json.load(json_file)
                print(input_data)
                ' iterate each sentence in the data and perform NER '
                for sentence in input_data:
                    print('input text: ' + sentence)
                    doc = nlp(sentence)
                    print('output NER:')
                    ner_entities: List[str] = []
                    for entity in doc.ents:
                        ' Print the entity text and its NER label '
                        ner_entity = entity.text + ' is ' + entity.label_
                        print(ner_entity)
                        ner_entities.append(ner_entity)
                    print('ner_entities = + ' + ner_entities)
                    ner_output = NEROutput(input_text=sentence, ner_entities=ner_entities)
                    ner_output_list.append(dict(ner_output))
                print('ner_output_list = ' + ner_output_list)
            print('Inference completed')
            ' save output in a file '
            with open('/mnt/data/output_data.json', 'w') as json_file:
                json.dump(ner_output_list, json_file)
            print(subprocess.run('cd /mnt/data && ls -l ', shell=True, capture_output=True).stdout.decode())
          command:
          - python
          volumeMounts:
          - name: data-dir
            mountPath: /mnt/data
          resources:
            requests:
              cpu: '0.5'
              memory: 1Gi
      volumeClaimTemplates:
      - metadata:
          name: data-dir
        spec:
          accessModes:
          - ReadWriteOnce
          resources:
            requests:
              storage: 1Gi
    ```

