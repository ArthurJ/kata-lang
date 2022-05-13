from dataclasses import dataclass
import re


token_patterns = {
    # "SHEBANG": re.compile(r"(#\!.*)"),
    "COMMENT": re.compile(r"(#.*)$"),
    "INDENT": re.compile(r"^([\t ]+)"),
    #
    "STR": re.compile(r"(?:(?<=^)|(?<=\s))'(.*?)'(?:(?=\s)|(?=$))"),
    "F_STR": re.compile(r"(?:(?<=^)|(?<=\s))f'(.*?)'(?:(?=\s)|(?=$))"),
    # R_STR? BYTES?
    #
    "LET": re.compile(r"(?:(?<=^)|(?<=\s))(let)(?=\s)"),
    # "LAMBDA": re.compile(r"(?:(?<=^)|(?<=\s))(lambda)(?=\s)"),
    # "ACTION": re.compile(r"(?:(?<=^)|(?<=\s))(action)(?=\s)"),
    #
    # # KIS for now
    # "NUM": re.compile(r"(?:(?<=^)|(?<=\s))([+-]?(?:\d+)(?:\.\d+)?)+(?:(?=\s)|(?=$))"),  # noqa: E501
    "INT": re.compile(
        r"(?:(?<=^)|(?<=\s))([+-]?(?:\d_?)+)(?:(?=\s)|(?=$))"  # noqa: E501
    ),  # INT base 10
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
    "BOOL": re.compile(r"(?:(?<=^)|(?<=\s))(true|false)(?:(?=\s)|(?=$))"),
    #
    "TYPED_SYMB": re.compile(r"(?:(?<=^)|(?<=\s))(\S+::\S+)(?:(?=\s)|(?=$))"),
    "TYPED_SEP": re.compile(r"(?<=^)(::)(?=$)"),
    "SYMBOL": re.compile(
        r"(?:(?<=^)|(?<=\s))([^\sA-Z0-9:\.\'][^\s:\.\']*)(?:(?=\s)|(?=$))"
    ),  # noqa: E501
    #
    "TYPE": re.compile(r"(?:(?<=^)|(?<=\s))([A-Z][a-z]+)(?:(?=\s)|(?=$))"),
    "INTERFACE": re.compile(
        r"(?:(?<=^)|(?<=\s))([A-Z]+)(?:(?=\s)|(?=$))"
    ),  # noqa: E501
    "UNKNOWN": re.compile(r"(.*)"),
}


@dataclass
class Token:
    token_type: str
    value: str
    source_line: str


def replacer(str_tk_list, pattern, tk_type, line):
    for index, item in enumerate(str_tk_list):
        if not isinstance(item, Token):
            if found := pattern.findall(item):
                str_tk_list[index] = [
                    Token(tk_type, i, line) if i in found else i
                    for i in pattern.split(item)
                    if (tk_type == "INDENT" or i.strip())
                ]
    return flatten(str_tk_list)


def flatten(itr):
    if type(itr) in (str, bytes):
        yield itr
    else:
        for x in itr:
            try:
                yield from flatten(x)
            except TypeError:
                yield x


def typed_parser(thing, patterns):
    if isinstance(thing, str) or thing.token_type != "TYPED_SYMB":
        return thing
    typed_value = re.split("(::)", thing.value)
    line = thing.source_line
    # typed_value.reverse()
    for tk_type, pattern in patterns.items():
        typed_value = list(replacer(typed_value, pattern, tk_type, line))  # noqa: E501
    return typed_value


def tokenize(code, patterns):
    for i, line in enumerate(code):
        code[i] = [line]
        for tk_type, pattern in patterns.items():
            code[i] = [
                tok for tok in replacer(code[i], pattern, tk_type, line) if tok
            ]  # noqa: E501
            if tk_type == "TYPED_SYMB":
                code[i] = list(
                    flatten([typed_parser(tok, patterns) for tok in code[i]])
                )  # noqa: E501
    return [i for i in code if i]


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    from pprint import pp

    with open("tokenizers_test_code.txt", "r") as test_code:
        pp(
            tokenize(test_code.read().splitlines(), token_patterns),
            width=80,
            depth=2,
        )
