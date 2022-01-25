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




r_words = {
    'lambda':'LAMBDA', 'λ':'LAMBDA', 'let':'LET',
    '(':'LEFT_PAREN', ')':'RIGHT_PAREN',
    ',':'COMMA', '.':'DOT', ':':'COLON',
    'otherwise':'OTHERWISE', 'with':'WITH', 'as':'AS',
    '?':'QUESTION_MARK'
}
token_type = [
    'LAMBDA', 'LET',
    'IDENTIFIER', 'STRING', 'NUMBER', 
    'LEFT_PAREN', 'RIGHT_PAREN',
    'COMMA', 'DOT', 'COLON',
    'OTHERWISE', 'WITH', 'AS',
    'QUESTION_MARK'
]

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

scope = {'cache':{}}

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

def interpret(token_list,stop=False, stack=None, fun_map=std_lib_funs):
    #breakpoint()
    if not stack: stack=[]
    if not token_list: return stack
    
    token = token_list.pop(0)
    
    if token[0]=='SYMB':
        if token[1] in fun_map:
            stack.append(fun_map[token[1]][1])
            for _ in range(fun_map[token[1]][0]):
                if token_list[0][1] in fun_map:
                    stack.append(interpret(token_list, True))
                else: 
                    stack.append(literal_val(token_list.pop(0)))
        else:
            print('Function not implemented')
    else: # if literal
        stack.append(literal_val(token))
    if stop: 
        return stack
    interpret(token_list, stack=stack)
    
    return stack

def apply(stack, scope=scope):
    print(stack)
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
        pprint.pprint(scope['cache'])
        return
        
    stack = interpret(token_list)
    print(apply(stack))


if __name__ == '__main__':
    prompt()
