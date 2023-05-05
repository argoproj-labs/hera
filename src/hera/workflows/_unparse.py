import ast

import astunparse  # type: ignore


def roundtrip(source):
    tree = ast.parse(source)
    if hasattr(ast, "unparse"):
        return ast.unparse(tree)
    return astunparse.unparse(tree)
