"""This example showcases how one can run a sidecar container with Hera"""

from hera import Sidecar, Task, Workflow

# this assumes you have set a global token and a global host
with Workflow("sidecar-", generate_name=True) as w:
    Task(
        "sidecar-example",
        image="alpine:latest",
        command=["sh", "-c"],
        args=[
            "apk update && apk add curl && until curl -XPOST 'http://127.0.0.1:8086/query' --data-urlencode 'q=CREATE DATABASE mydb' ; do sleep .5; done && for i in $(seq 1 20); do curl -XPOST 'http://127.0.0.1:8086/write?db=mydb' -d \"cpu,host=server01,region=uswest load=$i\" ; sleep .5 ; done"
        ],
        sidecars=[Sidecar("influxdb", image="influxdb:1.2", command=["influxd"])],
    )

w.create()
