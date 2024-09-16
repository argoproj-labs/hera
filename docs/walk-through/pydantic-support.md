# Integrated Pydantic Support

## The why and what

As Argo deals with YAML objects, which are actually a subset of JSON, Pydantic support is practically built-in to Hera
through Pydantic's serialization (to/from JSON) features. Using Pydantic objects (instead of dictionaries) in Script
templates makes them less error-prone, and easier to write! Using Pydantic classes yourself is as simple as inheriting
from Pydantic's `BaseModel`. [Read more about Pydantic models here](https://docs.pydantic.dev/latest/usage/models/).

## In Hera

Hera offers some features that explicitly rely on Pydantic. This includes the Hera Runner, which uses Pydantic to
validate the function call. Using Pydantic classes in your function parameters unlocks the powerful serializing and
de-serializing features of Pydantic when running on Argo. Your functions can return objects that are serialized, passed
to another `Step` as a string argument, and then de-serialized in another function. This flow can be seen in
[the callable scripts example](../examples/workflows/scripts/callable_script.md).

The Script Runner IO experimental feature provides a way to specify template inputs and outputs using the class fields
of the special `Input` and `Output` classes in Hera. Read more in the
[Script Runner IO guide](../user-guides/script-runner-io.md).
