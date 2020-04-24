from pathlib import Path

from .utils import SafeDict, benchmark
from .exceptions import PreqlError, pql_TypeError, pql_ValueError

from .evaluate import State, execute, evaluate, localize, eval_func_call
from .parser import parse_stmts, parse_expr
from . import pql_ast as ast
from . import pql_objects as objects
from . import pql_types as types
from .interp_common import new_value_instance

from .pql_functions import internal_funcs, joins


def initial_namespace():
    ns = SafeDict({p.name: p for p in types.Primitive.by_pytype.values()})
    ns.update(internal_funcs)
    ns.update(joins)
    ns['list'] = types.ListType(types.any_t)
    ns['aggregate'] = types.Aggregated(types.any_t)
    ns['TypeError'] = pql_TypeError
    ns['ValueError'] = pql_ValueError
    return [dict(ns)]

class Interpreter:
    def __init__(self, sqlengine):
        self.sqlengine = sqlengine
        self.state = State(sqlengine, 'text', initial_namespace())
        self.include('core.pql', __file__) # TODO use an import mechanism instead

    def call_func(self, fname, args):
        with benchmark.measure('call_func'):
            return eval_func_call(self.state, self.state.get_var(fname), args, None)

    def eval_expr(self, code, args):
        expr_ast = parse_expr(code)
        with self.state.use_scope(args):
            obj = evaluate(self.state, expr_ast)
        return obj

    def execute_code(self, code, args=None):
        assert not args, "Not implemented yet: %s" % args
        last = None
        for stmt in parse_stmts(code):
            last = execute(self.state, stmt)
        return last

    def include(self, fn, rel_to=None):
        if rel_to:
            fn = Path(rel_to).parent / fn
        with open(fn, encoding='utf8') as f:
            self.execute_code(f.read())

    def set_var(self, name, value):
        if not isinstance(value, types.PqlObject):
            try:
                value = value._to_pql()
            except AttributeError:
                value = new_value_instance(value)

        self.state.set_var(name, value)