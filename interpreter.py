from typing import List
from toolbox import bidict, LangException
from tokenizer import Token
from pprint import pprint  # noqa: F401
import pdb  # noqa: F401

# TODO!
# diferenciar Token do tokenizador
# e token do interpretador

value_types = {
    "FLOAT": {"converter": float, "type_name": "Float"},
    "INT": {"converter": int, "type_name": "Int"},
    "BIN": {"converter": lambda x: int(x, base=2), "type_name": "Int"},
    "HEX": {"converter": lambda x: int(x, base=16), "type_name": "Int"},
    "STR": {"converter": lambda x: x, "type_name": "Str"},
}

interface_relations = bidict(
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
ident = {"pi": (3.1415, "Float")}


def execute_lambda(symbol, args):
    # pprint(args)
    # breakpoint()
    arg_qty = len(list(lambdas[symbol].items())[0])
    arg_types = [arg.type_name for arg in args[:arg_qty] if arg]
    chosen_lambda, return_type = match_types(lambdas[symbol], arg_types)
    arg_values = [arg.value for arg in args[:arg_qty]]
    ret_val = Token(
        value=chosen_lambda(*arg_values),
        token_type=return_type,
        source_line=None,  # noqa: E501
    )
    ret_val.type_name = return_type
    if len(args) > arg_qty:
        ret_list = [ret_val]
        ret_list.extend(args[arg_qty:])
        return ret_list
    return ret_val


def interpret(stack):
    # pprint(stack)
    # breakpoint()
    if not stack:
        return ""
    if isinstance(stack, Token):
        return stack
    if isinstance(stack, list):
        if len(stack) == 1:
            return interpret(stack[0])
        if len(stack) == 2:
            if stack[0].token_type == "LAMBDA" and isinstance(stack[1], list):
                return execute_lambda(stack[0].value, interpret(stack[1]))
        if stack[0].token_type == "LET":
            return do_bind(stack)
        return [interpret(s) for s in stack]
    raise LangException("Interpreter ERROR")


def do_bind(stack):
    # breakpoint()
    stack.pop(0)
    val_name = stack.pop(0).value
    val_type = "Unknown"
    if not isinstance(stack[0], list) and stack[0].token_type == "TYPED_SEP":
        val_type = stack[1].value
        stack.pop(0)
        stack.pop(0)
    value = interpret(stack)
    ident[val_name] = (value.value, val_type)
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


def create_stack(token_list, stack):
    # pprint(stack)
    # breakpoint()
    if not token_list:
        return stack
    if token_list[0].token_type == "INDENT":
        token_list.pop(0)
    t = token_list[0]
    if t.token_type == "UNKNOWN":
        raise LangException(f"Syntatic ERROR on {t.source_line}")
    if t.token_type == "SYMBOL":
        return symbol_dealer(t, token_list, stack)
    if t.token_type in value_types.keys():
        return value_dealer(t, token_list, stack)
    if t.token_type == "LET":
        return bind_dealer(t, token_list, stack)
    raise LangException(f"ERROR creating stack for '{t.source_line}'")


# TODO transformar token de lexing em token de parsing
def set_symbol_definition(tok):
    # breakpoint()
    if tok.value in lambdas.keys():
        tok.token_type = "LAMBDA"
    elif tok.value in ident.keys():
        tok.token_type = "IDENT"
    else:
        raise LangException(f'ERROR: undefined symbol "{tok.value}"')
    return tok


def symbol_dealer(t, token_list, stack):
    # breakpoint()
    t = set_symbol_definition(t)
    if t.token_type == "LAMBDA":
        stack.append([t, create_stack(token_list[1:], [])])
        return [stack]
    if t.token_type == "IDENT":
        t.type_name = ident[t.value][1]
        t.value = ident[t.value][0]
        t.token_type = "VALUE"
        stack.append(t)
        return create_stack(token_list[1:], stack=stack)


def value_dealer(t, token_list, stack):
    # breakpoint()
    t.value = value_types[t.token_type]["converter"](t.value)
    t.type_name = value_types[t.token_type]["type_name"]
    t.token_type = "VALUE"
    stack.append(t)
    return create_stack(token_list[1:], stack=stack)


def bind_dealer(t, token_list, stack: List):
    if not token_list[1].token_type == "SYMBOL":
        raise LangException(
            "ERROR: expecting a symbol to bind a "
            'value to after "let" statement on '
            f'line "{t.source_line}"'
        )  # noqa: E501
    stack.append(t)
    stack.append(token_list[1])
    if token_list[2].token_type == "TYPED_SEP":
        if token_list[3].token_type not in ("INTERFACE", "TYPE"):
            raise LangException(
                "ERROR: typed symbol needs a "
                f'type, not a "{t.value}"'
                f'\nOn line "{t.source_line}"'
            )  # noqa: E501
        if (
            token_list[3].value not in interface_relations.keys()
            and token_list[3].value not in interface_relations.inverse.keys()
        ):
            raise LangException(
                "ERROR: Unknown type or interface "
                f'on line "{t.source_line}"'  # noqa: E501
            )
        stack.append(token_list[2])
        stack.append(token_list[3])
        return create_stack(token_list[4:], stack=stack)
    else:
        return create_stack(token_list[2:], stack=stack)
