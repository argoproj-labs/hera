"""Demonstrates usage of [daemon container IP](https://argoproj.github.io/argo-workflows/variables/).

This example creates two tasks, one of the Tasks is a daemon task and its IP address is shared with the second task. The
daemon task operates as server, serving an example payload, with the second task operating as a client, making http
requests to the server."""

from hera.workflows import DAG, Workflow, script
from hera.workflows.models import HTTPGetAction, Probe


@script(daemon=True, readiness_probe=Probe(http_get=HTTPGetAction(path="/", port=8080)))
def server():
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class MyServer(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes("{'name':'John'}", "utf-8"))

    webServer = HTTPServer(("0.0.0.0", 8080), MyServer)
    webServer.serve_forever()


@script()
def consumer(ip):
    import http.client
    import os

    print(os.environ)
    server_ip = ip.replace('"', "")
    connection = http.client.HTTPConnection("{server_ip}:8080".format(server_ip=server_ip))
    connection.request("GET", "/")
    response = connection.getresponse()
    print(response.read())


with Workflow(generate_name="daemon-", entrypoint="d") as w:
    with DAG(name="d"):
        s = server()
        c = consumer(arguments={"ip": s.ip})
        s >> c
