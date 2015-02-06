#! /usr/bin/env python
'''
Date: 2015/02/06-07
Description: Hust.UniqueStudio.Hackday
'''

import calc

__table = {}
__specail_forms = {}

# parse

def atom(token):
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return token # the same as str(token)

def get_tokens(source):
    tokens = []
    pos = 0
    is_str = False
    token = ''
    while pos < len(source):
        c = source[pos]
        if c == '(' or c == ')':
            if len(token) != 0: tokens.append(token)
            token = ''
            tokens.append(c)
        elif c == ' ' and not is_str:
            tokens.append(token)
            token = ''
        elif c == '\"':
            is_str = not is_str
            token += c
        else:
            token += c
        pos += 1
    return tokens

def parse(source):
    stack = [[]]
    try: 
        for token in get_tokens(source):
            if '(' == token: stack.append([])
            elif ')' == token: 
                exp = stack.pop()
                if len(exp) > 0: stack[-1].append(exp)
                else: raise SyntaxError('Empty list!')
            else: stack[-1].append(atom(token))
        return stack.pop()[0]
    except:
        raise SyntaxError('Syntax Error')

# built-in function

def _import(module, name=None):
    if not name: name = module
    __table.update({name: __import__(module)})

def _print(x):
    print x

def build_table():
    import math, operator as op
    __table.update(vars(math))
    __table.update({
        '+': calc.add, '-': calc.sub, '*': calc.mul, '/': calc.div, '**': pow,
        '<': calc.lt, '>': calc.gt, '<=': calc.le, '>=': calc.ge, '=': calc.eq})
    
    __table.update({
        'quotient': lambda a, b: a // b,
        'remainder':calc.rem,
        'modulo':   lambda a, b: a % b,
        'gcd':      calc.gcd
        'lcm':      calc.lcm

        'fwrite':   lambda f, s: open(f, 'w').write(s),
        'fread':    lambda f: open(f).read(),
        'expt':     lambda x, y: x ** y,
        'list':     lambda *x: list(x),
        'set':      lambda *x: set(x),
        'dict':     lambda x, y: dict(zip(x, y)), 
        'zero?':    lambda x: x == 0, 
        'print':    _print, 'import': _import, 
        'map':      map,
        'reduce':   reduce,
        'max':      max,
        'min':      min,
        'abs':      abs,
        'len':      len, 
        'append':   op.add,  
        'apply':    apply,
        'begin':    lambda *x: x[-1],
        'first':    lambda x: x[0],
        'rest':     lambda x: x[1:], 
        'cons':     lambda x, y: [x] + y,
        'eq?':      op.is_, 
        'equal?':   op.eq, 
        'list?':    lambda x: isinstance(x, list), 
        'max':      max,
        'min':      min,
        'not':      op.not_,
        'null?':    lambda x: x == [], 
        'number?':  lambda x: isinstance(x, int) or isinstance(x, float),  
        'complex?': lambda x: isinstance(x, complex),
        'boolean?': lambda x: isinstance(x, bool),
        'rational?':lambda x: isinstance(x, float),
        'integer?': lambda x: isinstance(x, int),
        'zero?':    lambda x: x == 0,
        'positive?':lambda x: x > 0,
        'negative?':lambda x: x < 0,
        'odd?':     lambda x: x % 2 == 1,
        'even?':    lambda x: x % 2 == 0,

        'procedure?': callable,
        'round':    round,
        'symbol?':  lambda x: isinstance(x, str),
        })

build_table()

# eval

def find_symbol(table, symbol):
    pos = symbol.rfind('.')
    return getattr(table[symbol[:pos]], symbol[pos+1:])

def leval(exp, local={}):
    if isinstance(exp, str):
        if len(exp) > 2 and exp[0]=='\"' and exp[-1]=='\"': return exp[1:-1]
        elif exp in local: return local[exp]
        elif exp in __table: return __table[exp]
        elif '.' in exp: return find_symbol(__table, exp)
        else: raise NameError('No such name!')
    elif not isinstance(exp, list):
        return exp
    first = exp[0]
    if first == 'quote' or first == '\'':
        return exp[1:]
    elif first == 'if':
        (_, test, t, f) = exp
        return leval(t, local) if leval(test, local) else leval(f, local)
    elif first == 'def':
        (_, var, sub) = exp
        __table[var] = leval(sub, local)
    elif first == 'do':
        l = local.copy()
        updates = {}
        (_, v, t) = exp
        for var in v:
            (var, val, update) = var
            l[var]=val
            updates[var] = update
        (test, res) = t
        while not leval(test,l):
            for k in updates:
                l[k] = leval(updates[k], l)
        return leval(res, l)
    elif first == 'fn':
        (_, var, sub) = exp
        return Lamfn(var, sub, local)
    else:
        fn = leval(first, local)
        args = [leval(sub, local) for sub in exp[1:]]
        return fn(*args)

# repl

def check_paren(source_in):
    paren = 0
    for c in source_in:
        if c == '(': paren += 1
        elif c == ')': paren -= 1
    return paren

def repl(prompt='pylisp'):
    prompt += '=>'
    pro = prompt
    source = ''
    while True: 
        source += raw_input(pro) + ' '
        paren = check_paren(source)
        if paren <= 0:
            if paren == 0:
                try : print leval(parse(source))
                except Exception, e: print e
            elif paren < 0:
                print 'Error: unmacthed parentheis!'
            pro = prompt
            source = ''
        else:
            pro = '.'*len(prompt[:-2]) + '=>' + ' '*paren*2

class Lamfn:
    def __init__(self, var, sub, local):
        self.var, self.sub, self.local = var, sub, local
    def __call__(self, *args):
        local = self.local.copy()
        local.update(dict(zip(self.var, args)))
        return leval(self.sub, local)

def interpret(filename):
    source = ''
    for line in open(filename).readlines():
        source += line + ' '
        paren = check_paren(source)
        if paren <= 0:
            if paren == 0:
                try: leval(parse(source))
                except Exception, e: print e
            elif paren < 0:
                print 'Error: unmatched parentheis!'
            source = ''

if __name__ == '__main__':
    import sys
    argstr = sys.argv[1]
    if argstr == '-repl': repl() 
    else :interpret(sys.argv[1])

