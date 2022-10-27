# Daemon

Enablement of https://argoproj.github.io/argo-workflows/variables/. This example creates two tasks, one of the
Tasks is a deamond task and its IP address is shared with the second task. The daemoned task operates as server,
serving an example payload, with the second task operating as a client, making HTTP requests to the server

```python
from hera import Env, Task, Workflow


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

    print(os.environ)
    server_ip = os.environ["SERVER_IP"].replace('"', "")
    connection = http.client.HTTPConnection(f"{server_ip}:8080")
    connection.request("GET", "/")
    response = connection.getresponse()
    print(response.read())


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow("variables") as w:
    d = Task("daemon", server, daemon=True)
    t = Task("consumer", consumer, env=[Env(name="SERVER_IP", value_from_input=d.ip)])
    d >> t

w.create()
```