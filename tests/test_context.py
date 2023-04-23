import asyncio

from hera.workflows import Steps, Workflow, script


@script(image="python:3.9")
def echo(message: str):
    print(message)


@script(image="python:3.10")
def hello(name: str):
    print(f"Hello {name}")


async def abuild_workflow_wait(event):
    with Workflow(
        generate_name="waiter-",
        entrypoint="steps",
    ) as w:
        with Steps(name="steps"):
            echo(arguments={"message": "hello 0"})
            await event.wait()
    return w


async def abuild_workflow_set(event):
    with Workflow(
        generate_name="setter-",
        entrypoint="steps",
    ) as w:
        with Steps(name="steps"):
            hello(arguments={"name": "world"})

    event.set()
    return w


def test_async_context():
    """
    In this test, we create 2 workflows using async functions and make sure the context isn't leaking.

    In the middle of the first one, we pause by waiting thus never calling the context exit() function;
    meanwhile the 2nd function will create another workflow, then unblock the first one which will resume.
    Both workflows have to be complete and not be entangled: they were created in 2 isolated flows.
    """

    async def main():
        event = asyncio.Event()
        t0 = asyncio.create_task(abuild_workflow_wait(event))
        t1 = asyncio.create_task(abuild_workflow_set(event))
        rv0 = await t0
        rv1 = await t1

        return rv0, rv1

    rv = asyncio.run(main())

    assert len(rv) == 2
    w0, w1 = rv

    assert [x.name for x in w0.templates] == ["steps", "echo"]
    assert w0.templates[1].image == "python:3.9"
    assert [x.name for x in w1.templates] == ["steps", "hello"]
    assert w1.templates[1].image == "python:3.10"


def test_sync_context():
    """
    Context is not leaking between 2 successive sync workflow creations
    """
    with Workflow(
        generate_name="w0-",
        entrypoint="steps",
    ) as w0:
        with Steps(name="steps"):
            echo(arguments={"message": "hello 0"})

    with Workflow(
        generate_name="w1-",
        entrypoint="steps",
    ) as w1:
        with Steps(name="steps"):
            hello(arguments={"message": "hello 1"})

    assert [x.name for x in w0.templates] == ["steps", "echo"]
    assert w0.templates[1].image == "python:3.9"
    assert [x.name for x in w1.templates] == ["steps", "hello"]
    assert w1.templates[1].image == "python:3.10"
