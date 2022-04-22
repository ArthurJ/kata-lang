from dataclasses import dataclass
import re


token_patterns = {
    "SHEBANG": re.compile(r"#(!.*$)"),
    "COMMENT": re.compile(r"#.*$"),
    "INDENT": re.compile(r"(^[\t ]+)"),
    "STR": re.compile(r"(?:(?<=^)|(?<=\s))'(.*?)'(?:(?=\s)|(?=$))"),
    # 'R_STR':re.compile(r"r'(.*?)'"), #TODO ?
    "F_STR": re.compile(r"(?:(?<=^)|(?<=\s))f'(.*?)'(?:(?=\s)|(?=$))"),
    "LET": re.compile(r"(?:(?<=^)|(?<=\s))(let)(?=\s)"),
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
    "TYPED_THING": re.compile(r"(?:(?<=^)|(?<=\s))(\w+::\w+)(?:(?=\s)|(?=$))"),
    "SYMB": re.compile(r"(?:(?<=^)|(?<=\s))([a-z]\w*)(?:(?=\s)|(?=$))"),
    "TYPE": re.compile(r"([A-Z][a-z]+)"),
    "INTERFACE": re.compile(r"([A-Z][A-Z0-9]*)"),
}
# TODO ? #'TYPED_VAL': 5::Int, 12::Float, 9::NUM
# TODO ? #'TYPED_VAR': a::NUM, b::Str


@dataclass
class Token:
    token_type: str
    value: str


def replacer(str_tok_list, pattern, tok_type):
    for idx, item in enumerate(str_tok_list):
        if not isinstance(item, Token):
            # print('replacer input->', str_tok_list)
            # print('replacer item->', item)
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


def tthing_parse(thing):
    if isinstance(thing, str):
        return thing
    if thing.token_type != "TYPED_THING":
        return thing

    val_and_type = thing.value.split("::")
    for tok_type in token_patterns.keys():
        val_and_type = list(
            replacer(val_and_type, token_patterns[tok_type], tok_type)
        )  # noqa: E501
    print(val_and_type)
    return thing


def tokenize_code(code):
    lines = [[line] for line in code]
    for tok_type in token_patterns.keys():
        for idx, line in enumerate(lines):
            # print('\ttokenize_code antes->', lines[idx])
            lines[idx] = list(
                replacer(line, token_patterns[tok_type], tok_type)
            )  # noqa: E501
            # print('\ttokenize_code depois->',lines[idx])
            if tok_type == "TYPED_THING":
                # print('\ttokenize_code [typed_things] antes ->', lines[idx])
                lines[idx] = [tthing_parse(token) for token in lines[idx]]  # noqa: E501
                # print('\ttokenize_code [typed_things] depois ->', lines[idx])
    # TODO token para símbolos quebrando os strings que sobram
    # VER RESULTADOS
    # for line in lines:
    #   print(line)


# -----------------------------------------------------------------------------

with open("tokenizers_test_code.txt", "r") as test_code_file:
    tokenize_code(test_code_file.read().splitlines())
