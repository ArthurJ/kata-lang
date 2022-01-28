import re

def commented(line):
    return line.split('#', 1)[0]

def indented(line, r=re.compile('^\s+')):
    length = r.match(line).span()[1] if r.match(line) else 0
    return (length, line[length:])

lit_str=re.compile('[rf]?(\".*?\"|\'.*?\')')

lit_float=re.compile('[+-]?([0-9]*\.[0-9]+([eE][+-]?[0-9]*)?)')

lit_int=re.compile('[+-]?'
                       '(((0b)[0-1]+)'
                       '|((0o)[0-7]+)'
                       '|((0x)[0-9a-fA-F]+)'
                       '|((0d)?[0-9]+))')


def tokenize(line):
    line = commented(line)
    indent_qtd, line = indented(line)
    
    line = lit_str.split(line)
    
    sub_split = []
    for item in line:
        if lit_str.match(item):
            sub_split.append(('STR',item))
            continue
        for i in item.split():
            # this strategy is too agressive, TODO change it
            i=i.replace('(','').replace(')','').replace(',','')
            
            label = 'SYMB'
            if i=='let': label='LET'
            elif i in ['True','False']: 'BOOL'
            elif lit_float.match(i): label='FLOAT'
            elif lit_int.match(i): label='INT'
            
            if i:
                sub_split.append((label, i))
    
    return indent_qtd, sub_split



# para o futuro
r_words = {
    'let':'LET',
    'lambda':'LAMBDA', 
    'λ':'LAMBDA', 
    '(':'LEFT_PAREN', 
    ')':'RIGHT_PAREN',
    ',':'COMMA', 
    '.':'DOT', 
    ':':'COLON',
    'as':'AS',
    'with':'WITH', 
    '?':'QUESTION_MARK',
    'otherwise':'OTHERWISE' 
}

token_type = [
    'LAMBDA', 'LET',
    'IDENTIFIER', 'STRING', 'NUMBER', 
    'LEFT_PAREN', 'RIGHT_PAREN',
    'COMMA', 'DOT', 'COLON',
    'OTHERWISE', 'WITH', 'AS',
    'QUESTION_MARK'
]