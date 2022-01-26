from time import process_time
from functools import wraps

import pprint

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

scope = {'cache':{},
         'functions':{'outer_scope':std_lib_funs},
         'values':{}}

def prompt():
    while True:
        try:
            line = input('-> ')
        except EOFError: 
            break
        run_line(line)


def literal_val(token):
    if token[0]=='STR': return token[1]
    if token[0]=='INT': return int(token[1])
    if token[0]=='FLOAT': return float(token[1])
    if token[1] in scope: return scope[token[1]]
    raise ValueError(f'{token[1]} not know')

def is_literal(val):
    if isinstance(val, tuple): return val[0] in ['STR', 'INT', 'FLOAT']
    if isinstance(val, str): return True
    if isinstance(val, int): return True
    if isinstance(val, float): return True
    if isinstance(val, bool): return True
    return False

def bind(symb, value, scope=scope):
    if not symb[0]=='SYMB': raise ValueError('To bind a symbol is needed')
    if is_literal(value):
        scope[symb[1]]=literal_val(value)
    elif value[1] in scope:
        scope[symb[1]]=scope[value[1]]
    else: #TODO accept expressions
        raise ValueError('For now, just bind literal values')

def interpret(token_list,stop=False, stack=None, fun_map=std_lib_funs):
    #breakpoint()
    if not stack: stack=[]
    if not token_list: return stack
    
    token = token_list.pop(0)
    if token[0]=='LET':
        symb=token_list.pop(0)
        value=token_list.pop(0)
        bind(symb, value)
        return stack
    elif token[0]=='SYMB':
        if token[1] in fun_map:
            stack.append(fun_map[token[1]][1])
            for _ in range(fun_map[token[1]][0]):
                if token_list[0][1] in fun_map:
                    stack.append(interpret(token_list, True))
                else: 
                    stack.append(literal_val(token_list.pop(0)))
        elif token[1] in scope: # for now, variables only take values, not functions
            stack.append(scope[token[1]])
        else:
            print('Unknown Symbol')
    else:
        stack.append(literal_val(token))
    if stop: 
        return stack
    interpret(token_list, stack=stack)
    
    return stack

def apply(stack, scope=scope):
    if not stack: return ''
    print(stack)
    if is_literal(stack[0]):
        return stack[0]
    for i, item in enumerate(stack):
        if isinstance(item, list):
            stack[i] = apply(stack[i])
    if (stack[0], tuple(stack[1:])) in scope['cache']:
        return scope['cache'][(stack[0], tuple(stack[1:]))]
    scope['cache'][(stack[0], tuple(stack[1:]))] = (result:=stack[0] (*stack[1:]))
    return result


@timer()
def run_line(line):
    
    indent, token_list = tokenize(line)
    if token_list[0][1] == 'dir':
        pprint.pprint(scope)
        return
    
    try:
        stack = interpret(token_list)
        print(apply(stack))
    except Exception as e:
        #breakpoint()
        print(f'Error: {e}')


if __name__ == '__main__':
    prompt()
