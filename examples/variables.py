# Enablement of https://argoproj.github.io/argo-workflows/variables/
# This example creates two tasks, one of the Tasks is a deamond task and its IP address is shared with the second task
# The daemoned task operates as server, serving an example payload, with the second task operating as a client, making
# http requests to the server

from hera import Task, VariableAsEnv, Workflow, WorkflowService


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


def consumer():
    import http.client
    import os

    print(os.environ["SERVER_IP"])
    server_ip = os.environ["SERVER_IP"].replace('"', '')
    connection = http.client.HTTPConnection(f"{server_ip}:8080")
    connection.request("GET", "/")
    response = connection.getresponse()
    print(response.read())


namespace = "argo"
# TODO: replace the domain and token with your own
ws = WorkflowService(host='my-argo-server.com', token="token", namespace=namespace)
w = Workflow('variables', ws)
d = Task('daemon', server, daemon=True)
server_ip_variable = VariableAsEnv(name='SERVER_IP', value=d.ip)
t = Task('consumer', consumer, variables=[server_ip_variable])

d >> t

w.add_tasks(d, t)
w.create(namespace=namespace)
