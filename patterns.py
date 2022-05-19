import re

patterns = {
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
