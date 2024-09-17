# Daemon



Enablement of https://argoproj.github.io/argo-workflows/variables/
This example creates two tasks, one of the Tasks is a deamond task and its IP address is shared with the second task
The daemoned task operates as server, serving an example payload, with the second task operating as a client, making
http requests to the server.


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, script


    @script(daemon=True)
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
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: daemon-
    spec:
      entrypoint: d
      templates:
      - dag:
          tasks:
          - name: server
            template: server
          - arguments:
              parameters:
              - name: ip
                value: '{{tasks.server.ip}}'
            depends: server
            name: consumer
            template: consumer
        name: d
      - daemon: true
        name: server
        script:
          command:
          - python
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            from http.server import BaseHTTPRequestHandler, HTTPServer

            class MyServer(BaseHTTPRequestHandler):

                def do_GET(self):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(bytes("{'name':'John'}", 'utf-8'))
            webServer = HTTPServer(('0.0.0.0', 8080), MyServer)
            webServer.serve_forever()
      - inputs:
          parameters:
          - name: ip
        name: consumer
        script:
          command:
          - python
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: ip = json.loads(r'''{{inputs.parameters.ip}}''')
            except: ip = r'''{{inputs.parameters.ip}}'''

            import http.client
            import os
            print(os.environ)
            server_ip = ip.replace('"', '')
            connection = http.client.HTTPConnection('{server_ip}:8080'.format(server_ip=server_ip))
            connection.request('GET', '/')
            response = connection.getresponse()
            print(response.read())
    ```

