# Loops

When writing Workflows, you may want to reuse a single template over a set of inputs. Argo exposes two mechanisms for
this looping, which are "with items" and "with param". These mechanisms function in exactly the same way, but as the
name suggests, "with param" lets you use a parameter to loop over, while "with items" is generally for a hard-coded list
of items. When using loops in Argo, the template will run in parallel for all the items; the items will be launched
sequentially but the running times may overlap. If you do not want to loop over the items in parallel, you should use a
[Synchronization](https://argoproj.github.io/argo-workflows/synchronization/) mechanism.

## Loops in Hera

In pure Argo YAML specification, `withItems` and `withParam` are single values or JSON objects. In Hera, we can pass any
`Parameter` or serializable object, plus, `with_items` and `with_params` work exactly the same for hard-coded values.

## A Simple `with_items` Example

Consider the [Hello World](hello-world.md) example:

```py
@script()
def echo(message: str):
    print(message)


with Workflow(
    generate_name="hello-world-",
    entrypoint="steps",
) as w:
    with Steps(name="steps"):
        echo(arguments={"message": "Hello world!"})
```

We can easily convert this to call `echo` for multiple strings; the only changes we need to make are in the function
call. First, specify the list of items you want to echo in the `with_items` kwarg:

```py
        echo(
            arguments={"message": "Hello world!"},
            with_items=["Hello world!", "I'm looping!", "Goodbye world!"],
        )
```

Now, we need to replace the value of the `message` argument. In Argo, you would use the `"{{item}}"` expression syntax,
which is also what we use in Hera:

```py
        echo(
            arguments={"message": "{{item}}"},
            with_items=["Hello world!", "I'm looping!", "Goodbye world!"],
        )
```

When running this Workflow, each value of `with_items` is passed to the `{{item}}` expression and runs in an independent
instance of the `echo` script container. Your Workflow logs should look something like:

```console
hello-world-9cf9j-echo-3186990983: Hello world!
hello-world-9cf9j-echo-4182774221: I'm looping!
hello-world-9cf9j-echo-1812072106: Goodbye world!
```

## `with_items` Using a Dictionary

We mentioned we can use any serializable object, so let's see how dictionaries are handled.

The `{{item}}` syntax represents the whole "item" passed in to the argument, so in the "hello world" example above, that
translates to just a string. For dictionaries, this `{{item}}` would translate to the whole dictionary. If instead we
want to pass values from the item dictionary to the function arguments, we provide them with Argo's key access syntax:
`{{item.key}}`.

Let's create a workflow to process everyone's favorite bubble tea orders!

First, a function that takes the customer's name, the drink flavor, ice level and sugar level:

```py
@script()
def make_bubble_tea(
    name: str,
    flavor: str,
    ice_level: float,
    sugar_level: float,
):
    print(
        f"Making {name}'s {flavor} bubble tea with {ice_level:.0%} ice and {sugar_level:.0%} sugar."
    )

```

Now, a Workflow with a `Steps` context:

```py
with Workflow(
    generate_name="make-drinks-",
    entrypoint="steps",
) as w:
    with Steps(name="steps"):
        make_bubble_tea(...)
```

And now for each argument of `make_bubble_tea`, we use the key access syntax for each value:

```py
with Workflow(
    generate_name="make-drinks-",
    entrypoint="steps",
) as w:
    with Steps(name="steps"):
        make_bubble_tea(
            arguments={
                "name": "{{item.name}}",
                "flavor": "{{item.flavor}}",
                "ice_level": "{{item.ice_level}}",
                "sugar_level": "{{item.sugar_level}}",
            },
            ...
        )
```

Now we need the actual values! For `with_item`, we will pass a list of dictionaries, with the keys "name", "flavor",
"ice_level" and "sugar_level":

```py
with Workflow(
    generate_name="make-drinks-",
    entrypoint="steps",
) as w:
    with Steps(name="steps"):
        make_bubble_tea(
            arguments={
                "name": "{{item.name}}",
                "flavor": "{{item.flavor}}",
                "ice_level": "{{item.ice_level}}",
                "sugar_level": "{{item.sugar_level}}",
            },
            with_items=[
                {
                    "name": "Elliot",
                    "flavor": "Taro Milk Tea",
                    "ice_level": 0.25,
                    "sugar_level": 0.75,
                },
                {
                    "name": "Flaviu",
                    "flavor": "Brown Sugar Milk Tea",
                    "ice_level": 1.00,
                    "sugar_level": 0.5,
                },
                {
                    "name": "Sambhav",
                    "flavor": "Green Tea",
                    "ice_level": 0.5,
                    "sugar_level": 0.25,
                },
            ],
        )
```

Running this Workflow, in the UI we'll see a fanout of three nodes, and the logs for "All" containers will show:

```console
make-drinks-h2qgq-make-bubble-tea-3759662853: Making Elliot's Taro Milk Tea bubble tea with 25% ice and 75% sugar.
make-drinks-h2qgq-make-bubble-tea-470512305: Making Sambhav's Green Tea bubble tea with 50% ice and 25% sugar.
make-drinks-h2qgq-make-bubble-tea-615962639: Making Flaviu's Brown Sugar Milk Tea bubble tea with 100% ice and 50% sugar.
```

### `with_param`
