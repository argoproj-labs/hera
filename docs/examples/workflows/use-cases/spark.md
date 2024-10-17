# Spark



This example showcases how to run PySpark within Hera / Argo Workflows!

This is not a comprehensive example that showcases how to spin up a Spark cluster, but rather a simple example that
compares a regular Pandas dataframe with a Spark dataframe. Inspired by: https://sparkbyexamples.com/pyspark-tutorial/


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Resources, Workflow, script


    @script(image="jupyter/pyspark-notebook:latest", resources=Resources(cpu_request=4, memory_request="8Gi"))
    def spark(num_data: int) -> None:
        import random
        import subprocess
        import time

        # the used image does not have `pyspark` or `pandas` installed, so we need to install it first!
        subprocess.run(
            ["pip", "install", "pyspark", "pandas"],
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )

        import pandas as pd
        from pyspark.sql import SparkSession

        spark = SparkSession.builder.master("local[1]").appName("my-spark-example-running-in-hera.com").getOrCreate()

        # let's compare a regular dataframe vs a spark dataframe! First, we define the data to use
        data, columns = [random.randint(0, num_data) for _ in range(num_data)], ["value"]

        # as a very simple and naive comparison, let's print out the average, min, and max of both dataframes
        # and now let's create a regular Pandas dataframe
        pandas_df = pd.DataFrame(data=data, columns=columns)
        start = time.time()
        pandas_result = pandas_df.describe()
        pandas_elapsed = time.time() - start
        print("Pandas dataframe: ")
        print(pandas_result)
        print("Pandas dataframe took {pandas_elapsed} seconds to compute".format(pandas_elapsed=pandas_elapsed))

        # now let's create a Spark dataframe with the said data!
        spark_df = spark.createDataFrame(data=pandas_df, schema=columns)

        start = time.time()
        spark_result = spark_df.describe()
        spark_elapsed = time.time() - start
        print("Spark dataframe: ")
        print(spark_result)
        print("Spark dataframe took {spark_elapsed} seconds to compute".format(spark_elapsed=spark_elapsed))


    with Workflow(generate_name="spark-", entrypoint="d") as w:
        with DAG(name="d"):
            for i, num_data in enumerate([1_000, 10_000, 100_000, 1_000_000, 10_000_000, 100_000_000]):
                spark(name="spark-{i}".format(i=i), arguments={"num_data": num_data})
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: spark-
    spec:
      entrypoint: d
      templates:
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: num_data
                value: '1000'
            name: spark-0
            template: spark
          - arguments:
              parameters:
              - name: num_data
                value: '10000'
            name: spark-1
            template: spark
          - arguments:
              parameters:
              - name: num_data
                value: '100000'
            name: spark-2
            template: spark
          - arguments:
              parameters:
              - name: num_data
                value: '1000000'
            name: spark-3
            template: spark
          - arguments:
              parameters:
              - name: num_data
                value: '10000000'
            name: spark-4
            template: spark
          - arguments:
              parameters:
              - name: num_data
                value: '100000000'
            name: spark-5
            template: spark
        name: d
      - inputs:
          parameters:
          - name: num_data
        name: spark
        script:
          command:
          - python
          image: jupyter/pyspark-notebook:latest
          resources:
            requests:
              cpu: '4'
              memory: 8Gi
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: num_data = json.loads(r'''{{inputs.parameters.num_data}}''')
            except: num_data = r'''{{inputs.parameters.num_data}}'''

            import random
            import subprocess
            import time
            subprocess.run(['pip', 'install', 'pyspark', 'pandas'], stdout=subprocess.PIPE, universal_newlines=True)
            import pandas as pd
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.master('local[1]').appName('my-spark-example-running-in-hera.com').getOrCreate()
            (data, columns) = ([random.randint(0, num_data) for _ in range(num_data)], ['value'])
            pandas_df = pd.DataFrame(data=data, columns=columns)
            start = time.time()
            pandas_result = pandas_df.describe()
            pandas_elapsed = time.time() - start
            print('Pandas dataframe: ')
            print(pandas_result)
            print('Pandas dataframe took {pandas_elapsed} seconds to compute'.format(pandas_elapsed=pandas_elapsed))
            spark_df = spark.createDataFrame(data=pandas_df, schema=columns)
            start = time.time()
            spark_result = spark_df.describe()
            spark_elapsed = time.time() - start
            print('Spark dataframe: ')
            print(spark_result)
            print('Spark dataframe took {spark_elapsed} seconds to compute'.format(spark_elapsed=spark_elapsed))
    ```

