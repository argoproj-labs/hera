"""This example showcases how to run PySpark within Hera / Argo Workflows!

This is not a comprehensive example that showcases how to spin up a Spark cluster, but rather a simple example that
compares a regular Pandas dataframe with a Spark dataframe. Inspired by: https://sparkbyexamples.com/pyspark-tutorial/
"""
from hera.workflows import DAG, Resources, Workflow, script


@script(image="jupyter/pyspark-notebook:latest", resources=Resources(cpu_request=4, memory_request="8Gi"))
def spark(n: int) -> None:
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
    data, columns = [random.randint(0, n) for _ in range(n)], ["value"]

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
        for i, n in enumerate([1_000, 10_000, 100_000, 1_000_000, 10_000_000, 100_000_000]):
            spark(name="spark-{i}".format(i=i), arguments={"n": n})
