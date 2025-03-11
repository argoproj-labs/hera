<div style="display: flex; align-items: center; gap: 20px;">
  <h1 style="margin: 0;">
  <span style="font-size: 1.5em;">Python Orchestration</span><br>
  <span style="font-size: 0.6em;"><em>Powered by Argo Workflows</em></span>
  </h1>
  <img src="https://raw.githubusercontent.com/argoproj-labs/hera/main/docs/assets/hera-logo.svg" width="20%" alt="Hera mascot" style="margin-left: auto;">
</div>

### What is Hera?

Hera is the go-to Python SDK to make Argo Workflows simple and intuitive. Easily turn Python functions into
containerised templates that run on Kubernetes, with full access to its capabilities.

### Why Hera?

✅ **Python-First** – Write native Python (with all your favourite libraries!)  
✅ **Lightweight & Unintrusive** – Keep orchestration logic out of your functions  
✅ **Built on Argo Workflows** – All the power of Kubernetes, with the simplicity of Python  

### The Basics

Install with your favourite package manager:

```
pip install hera
```

Use the `@script` decorator on your functions, and arrange them in a `DAG`. Create a `DAG` in a `Workflow` to submit it
to Argo!

```python
from hera.workflows import DAG, Workflow, script


@script()
def echo(message: str):
    print(message)


with Workflow(
    generate_name="dag-diamond-",
    entrypoint="diamond",
) as w:
    with DAG(name="diamond"):
        A = echo(name="A", arguments={"message": "A"})
        B = echo(name="B", arguments={"message": "B"})
        C = echo(name="C", arguments={"message": "C"})
        D = echo(name="D", arguments={"message": "D"})
        A >> [B, C] >> D  # Define execution order

w.create()
```

Check out the [Quick Start](walk-through/quick-start.md) for more!

## Community Presentations

<!-- Add 3 most recent talks here -->

- [KubeCon/ArgoCon NA 2024 - Data Science Workflows Made Easy: Python-Powered Argo for Your Organization](https://www.youtube.com/watch?v=hZOcj5uVQOo&list=PLj6h78yzYM2Ow7Jy0paxwrimeuFGONU_7&index=14)
- [KubeCon/ArgoCon EU 2024 - Orchestrating Python Functions Natively in Argo Using Hera](https://www.youtube.com/watch?v=4G3Q6VMBvfI&list=PLj6h78yzYM2NA4NbSC6_mQNza2r3WV87h&index=4)
- [CNCF TAG App-Delivery @ KubeCon NA 2023 - Automating the Deployment of Data Workloads to Kubernetes with ArgoCD, Argo Workflows, and Hera](https://www.youtube.com/watch?v=NZCmYRVziGY&t=12481s&ab_channel=CNCFTAGAppDelivery)

<details><summary><i>More presentations</i></summary>

<ul>
  <li>
    <a href="https://www.youtube.com/watch?v=nRYf3GkKpss&ab_channel=CNCF%5BCloudNativeComputingFoundation%5D">
      KubeCon/ArgoCon NA 2023 - How to Train an LLM with Argo Workflows and Hera
    </a>
    <ul>
      <li>
        <a href="https://github.com/flaviuvadan/kubecon_na_23_llama2_finetune">
          Featured code
        </a>
      </li>
    </ul>
  </li>
  <li>
    <a href="https://www.youtube.com/watch?v=h2TEw8kd1Ds">
      KubeCon/ArgoCon EU 2023 - Scaling gene therapy with Argo Workflows and Hera
    </a>
  </li>
  <li>
    <a href="https://youtu.be/sSLFVIIEKcE?t=2088">
      DoKC Town Hall #2 - Unsticking ourselves from Glue - Migrating PayIt's Data Pipelines to Argo Workflows and Hera
    </a>
  </li>
  <li>
    <a href="https://youtu.be/sdkBDPOdQ-g?t=231">
      Argo Workflows and Events Community Meeting 15 June 2022 - Hera project update
    </a>
  </li>
  <li>
    <a href="https://youtu.be/QETfzfVV-GY?t=181">
      Argo Workflows and Events Community Meeting 20 Oct 2021 - Hera introductory presentation
    </a>
  </li>
</ul>


</details>

## Community Blogs

<!-- Add 3 most recent blogs here -->
<!-- Currently 4 blogs - add collapsable section when next blog is added, and remove this comment -->

- [How To Get the Most out of Hera for Data Science](https://pipekit.io/blog/how-to-get-the-most-out-of-hera-for-data-science)
- [Data Validation with Great Expectations and Argo Workflows](https://towardsdatascience.com/data-validation-with-great-expectations-and-argo-workflows-b8e3e2da2fcc)
- [Hera introduction and motivation](https://www.dynotx.com/hera-the-missing-argo-workflows-python-sdk/)
- [Dyno is scaling gene therapy research with cloud-native tools like Argo Workflows and Hera](https://www.dynotx.com/argo-workflows-hera/)


## License

Hera is licensed under Apache 2.0. See [License](https://github.com/argoproj-labs/hera/blob/main/LICENSE) for details.
