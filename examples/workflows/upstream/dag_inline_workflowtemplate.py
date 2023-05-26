from hera.shared import global_config
from hera.workflows import DAG, Container, Task, WorkflowTemplate

global_config.host = "https://argo.dynet.ai"
global_config.namespace = "default"
global_config.token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjJkOWE1ZWY1YjEyNjIzYzkxNjcxYTcwOTNjYjMyMzMzM2NkMDdkMDkiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiI5MTczODc2NzY5MjctcG00djh1OXYxYXNmc2VpanVmdXM2N2hwaXBvOXZoa3QuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhenAiOiIxMDQyNjQ1NDY0NTY2Njk1Njk1MTIiLCJlbWFpbCI6ImR5bmV0LWlhcC11c2VyQGR5bmV0LTMwODUwMC5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJleHAiOjE2ODUwNzMyOTIsImlhdCI6MTY4NTA2OTY5MiwiaXNzIjoiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tIiwic3ViIjoiMTA0MjY0NTQ2NDU2NjY5NTY5NTEyIn0.i5jRUFiVMUXz1_2Oq4kzkmPhaZWbJ4lGoF-VG98lOTL2fRe6YhmW_1G7g1lwYcbrqbhEzgUStmX6ILDGJHaJu8sK3oRsftJ6cAmzMH6YUWRNXWvG707Z_Lr2cMJMBzYIzj2zQwg1ApFDu4WAUIp5fK4F09KiOS5rK_QKY5ZGBvMmpV6r8XUu06guwj1qTJS_4TaxnCU3CNoj5emu1RMN_Rk8oYIrFxxPRqi1WoxpTk9HEqAMXlTWxwG5NhlM8zGF6WBXoZJDphgxJfKTfVy9UlzmEaYD2e7yuz360hMthTJBFapOokLLRtiuXLdpgyfD1vD_3KFptjcZw9tF_xvZiQ"

container = Container(image="argoproj/argosay:v2")

with WorkflowTemplate(
    name="dag-inline",
    entrypoint="main",
    annotations={
        "workflows.argoproj.io/description": ("This example demonstrates running a DAG with inline templates."),
        "workflows.argoproj.io/version": ">= 3.2.0",
    },
) as w:
    with DAG(name="main"):
        Task(name="a", inline=container)
