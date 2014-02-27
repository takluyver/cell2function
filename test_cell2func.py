import ast
import sys
PY3 = sys.version_info[0] >= 3

import cell2function

cell1 = """
b=2
def subfunc(c=1, d=z):
    e = 99
    print(y)
    c * 2
a = a*2
x += 1
sum(d + [1])
"""

def test_makefunction():
    res = cell2function.makefunction('foobar', cell1)
    tree = ast.parse(res)
    assert len(tree.body) == 1
    assert isinstance(tree.body[0], ast.FunctionDef)
    funcdef = tree.body[0]
    if PY3:
        params = [a.arg for a in funcdef.args.args]
    else:
        params = [n.id for n in funcdef.args.args]
    assert params == ['z', 'y', 'a', 'x', 'd']
    assert isinstance(funcdef.body[-1], ast.Return)
    assert isinstance(funcdef.body[-1].value, ast.Tuple)
    retvals = [n.id for n in funcdef.body[-1].value.elts]
    assert retvals == ['b', 'subfunc', 'a', 'x']