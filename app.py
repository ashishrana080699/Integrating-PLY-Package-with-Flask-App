#import required packages
from flask import *
import json
import os
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np

app = Flask(__name__)
NO_OF_CHARS = 256
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/run',methods=["post"])
def run():
    if os.path.exists("Answer.txt"):
        os.remove("Answer.txt")
    formvalues = request.form
    path1 = "static/json/"
    with open(os.path.join(os.getcwd()+"/"+path1,'file.json'), 'w') as f:
        json.dump(formvalues, f)
    with open(os.path.join(os.getcwd()+"/"+path1,'file.json'), 'r') as f:
        values = json.load(f)
        s=values["text"]

    Funct(s)
    f=open("Answer.txt",'r')
    return render_template("index.html", txt_disp=s, ans=f.read(), **request.args)

def Funct(s): 
    tokens = (
        'NAME','NUMBER',
        'PLUS','MINUS','TIMES','DIVIDE','EQUALS',
        'LPAREN','RPAREN',
        )

    # Tokens

    t_PLUS    = r'\+'
    t_MINUS   = r'-'
    t_TIMES   = r'\*'
    t_DIVIDE  = r'/'
    t_EQUALS  = r'='
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'

    def t_NUMBER(t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            print("Integer value too large %d", t.value)
            t.value = 0
        return t

    # Ignored characters
    t_ignore = " \t"

    def t_newline(t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
        
    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)
        
    # Build the lexer
    import ply.lex as lex
    lexer = lex.lex()

    # Parsing rules

    precedence = (
        ('left','PLUS','MINUS'),
        ('left','TIMES','DIVIDE'),
        ('right','UMINUS'),
        )

    # dictionary of names
    names = { }

    def p_statement_assign(t):
        'statement : NAME EQUALS expression'
        names[t[1]] = t[3]

    def p_statement_expr(t):
        'statement : expression'
        f = open("Answer.txt", "a")
        f.write(str(t[1]))
        f.close()
    def p_expression_binop(t):
        '''expression : expression PLUS expression
                    | expression MINUS expression
                    | expression TIMES expression
                    | expression DIVIDE expression'''
        if t[2] == '+'  : t[0] = t[1] + t[3]
        elif t[2] == '-': t[0] = t[1] - t[3]
        elif t[2] == '*': t[0] = t[1] * t[3]
        elif t[2] == '/': t[0] = t[1] / t[3]

    def p_expression_uminus(t):
        'expression : MINUS expression %prec UMINUS'
        t[0] = -t[2]

    def p_expression_group(t):
        'expression : LPAREN expression RPAREN'
        t[0] = t[2]

    def p_expression_number(t):
        'expression : NUMBER'
        t[0] = t[1]

    def p_expression_name(t):
        'expression : NAME'
        try:
            t[0] = names[t[1]]
        except LookupError:
            f = open("Answer.txt", "w")
            f.write("Undefined name '%s'" % t[1])
            f.close()
            #print("Undefined name '%s'" % t[1])
            t[0] = 0

    def p_error(t):
        f = open("Answer.txt", "w")
        f.write("Syntax error at '%s'" % t.value)
        f.close()
        #print("Syntax error at '%s'" % t.value)

    import ply.yacc as yacc
    parser = yacc.yacc()

    parser.parse(s) 

if __name__ == '__main__':
    app.run()