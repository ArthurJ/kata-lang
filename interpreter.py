from time import process_time
from functools import wraps

import pprint
from prompt_toolkit import PromptSession

from tokenizer import tokenize

def timer(msg="Exec time: {0:.7f}s"):
    def decorador(method):
        @wraps(method)
        def wrapper(*args, **kw):
            ts = process_time()
            result = method(*args, **kw)
            te = process_time()
            delta = te-ts
            print(msg.format(delta))
            return result
        return wrapper
    return decorador

def tupleit(l):
    return tuple(map(tupleit, l)) if isinstance(l, (list, tuple)) else l

#future -> (qtd_arg, {(type list):implementation})
std_lib_funs = {
    '+': (2, lambda x,y: x+y),
    '-': (2, lambda x,y: x-y),
    '*': (2, lambda x,y: x*y),
    '/': (2, lambda x,y: x/y),
    '//':(2, lambda x,y:x//y),
    '**':(2, lambda x,y:x**y),
    '=': (2, lambda x,y:x==y),
    '<=':(2, lambda x,y:x<=y),
    '>=':(2, lambda x,y:x>=y),
    '<': (2, lambda x,y: x<y),
    '>': (2, lambda x,y: x>y),
}

class Scope:
    def __init__(self, values=None,
                 functions=std_lib_funs, cache=None,
                 outer_scope=None) -> None:
        self.__cache__ = cache or {}
        self.__values__ = values or {}
        self.__functions__ = functions or {}
        if outer_scope:
            self.__cache__.update(outer_scope.cache)
            self.__values__.update(outer_scope.values)
            self.__functions__.update(outer_scope.functions)

    @property
    def functions(self):
        # As funções podem mudar, 
        # mas os resultados do lambda no cache se mantém pois o lambda ao qual se referem é a chave
        # assim não é necessário atualizar o cache
        return self.__functions__

    @property
    def values(self):
        return self.__values__

    @property
    def cache(self):
        return self.__cache__

    def __contains__(self, value):
        return value in self.cache \
                or value in self.__functions__ \
                or value in self.__values__

    def __str__(self):
        return 'Functions:\n'\
                + pprint.pformat(self.functions).replace('\n','\n ')\
                + '\nCache:\n'\
                + pprint.pformat(self.__cache__).replace('\n','\n ')\
                + '\nValues:\n'\
                + pprint.pformat(self.__values__).replace('\n','\n ')


scope = Scope()

def prompt():
    session =  PromptSession()
    while True:
        try:
            line = session.prompt('-> ')
        except EOFError:
            break
        run_line(line)


def literal_val(token):
    if token[0]=='STR': return token[1]
    if token[0]=='INT': return int(token[1])
    if token[0]=='FLOAT': return float(token[1])
    if token[0]=='BOOL': return token[1]=='True'
    if token[1] in scope: return scope[token[1]]
    raise ValueError(f'{token[1]} not know')

def is_literal(val):
    if isinstance(val, tuple): return val[0] in ['STR', 'INT', 'FLOAT', 'BOOL']
    return False


'''
0
+ 1 1
+ 1 - 5 4
let x 0
let y - 4 8
'''
def interpret(token_list, scope=scope):
    if not token_list: return []
    #breakpoint()
    root = token_list.pop(0)
    if root[0]=='LET':
        return ['LET', interpret(token_list, scope)]
    elif is_literal(root): return root
    elif root[1] in scope.functions:
        arg_qtd, _lambda= scope.functions[root[1]]
        args = []
        for _ in range(arg_qtd):
            args.append(interpret(token_list, scope))
        return [_lambda, args]  # [root, args]
    elif root[1] in scope.values:
        return scope.values[root[1]]
    elif root[0]=='SYMB': return [root, interpret(token_list, scope)]

    raise ValueError('Something went wrong with your expression')


def bind(symb, val, scope=scope): # sempre guarda expressões
    if not symb[0]=='SYMB': raise ValueError('To bind a symbol is needed')
    scope.values[symb[1]]=val


def eval(stack, scope=scope):
    #print(stack)
    if not stack: return ''
    if is_literal(stack): return literal_val(stack)
    if stack[0]=='LET':
        bind(*stack[1], scope)
        return stack
    if callable(stack[0]):
        scope.cache[stack] = \
            scope.cache.get(stack,
                            stack[0](*[eval(x, scope) for x in stack[1]]))
        return scope.cache[stack]
    if stack[0]=='SYMB' and stack[1] not in scope.values:
        raise ValueError('Unknown symbol')
    raise Exception('Something wrong is not right')

@timer()
def run_line(line):
    indent, token_list = tokenize(line)
    if token_list[0][1] == 'dir':
        print(scope)
        return
    try:
        stack = tupleit(interpret(token_list))
        print(eval(stack))
    except Exception as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    prompt()
