from dataclasses import dataclass
import re


token_patterns = {
    "SHEBANG": re.compile(r"#(!.*$)"),
    "COMMENT": re.compile(r"#.*$"),
    #
    "INDENT": re.compile(r"(^[\t ]+)"),
    #
    "STR": re.compile(r"(?:(?<=^)|(?<=\s))'(.*?)'(?:(?=\s)|(?=$))"),
    "F_STR": re.compile(r"(?:(?<=^)|(?<=\s))f'(.*?)'(?:(?=\s)|(?=$))"),
    #
    "LET": re.compile(r"(?:(?<=^)|(?<=\s))(let)(?=\s)"),
    # "LAMBDA": re.compile(r"(?:(?<=^)|(?<=\s))(lambda)(?=\s)"),
    # "ACTION": re.compile(r"(?:(?<=^)|(?<=\s))(action)(?=\s)"),
    #
    "INT": re.compile(
        r"(?:(?<=^)|(?<=\s))([+-]?(?:\d_?)+(?:[eE][+-]?(?:\d_?)+)?)(?:(?=\s)|(?=$))"  # noqa: E501
    ),  # INT base 10, INT eng
    "FLOAT": re.compile(
        r"(?:(?<=^)|(?<=\s))([+-]?(?:\d_?)*\.(?:\d_?)+(?:[eE](?:\d_?)+)?)(?:(?=\s)|(?=$))"  # noqa: E501
    ),  # FLOAT base 10, FLOAT eng
    "BIN": re.compile(
        r"(?:(?<=^)|(?<=\s))([+-]?0b(?:[01]_?)+)(?:(?=\s)|(?=$))"
    ),  # noqa: E501
    "OCT": re.compile(
        r"(?:(?<=^)|(?<=\s))([+-]?0o(?:[0-7]_?)+)(?:(?=\s)|(?=$))"
    ),  # noqa: E501
    "HEX": re.compile(
        r"(?:(?<=^)|(?<=\s))([+-]?0x(?:[\da-fA-F]_?)+)(?:(?=\s)|(?=$))"
    ),  # noqa: E501
    #
    # NÃO PONHA O CARRO NA FRENTE DOS BOIS
    # "QUESTION_MARK": re.compile(
    #    r"(?:(?<=^)|(?<=\s))(\?)(?:(?=\s)|(?=$))"),
    # "UNDERSCORE": re.compile(
    #    r"(?:(?<=^)|(?<=\s))(_)(?:(?=\s)|(?=$))"),
    #
    "TYPED_SYMB": re.compile(r"(?:(?<=^)|(?<=\s))(\S+::\S+)(?:(?=\s)|(?=$))"),
    "SYMBOL": re.compile(
        r"(?:(?<=^)|(?<=\s))([^\sA-Z0-9\+:\.\-]+)(?:(?=\s)|(?=$))"
    ),  # noqa: E501
    #
    "TYPE": re.compile(r"(?:(?<=^)|(?<=\s))([A-Z][a-z]+)(?:(?=\s)|(?=$))"),
    "INTERFACE": re.compile(
        r"(?:(?<=^)|(?<=\s))([A-Z][A-Z0-9]*)(?:(?=\s)|(?=$))"
    ),  # noqa: E501
}


@dataclass
class Token:
    token_type: str
    value: str


def replacer(str_tok_list, pattern, tok_type):
    for idx, item in enumerate(str_tok_list):
        if not isinstance(item, Token):
            if found := pattern.findall(item):
                str_tok_list[idx] = [
                    Token(tok_type, i) if i in found else i
                    for i in pattern.split(item)
                    if i.strip()
                ]
    return flatten(str_tok_list)


def flatten(itr):
    if type(itr) in (str, bytes):
        yield itr
    else:
        for x in itr:
            try:
                yield from flatten(x)
            except TypeError:
                yield x


def typed_parser(thing):
    if isinstance(thing, str) or thing.token_type != "TYPED_SYMB":
        return thing
    typed_value = thing.value.split("::")
    # typed_value.reverse()
    for tok_type in token_patterns.keys():
        typed_value = list(
            replacer(typed_value, token_patterns[tok_type], tok_type)
        )  # noqa: E501
    return typed_value


def tokenize_code(code):
    lines = [[line] for line in code]
    for tok_type in token_patterns.keys():
        for idx, line in enumerate(lines):
            lines[idx] = list(
                replacer(line, token_patterns[tok_type], tok_type)
            )  # noqa: E501
            if tok_type == "TYPED_SYMB":
                lines[idx] = list(
                    flatten([typed_parser(tok) for tok in lines[idx]])
                )  # noqa: E501
    return lines


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    from pprint import pprint

    with open("tokenizers_test_code.txt", "r") as test_code_file:
        pprint(tokenize_code(test_code_file.read().splitlines()))
