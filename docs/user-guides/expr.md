# Hera Python -> expr transpiler

[**Expr**](https://github.com/antonmedv/expr/blob/master/docs/Language-Definition.md) is an expression evaluation language used by [**Argo**](https://argoproj.github.io/argo-workflows/variables/#expression).

Hera provides an easy way to construct `expr` expressions in `Python`. It supports the full language definition of `expr` including the enhancements added by `Argo`.

## Usage

The recommended way of using the `hera.expr` module is to construct the expression in Python. Once your expressions is ready to be used,
you may call `str(<expression>)` to convert it to an appropriate `expr` expression. `hera` also supports formatting expressions such that they are surrounded by braces which is useful in Argo when substituting variables.. You can do this via Python string format literals and by adding `$` as a format string.

Example:

* `f"{g.input.parameters.value:$}" == "{{input.parameters.value}}"`: the `$` format string tells `hera` to insert the braces around the output as a simple variable.
* `f"{g.workflow.parameters.config.jsonpath('$.a'):=}" == "{{=jsonpath(workflow.parameters.config, '$.a')}}"`: the `=` format string tells `hera` to insert the braces around the output and insert and equals sign and output a complex expression.
* `f"{g.input.parameters.value}" == "input.parameters.value"`: without any extra format strings, the output is the transpiled `expr` expression.
* `str(g.input.parameters.value) == "input.parameters.value"`: calling `str` on a `hera.expr` expression also triggers the transpilation.


## Supported Literals

The transpiler supports constant literals via the class `C`:

* **strings** - single and double quotes (e.g. `"hello"`, `'hello'`) can be represented as `C("hello")`, `C('hello')`
* **numbers** - e.g. `103`, `2.5`, `.5` can be represented as `C(103)`, `C(2.5)`, `C(.5)`
* **arrays** - e.g. `[1, 2, 3]` can be represented as `C([1, 2, 3])`
* **maps** - e.g. `{foo: "bar"}` can be represented as `C({'foo': 'bar'})`
* **booleans** - `true` and `false` can be represented as `C(True)` and `C(False)`
* **nil** - `nil` can be represented as `C(None)`

> Note: `hera` is smart enough to transpile python constants used in conjunction with a literal directly to a literal.
> This helps with brevity. For eg: `C(1) + C(2)` is the same as writing `C(1) + 2`. This however only works if the left
> operand is a literal or an identifier. If in doubt, always define literals via `C(...)`

### Reference

| Python                             | expr transpilation             |
| ---------------------------------- | ------------------------------ |
| C(1)                               | 1                              |
| C(None)                            | nil                            |
| C(True)                            | true                           |
| C(False)                           | false                          |
| C([1, 2, 3])                       | [1, 2, 3]                      |
| C({"hello": False, "world": None}) | {"hello": false, "world": nil} |


## Identifiers/Variables

Global variables/identifiers can be accessed through attributes of the global context variable `g`:

* `g.var` transpiles to `var`

### Fields

Struct fields can be accessed by using the `.`  syntax.

* `g.var.attribute` transpiles to `var.attribute`

There maybe times that you want to get a struct field whose name conflicts with a `hera.expr` transpiler function. In this case you can use the `get` method.

* `g.get("var").get("attribute")` transpiles to `var.attribute`

### Map elements

Map elements can be accessed used the `[]` syntax.

* `g.var['element']` transpiles to `var['element']`

### Reference


| Python                                 | expr transpilation     |
| -------------------------------------- | ---------------------- |
| g.test[2]                              | test[2]                |
| g.test['as']                           | test['as']             |
| g.test.attr                            | test.attr              |
| g.get("test").get("attr").another_attr | test.attr.another_attr |

## Slices

* `array[:]` (slice)

Slices can work with arrays or strings. Python slices are transpiled appropriately to expr slices.

> Note: Only slices with step-size of 1 are supported.

Example:

Variable `array` is `[1,2,3,4,5]`.

```
g.array[1:5] == [2, 3, 4]
g.array[3:] == [4, 5]
g.array[:4] == [1, 2, 3]
g.array[:] == g.array
```

transpiles to

```
array[1:5] == [2,3,4]
array[3:] == [4,5]
array[:4] == [1,2,3]
array[:] == array
```


### Reference


| Python      | expr transpilation |
| ----------- | ------------------ |
| g.test[1:9] | test[1:9]          |
| g.test[1:]  | test[1:]           |
| g.test[:]   | test[:]            |
| g.test[:9]  | test[:9]           |
| g.test[0:9] | test[0:9]          |



## Operators

All the operators transpile appropriately and provide a native python look and feel.

### Arithmetic Operators

* `+` (addition)
* `-` (subtraction)
* `*` (multiplication)
* `/` (division)
* `%` (modulus)
* `**` (pow)

Example:

* `g.x ** 2 + g.y` transpiles to `x**2 + y`

### Comparison Operators

* `==` (equal)
* `!=` (not equal)
* `<` (less than)
* `>` (greater than)
* `<=` (less than or equal to)
* `>=` (greater than or equal to)

Example:

* `g.x >= C(1)` transpiles to `x >= 1`

### Logical Operators

* `not` or `!`
* `and` or `&&`
* `or` or `||`

Example:

* `~g.y` transpiles to `!y`
* `g.y & g.x` transpiles to `y && x`
* `g.y | g.x` transpiles to `y || x`

### String Operators

* `+` (concatenation)
* `matches` (regex match)
* `contains` (string contains)
* `starts_with` (has prefix)
* `ends_with` (has suffix)

Example:

* `C("test") + C("test2")` transpiles to `'test' + 'test2'`
* `C("test").matches(".*")` transpiles to `'test' matches '.*'`
* `g.var.contains("substring")` transpiles to `var contains 'substring'`
* `g.var.starts_with("substring")` transpiles to `var startsWith 'substring'`
* `g.var.ends_with("substring")` transpiles to `var endsWith 'substring'`


### Membership Operators

* `in` (contain)
* `not in` (does not contain)

Example:

* `g.user.Group.in([["human_resources", "marketing"]])` transpiles to `user.Group in ["human_resources", "marketing"]`
* `C("baz").not_in({"foo": 1, "bar": 2})` transpiles to `'baz' in {'foo': 1, 'bar': 2}`


### Numeric Operators

* `1..9` (range) can be represented as `C(range(1, 10))`

> Note: `range` in `expr` is inclusive i.e. `C(range(1, 3)) == C([1, 2]) == 1..2`

### Ternary Operators

* `foo ? 'yes' : 'no'` can be represented as `g.foo.check('yes', 'no')`

### Parantheses

In case users want to add parantheses around an expression, you can use the class `P`:

`P(C(1) * 4) / 2` transpiles to `(1 * 4) / 2`

### Reference

| Python                           | expr transpilation   |
| -------------------------------- | -------------------- |
| g.x**2 + g.y                     | x ** 2 + y           |
| C(1) + C(2) * C(3) / C(4)        | 1 + 2 * 3 / 4        |
| C(1) >= C(2)                     | 1 >= 2               |
| C(range(1, 10))                  | 1..9                 |
| -g.y                             | -y                   |
| +g.y                             | +y                   |
| ~g.y                             | !y                   |
| C(False) & C(True)               | true && false        |
| C(False) \| C(True)              | true \|\| false      |
| C(1).not_in([1, 2, 3])           | 1 not in [1, 2, 3]   |
| C(1).in_([1, 2, 3])              | 1 in [1, 2, 3]       |
| C("has") + "as"                  | 'has' + 'as'         |
| C("has").contains("as")          | 'has' contains 'as'  |
| C("has").matches(".*")           | 'has' matches '.*'   |
| C("has").starts_with("h")        | 'has' startsWith 'h' |
| C("has").ends_with("s")          | 'has' endsWith 's'   |
| C(range(1, 10))                  | 1..10                |
| g.test.check(g.test1, g.test2)   | test ? test1 : test2 |
| P(C(1) >= C(2)) & P(C(2) < C(3)) | (1 >= 2) and (2 < 3) |



## Builtin functions

* `len(foo)` (length of array, map or string) can be represented as `g.foo.length()`
* `asInt('1')` (convert the string to integer) can be represented as `C("1").as_int()`
* `asFloat('1.2')` (convert the string to integer) can be represented as `C("1.2").as_float()`
* `asFloat('1.2')` (convert the string to integer) can be represented as `C("1.2").as_float()`
* `toJson([1, 2])` (convert to a JSON string) can be represented as `C([1, 2]).to_json()`
* `jsonpath(test, 'test')` (extract the element from JSON using JSON Path) can be represented as `g.test.jsonpath("test")`

> Note: `jsonpath(path)` the `path` variable in the `jsonpath` method may either be a string or a
> [programmatic JSONPath expression](https://github.com/h2non/jsonpath-ng#programmatic-jsonpath) built using the
> `jsonpath-ng` library.


There are also some functional programming related functions which accept a list of items and a predicate. The iterable inside the predicate can be accessed via a special variable `it`. The following functions are supported

* `all` (will return `true` if all element satisfies the predicate)
* `none` (will return `true` if all element does NOT satisfy the predicate)
* `any` (will return `true` if any element satisfies the predicate)
* `one` (will return `true` if exactly ONE element satisfies the predicate)
* `filter` (filter array by the predicate)
* `map` (map all items with the closure)
* `count` (returns number of elements what satisfies the predicate)


### Closures

The closure is an expression that accepts a single argument. To access
the argument use the `it` variable.

Examples:

```
C(range(0, 9)).map(it / 2)
```

transpiles to

```
map(0..9, {# / 2})
```

Examples:

Ensure all tweets are less than 280 chars.

```python
g.Tweets.all(it.Size < 280)
```

transpiles to

```
all(Tweets, {#.Size < 280})
```

Ensure there is exactly one winner.

```python
g.Participants.one(it.Winner)
```

transpiles to

```
one(Participants, {#.Winner})
```

> Note: `expr` allows you to omit `#` when accessing attributes in the predicate. In order to ensure consistency, `hera`
> always includes `#` in the output closure, even though it can be omitted.


### Reference

| Python                                                         | expr transpilation                        |
| -------------------------------------------------------------- | ----------------------------------------- |
| g.test.length()                                                | len(test)                                 |
| g.test.length() > 2                                            | len(test) > 2                             |
| g.test[g.test.length() - 1]                                    | test[len(test) - 1]                       |
| g.test.string()                                                | string(test)                              |
| g.test.to_json()                                               | toJson(test)                              |
| g.test.jsonpath("test").test.length()                          | len(jsonpath(test, 'test').test)          |
| g.test.jsonpath("test").test.as_float()                        | asFloat(jsonpath(test, 'test').test)      |
| g.test.jsonpath("test").test.as_int()                          | asInt(jsonpath(test, 'test').test)        |
| g.test.jsonpath(Fields("foo").child("test").child(Slice("*"))) | jsonpath(test, 'foo.test.[*]')            |
| g.test.map(it + 2)                                             | map(test, {# + 2})                        |
| g.test.map(it.Size + 2)                                        | map(test, {#.Size + 2})                   |
| g.test.filter(P(it["items"].length() + 1) > 0)                 | filter(test, {(len(#['items']) + 1) > 0}) |

## Sprig functions

Spring functions may be called using the `sprig.<function>(*args)` syntax. For a complete list of functions you may visit the [sprig function documentation](http://masterminds.github.io/sprig/)

* `sprig.trim(g.test)` transpiles to `sprig.trim(test)`

### Reference

| Python                        | expr transpilation      |
| ----------------------------- | ----------------------- |
| sprig.trim("c")               | sprig.trim('c')         |
| sprig.add(g.test.length(), 1) | sprig.add(len(test), 1) |
