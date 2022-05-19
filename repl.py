from time import process_time
from functools import wraps

from tokenizer import tokenize
from patterns import patterns
from interpreter import interpret
from interpreter import value_types, lambdas, ident, interface_relations
from stacker import create_stack, nodefy

from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.lisp import CommonLispLexer as LispLexer

from rich.console import Console
from rich.traceback import install

from toolbox import LangException, Scope


def timer(msg="Exec time: {0:.7f}s"):
    def decorador(method):
        @wraps(method)
        def wrapper(*args, **kw):
            ts = process_time()
            result = method(*args, **kw)
            te = process_time()
            delta = te - ts
            print(msg.format(delta))
            return result

        return wrapper

    return decorador


def prompt():
    session = PromptSession()
    print_fun = Console().print
    scope = Scope(value_types, ident, interface_relations, lambdas)
    while True:
        try:
            line = session.prompt("-> ", lexer=PygmentsLexer(LispLexer))
        except EOFError:
            break
        if line:
            run_line([line], scope, print_fun)


@timer()
def run_line(line, scope, print_fun=None):
    res = ""
    if not print_fun:
        print_fun = print
    try:
        # breakpoint()
        node_list = nodefy(tokenize(line, patterns)[0], lambdas, ident)
        stack = create_stack(node_list, [], scope)
        # print_fun(stack,'-'*80)
        res = interpret(stack)
        print_fun(res, "\n")
    except LangException as e:
        print_fun(f"{e}")
    return res


if __name__ == "__main__":
    install()
    prompt()
