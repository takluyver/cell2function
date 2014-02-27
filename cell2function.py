# -*- coding: utf-8 -*-

import ast
import sys
PY3 = sys.version_info[0] >= 3

try:
    import builtins  # Python 3
except ImportError:
    import __builtin__ as builtins  # Python 2

class NameScanner(ast.NodeVisitor):
    """Check an AST for names defined in it, and names read before they are defined."""
    def __init__(self):
        super(NameScanner, self).__init__()
        self.read_before_defined = []
        self.defined_in_scopes = [list(builtins.__dict__), []]
    
    def visible(self, name):
        return any(name in defined for defined in self.defined_in_scopes)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.defined_in_scopes[-1].append(node.id)
        elif isinstance(node.ctx, ast.Load) and not self.visible(node.id):
            self.read_before_defined.append(node.id)
    
    def visit_Assign(self, node):
        """Reimplemented to ensure that we visit value before targets.
        So 'a = a + 1' counts as reading then writing a."""
        self.visit(node.value)
        for target in node.targets:
            self.visit(target)
    
    def visit_AugAssign(self, node):
        """Treat 'a += 1' as both reading and writing a."""
        if isinstance(node.target, ast.Name):
            if not self.visible(node.target.id):
                self.read_before_defined.append(node.target.id)
            self.defined_in_scopes[-1].append(node.target.id)
            self.visit(node.value)
        else:
            # Augmented assignment on attribute/subscript/slice
            self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        pn = ParameterNames()
        pn.visit(node.args)
        self.defined_in_scopes.append(pn.paramnames)
        self.generic_visit(node)
        self.defined_in_scopes.pop()
        self.defined_in_scopes[-1].append(node.name)
        # XXX: For now, assume functions aren't declaring any global/nonlocal
        # variables

class ParameterNames(ast.NodeVisitor):
    def __init__(self):
        super(ParameterNames, self).__init__()
        self.paramnames = []
    
    # Parameters are stored differently in Python 2 and 3
    if PY3:
        def visit_arg(self, node):
            self.paramnames.append(node.arg)
    else:
        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Param):
                self.paramnames.append(node.id)

def makefunction(name, cell):
    namescanner = NameScanner()
    namescanner.visit(ast.parse(cell))
    out = ["def {name}({args}):".format(name=name,
           args=", ".join(namescanner.read_before_defined))]
    out.extend("    " + l for l in cell.splitlines())
    out.append("    return " + ", ".join(namescanner.defined_in_scopes[1]))
    return "\n".join(out)

def load_ipython_extension(ip):
    def cell2function(line, cell):
        func_name = line.strip().split()[0] if line.strip() else 'unnamed'
        ip.set_next_input(makefunction(func_name, cell))
    
    ip.register_magic_function(cell2function, magic_kind='cell')