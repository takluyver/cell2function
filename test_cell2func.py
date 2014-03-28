import ast
import sys
PY3 = sys.version_info[0] >= 3

from astcheck import assert_ast_like, mkarg, listmiddle
import cell2function

cell1 = """
b=2
def subfunc(c=1, d=z):
    e = 99
    print(y)
    c * 2
a = a*2
a = a - 3
x * 2
x += 1
sum(d + [1])
sysmod.version  # modules shouldn't become parameters.
"""

template = ast.Module(body=[
    ast.FunctionDef(name="foobar", args=ast.arguments(args=[
                mkarg(name) for name in ['z', 'y', 'a', 'x', 'd']
    ]), body=listmiddle() + [
        ast.Return(value=ast.Tuple(elts=
            [ast.Name(id=n, ctx=ast.Load()) for n in ['b', 'subfunc', 'a', 'x']]
        ))
    ]),
    ast.Assign(targets=[ast.Tuple(ctx=ast.Store(), names=[
            ast.Name(id=id, ctx=ast.Store()) for id in ['b', 'subfunc', 'a', 'x']
            ])],
         value = ast.Call(func=ast.Name(id="foobar", ctx=ast.Load()),
                          args=[
              ast.Name(id=id, ctx=ast.Load()) for id in ['z', 'y', 'a', 'x', 'd']
            ])
        )
])

def test_makefunction():
    res = cell2function.makefunction('foobar', cell1, user_ns={'sysmod': sys})
    assert_ast_like(ast.parse(res), template)