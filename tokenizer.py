import re
from toolbox import Token
from patterns import patterns


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
            tokenize(test_code.read().splitlines(), patterns),
            width=80,
            depth=2,
        )
