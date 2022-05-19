from toolbox import LangException, Node, Token
from typing import List
from pprint import pprint  # noqa: F401
import pdb  # noqa: F401


def node_from_token(token: Token, lambdas, ident):
    node_type = None
    if token.token_type == "UNKNOWN":
        raise LangException(f"Syntatic ERROR on {token.source_line}")
    elif token.token_type == "SYMBOL":
        if token.value in lambdas.keys():
            node_type = "LAMBDA"
        elif token.value in ident.keys():
            node_type = "IDENT"
        else:
            node_type = "TBD"  # to be defined
    return Node(
        node_type=(node_type or token.token_type),
        type_name=token.token_type,
        value=token.value,
        token=token,
    )


def nodefy(token_list: List[Token], lambdas, ident):
    return [node_from_token(t, lambdas, ident) for t in token_list]


def create_stack(node_list, stack, scope):
    # pprint(stack)
    # breakpoint()
    if not node_list:
        return stack
    if node_list[0].node_type == "INDENT":
        node_list.pop(0)
    n = node_list[0]
    if n.type_name == "SYMBOL":
        return symbol_dealer(n, node_list, scope, stack)
    if n.node_type in scope.value_types.keys():
        return value_dealer(n, node_list, scope, stack)
    if n.node_type == "LET":
        return bind_dealer(n, node_list, scope, stack)
    if n.node_type == "TBD":
        raise LangException(
            f"Error: Attempt to use an undefined symbol at '{n.source_line}'"
        )
    raise LangException(f"ERROR creating stack for '{n.source_line}'")


def symbol_dealer(node, node_list, scope, stack):
    if node.node_type == "LAMBDA":
        stack.append([node, create_stack(node_list[1:], [], scope)])
        return [stack]
    if node.node_type == "IDENT":
        node.type_name = scope.ident[node.value].type_name
        node.value = scope.ident[node.value].value
        node.node_type = "VALUE"
        stack.append(node)
        return create_stack(node_list[1:], stack, scope)


def value_dealer(n, node_list, scope, stack):
    # breakpoint()
    n.value = scope.value_types[n.node_type]["converter"](n.value)
    n.type_name = scope.value_types[n.node_type]["type_name"]
    n.node_type = "VALUE"
    stack.append(n)
    return create_stack(node_list[1:], stack, scope)


def bind_dealer(n, nodes: List[Node], scope, stack: List):
    if not nodes[1].node_type == "TBD":
        raise LangException(
            "ERROR: expecting a symbol to bind a "
            'value to after "let" statement on '
            f'line "{n.source_line}"'
        )  # noqa: E501
    stack.append(n)
    stack.append(nodes[1])
    if nodes[2].node_type == "TYPED_SEP":
        if nodes[3].node_type not in ("INTERFACE", "TYPE"):
            raise LangException(
                "ERROR: typed symbol needs a "
                f'type, not a "{n.value}"'
                f'\nOn line "{n.source_line}"'
            )  # noqa: E501
        if (
            nodes[3].value not in scope.interface_relations.keys()
            and nodes[3].value not in scope.interface_relations.inverse.keys()
        ):
            raise LangException(
                "ERROR: Unknown type or interface "
                f'on line "{n.source_line}"'  # noqa: E501
            )
        stack.append(nodes[2])
        stack.append(nodes[3])
        return create_stack(nodes[4:], stack, scope)
    else:
        return create_stack(nodes[2:], stack, scope)
