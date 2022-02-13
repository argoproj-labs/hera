# Enablement of https://argoproj.github.io/argo-workflows/variables/
# This example creates two tasks, one of the Tasks is a deamond task and its IP address is shared with the second task
# The daemoned task operates as server, serving an example payload, with the second task operating as a client, making
# http requests to the server

from hera.task import Task
from hera.input import InputParameterAsEnv
from hera.workflow import Workflow
from hera.workflow_service import WorkflowService


def server():
    pass


def consumer(server_ip):
    print(server_ip)


# TODO: replace the domain and token with your own
ws = WorkflowService(host='my-argo-server.com', token='my-auth-token')


def server():
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class MyServer(BaseHTTPRequestHandler):
        def get_check(self):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes("{'name':'John'}", "utf-8"))

    webServer = HTTPServer(("0.0.0.0", 8080), MyServer)
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass


def consumer():
    import http.client
    import os

    print(os.environ["IP"])
    connection = http.client.HTTPConnection(f"{os.environ['IP']}:8080")
    connection.request("GET", "/")
    response = connection.getresponse()
    print(response.read())


namespace = "argo"
# TODO: replace the domain and token with your own
ws = WorkflowService(host='my-argo-server.com', token="token", namespace=namespace)
w = Workflow('variables', ws)
d = Task('daemon', server, daemon=True)
variables = InputParameterAsEnv(name='SERVER_IP', value="{{tasks.daemon.ip}}")
t = Task('consumer', consumer, variables=[variables])

d >> t

w.add_tasks(d, t)
w.submit(namespace=namespace)
