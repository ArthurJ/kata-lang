from dataclasses import dataclass
from typing import Dict, List


class Bidict(dict):
    def __init__(self, *args, **kwargs):
        super(Bidict, self).__init__(*args, **kwargs)
        self.inverse = {}
        for key, value in self.items():
            self.inverse.setdefault(value, []).append(key)

    def __setitem__(self, key, value):
        if key in self:
            self.inverse[self[key]].remove(key)
        super(Bidict, self).__setitem__(key, value)
        self.inverse.setdefault(value, []).append(key)

    def __delitem__(self, key):
        self.inverse.setdefault(self[key], []).remove(key)
        if self[key] in self.inverse and not self.inverse[self[key]]:
            del self.inverse[self[key]]
        super(Bidict, self).__delitem__(key)


class LangException(Exception):
    pass


@dataclass
class Token:
    token_type: str
    value: str
    source_line: str


@dataclass
class Scope:
    value_types: Dict
    ident: Dict
    interface_relations: Bidict
    lambdas: List


class Node:
    def __init__(self, node_type, type_name, value, token=None):
        self.original_token = token
        self.node_type = node_type
        self.type_name = type_name
        self.value = value

    @property
    def token_type(self):
        if not self.original_token:
            return None
        return self.original_token.token_type

    @property
    def source_line(self):
        if not self.original_token:
            return None
        return self.original_token.source_line

    def __repr__(self) -> str:
        return (
            f"Node(value={self.value},"
            f"\n\t node_type={self.node_type},"
            f"\n\t type_name={self.type_name},"
            f"\n\t original_token={self.original_token})"
        )

    def __str__(self) -> str:
        return str(self.value)
