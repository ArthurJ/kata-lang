from toolbox import Bidict, LangException, Node
from pprint import pprint  # noqa: F401
import pdb  # noqa: F401


value_types = {
    "FLOAT": {"converter": float, "type_name": "Float"},
    "INT": {"converter": int, "type_name": "Int"},
    "BIN": {"converter": lambda x: int(x, base=2), "type_name": "Int"},
    "HEX": {"converter": lambda x: int(x, base=16), "type_name": "Int"},
    "STR": {"converter": lambda x: x, "type_name": "Str"},
}

interface_relations = Bidict(
    {"Float": "NUM", "Int": "NUM", "BIN": "NUM", "HEX": "NUM"}
)  # noqa: E501
interface_lambdas = {"NUM": ["+", "-", "*", "/"]}  # TODO Usar isso(?)

# symbols
lambdas = {
    "+": {
        ("NUM", "NUM"): (lambda x, y: x + y, "NUM"),
        ("Str", "Str"): (lambda x, y: x + y, "Str"),
    },
    "-": {("NUM", "NUM"): (lambda x, y: x - y, "NUM")},
    "*": {("NUM", "NUM"): (lambda x, y: x * y, "NUM")},
    "/": {("NUM", "NUM"): (lambda x, y: x / y, "NUM")},
}

ident = {"pi": Node(value=3.1415, type_name="Float", node_type="VALUE")}


def interpret(stack):
    # pprint(stack)
    # breakpoint()
    if not stack:
        return ""
    if isinstance(stack, Node):
        return stack
    if isinstance(stack, list):
        if len(stack) == 1:
            return interpret(stack[0])
        if len(stack) == 2:
            if stack[0].node_type == "LAMBDA" and isinstance(stack[1], list):
                return execute_lambda(stack[0], interpret(stack[1]))
        if stack[0].node_type == "LET":
            return do_bind(stack)
        return [interpret(s) for s in stack]
    raise LangException("Interpreter ERROR")


def execute_lambda(node, args):
    # pprint(args)
    # breakpoint()
    symbol = node.value
    arg_qty = len(list(lambdas[symbol].items())[0])
    arg_types = [arg.type_name for arg in args[:arg_qty] if arg]
    chosen_lambda, return_type = match_types(lambdas[symbol], arg_types)
    arg_values = [arg.value for arg in args[:arg_qty]]
    ret_val = Node(
        value=chosen_lambda(*arg_values),
        type_name=return_type,  # noqa: E501
        node_type="VALUE",
    )
    if len(args) > arg_qty:
        ret_list = [ret_val]
        ret_list.extend(args[arg_qty:])
        return ret_list
    return ret_val


def do_bind(stack):
    # breakpoint()
    stack.pop(0)
    val_name = stack.pop(0).value
    if not isinstance(stack[0], list) and stack[0].node_type == "TYPED_SEP":
        # TODO tipos explicitados devem ser tratados
        stack.pop(0)
        stack.pop(0)
    value = interpret(stack)
    ident[val_name] = value
    return ""


def match_types(lambda_map, arg_types):
    possible_types = lambda_map.keys()
    for best_match in possible_types:
        all_matches = True
        for t1, t2 in zip(best_match, arg_types):
            all_matches = all_matches and type_match(t1, t2)
        if all_matches:
            return lambda_map[best_match]
    else:
        raise LangException("No lambda defined for these argument types")


def type_match(t1, t2):
    # breakpoint()
    match = False
    match = match or t1 == t2
    match = match or (
        t1 in interface_relations.inverse
        and t1 == interface_relations.get(t2)  # noqa: E501
    )
    match = match or (
        t2 in interface_relations.inverse
        and t2 == interface_relations.get(t2)  # noqa: E501
    )
    return match
