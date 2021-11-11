
DEBUG_PARSE = True

import sys
import os
import time



def interpret(tks):
    ast = parseTerm(tks)                # Parse the entry.
    tks.checkEOF()                      # Check if everything was consumed by the parse
    if DEBUG_PARSE:
        print("==debug mode============")
        print("BELOW IS THE PARSE TREE:")
        print(ast)
        print("========================")
    prettyPrint(ast)
    # tval = eval([],ast)                 # Evaluate the entry in an empty context.
    # val,typ = replShowTaggedValue(tval) # Report the resulting value.
    # print("val it =",val,":",typ)

def prettyPrint(ast):
    #['AP',['LM', name, theRest],defn]
    file = open('prettyPrint.sml','w')
    counter = 1
    main = ''
    endmain = ''
    file.write('let\n')
    while 'LM' in str(ast):
        var = 'x'+str(counter)
        term = 't'+str(counter)
        file.write('    val '+var+' = "'+str(ast[1][1])+'"\n')
        file.write('    val '+term+' = '+str(makeSMLFriendly(ast[2]))+'\n')
        ast = ast[1][2]
        main+='AP( LM ('+var+','
        endmain = '),'+term+')'+endmain
        counter+=1
    file.write('    val t = '+str(makeSMLFriendly(ast))+'\n')
    file.write('    val main = ' +main+'t'+endmain +'\n')
    file.write('    val value = norReduce main\nin\n    print (pretty value)\nend')

    file.close()

def makeSMLFriendly(ast):
    first = ast[0]
    if first is 'LM':
        return 'LM("'+str(ast[1])+'", '+makeSMLFriendly(ast[2]) + ')'
    if first is 'AP':
        return 'AP( '+ str(makeSMLFriendly(ast[1])) + ', ' + str(makeSMLFriendly(ast[2])) + ')'
    else:
        return 'VA "'+str(ast[1])+'"'
 
def lookUpVar(x,env,err):
    for (y,v) in env:
        if y == x:
            return v
    raise RunTimeError("Use of variable '"+x+"'. "+err)


def getIntValue(taggedValue,errMsg):
    if not isinstance(taggedValue,list) or taggedValue[0] != "Int":
        raise TypeError(errMsg)
    return taggedValue[1]

def getBoolValue(taggedValue,errMsg):
    if not isinstance(taggedValue,list) or taggedValue[0] != "Bool":
        raise TypeError(errMsg)
    return taggedValue[1]

def getClosValue(taggedValue,errMsg):
    if not isinstance(taggedValue,list) or taggedValue[0] != "Clos":
        raise TypeError(errMsg)
    return taggedValue[1],taggedValue[2],taggedValue[3]

def replShowTaggedValue(taggedValue):
    if isinstance(taggedValue,list) or len(taggedValue) < 2:
        val = taggedValue[1]
        tag = taggedValue[0]
        if tag == "Int":
            return (repr(val),'int')
        elif tag == "Bool":
            return (repr(val).lower(),'bool')
        if tag == "Clos":
            return ('fn','fn')
        if tag == "Bottom":
            return ('_|_',"Error! You forgot to implement (or return something) somewhere.")
    raise RunTimeError("Interpreter incorrectly constructed a bad value.")

#
# ------------------------------------------------------------
#

#
# Exceptions
#
# These define the exception raised by the interpreter.
#
class TypeError(Exception):
    pass

class RunTimeError(Exception):
    pass

class ParseError(Exception):
    pass

class SyntaxError(Exception):
    pass

class LexError(Exception):
    pass

#
# ------------------------------------------------------------
#
# The Parser
#
# This is a series of mutually recursive parsing functions that
# consume the stream of tokens. Each one corresponds to some 
# LHS of a grammar production. Their parsing action roughly
# corresponds to each of the case of the RHSs of productions.
#
# Each takes the token stream as a parameter, and returns an AST
# of what they parsed. The AST is represented as nested Python
# lists, with each list headed by a label (a string) and with
# each list having a final element that's a string reporting
# the place in the source code where their parse started.
# So each AST node is a list of the form
#
#     ["Label", info1, info2, ... , infok, where]
#
# where "Label" gives the node type ("If", "Plus", "Num", etc.)
# k is the "arity" of that node's constructor, and where is 
# a string reporting the location where the parse occurred.
#
# That 'where' string can be used for reporting errors during
# "semantic" checks. (e.g. during interpretation, type-checking).
#
#

def parseTerm(tokens):
    #
    # <disj> ::= <disj> orelse <conj> | <conj>
    #

    if tokens.nextIsName():
        name = tokens.eatName()
        if tokens.next() == '=':
            tokens.eat('=')
            defn = parseFunc(tokens)
            tokens.eat(';')
            theRest = parseTerm(tokens)
            return ['AP',['LM', name, theRest],defn]
    elif tokens.next() == 'main':
        tokens.eat('main')
        tokens.eat('=')
        e = parseFunc(tokens)
        tokens.eat(';')
        return e
    else:
        return parseFunc(tokens)



def parseFunc(tokens):
    where = tokens.report()
    # 
    # <expn> ::= let val <name> = <expn> in <expn> end
    #          | if <expn> then <expn> else <expn>
    #          | fn <name> => <expn>
    if tokens.next() == 'fn':
        tokens.eat('fn')
        name = tokens.eatName()
        tokens.eat('=>')
        body = parseFunc(tokens)
        return  ["LM", name, body]



    elif tokens.nextIsName():
        name = tokens.eatName()
        name = ['VA', name]
        while tokens.nextIsName():
            newName = tokens.eatName()
            name = ['AP',name,['VA', newName]]
        if tokens.next() == '(':
            tokens.eat('(')
            rest = parseFunc(tokens)
            tokens.eat(')')
            return ['AP', name, rest]
        return name
    elif tokens.next() == '(':
        tokens.eat('(')
        inside = parseFunc(tokens)
        tokens.eat(')')
        if tokens.nextIsName():
            appName = tokens.eatName()
            return ['AP', inside,  appName]
        elif tokens.next() == '(':
            otherInside = parseFunc(tokens)
            return ['AP', inside, otherInside]
        else:
            return inside
    else:
        where = tokens.report()
        err1 = "Unexpected token at "+where+". "
        err2 = "Saw: '"+tokens.next()+"'. "
        raise SyntaxError(err1 + err2)


# 
# Keywords, primitives, unary operations, and binary operations.
#
# The code below defines several strings or string lists used by
# the lexical analyzer (housed as class TokenStream, below).
#

RESERVED = ['fn', 'eof', 'main']

# Characters that separate expressions.
DELIMITERS = '();,|'

# Characters that make up unary and binary operations.
OPERATORS = '+-*/<>=&!:.' 


#
# LEXICAL ANALYSIS / TOKENIZER
#
# The code below converts ML source code text into a sequence 
# of tokens (a list of strings).  It does so by defining the
#
#    class TokenStream
#
# which describes the methods of an object that supports this
# lexical conversion.  The key method is "analyze" which provides
# the conversion.  It is the lexical analyzer for ML source code.
#
# The lexical analyzer works by CHOMP methods that processes the
# individual characters of the source code's string, packaging
# them into a list of token strings.
#
# The class also provides a series of methods that can be used
# to consume (or EAT) the tokens of the token stream.  These are
# used by the parser.
#


class TokenStream:

    def __init__(self,src,filename="STDIN"):
        """
        Builds a new TokenStream object from a source code string.
        """
        self.sourcename = filename
        self.source = src # The char sequence that gets 'chomped' by the lexical analyzer.
        self.tokens = []  # The list of tokens constructed by the lexical analyzer.
        self.extents = []     
        self.starts = []

        # Sets up and then runs the lexical analyzer.
        self.initIssue()
        self.analyze()
        self.tokens.append("eof")

    #
    # PARSING helper functions
    #

    def lexassert(self,c):
        if not c:
            self.raiseLex("Unrecognized character.")

    def raiseLex(self,msg):
        s = self.sourcename + " line "+str(self.line)+" column "+str(self.column)
        s += ": " + msg
        raise LexError(s)

    def next(self):
        """
        Returns the unchomped token at the front of the stream of tokens.
        """
        return self.tokens[0]

    def advance(self):
        """ 
        Advances the token stream to the next token, giving back the
        one at the front.
        """
        tk = self.next()
        del self.tokens[0]
        del self.starts[0]
        return tk

    def report(self):
        """ 
        Helper function used to report the location of errors in the 
        source code.
        """
        lnum = self.starts[0][0]
        cnum = self.starts[0][1]
        return self.sourcename + " line "+str(lnum)+" column "+str(cnum)

    def eat(self,tk):
        """
        Eats a specified token, making sure that it is the next token
        in the stream.
        """
        if tk == self.next():
            return self.advance()
        else:
            where = self.report()
            err1 = "Unexpected token at "+where+". "
            err2 = "Saw: '"+self.next()+"'. "
            err3 = "Expected: '"+tk+"'. "
            raise SyntaxError(err1 + err2 + err3)

    def eatInt(self):
        """
        Eats an integer literal token, making sure that such a token is next
        in the stream.
        """
        if self.nextIsInt():
            tk = self.advance()
            if tk[0] == '-':
                return -int(tk[1:])
            else:
                return int(tk)
        else:
            where = self.report()
            err1 = "Unexpected token at "+where+". "
            err2 = "Saw: '"+self.next()+"'. "
            err3 = "Expected an integer literal. "
            raise SyntaxError(err1 + err2 + err3)

    def eatName(self):
        """
        Eats a name token, making sure that such a token is next in the stream.
        """
        if self.nextIsName():
            if '_' in self.next():
                where = self.report()
                err1 = "Unexpected token at "+where+". "
                err2 = "Saw: '"+self.next()+"'. "
                err3 = "Underscores are not allowed in variable names. "
                raise SyntaxError(err1 + err2 + err3)
            return self.advance()
        else:
            where = self.report()
            err1 = "Unexpected token at "+where+". "
            err2 = "Saw: '"+self.next()+"'. "
            err3 = "Expected a name. "
            raise SyntaxError(err1 + err2 + err3)

    def eatString(self):
        """
        Eats a string literal token, making sure that such a token is next in the stream.
        """
        if self.nextIsString():
            return self.advance()[1:-1]
        else:
            where = self.report()
            err1 = "Unexpected token at "+where+". "
            err2 = "Saw: '"+self.next()+"'. "
            err3 = "Expected a string literal. "
            raise SyntaxError(err1 + err2 + err3)

    def nextIsInt(self):
        """
        Checks if next token is an integer literal token.
        """
        tk = self.next()
        return tk.isdigit()

    def checkEOF(self):
        """
        Checks if next token is an integer literal token.
        """
        if self.next() != 'eof':
            raise ParseError("Parsing failed to consume tokens "+str(self.tokens[:-1])+".")


    def nextIsName(self):
        """
        Checks if next token is a name.
        """
        tk = self.next()
        isname = tk[0].isalpha() or tk[0] =='_'
        for c in tk[1:]:
            isname = isname and (c.isalnum() or c == '_')
        return isname and (tk not in RESERVED)

    def nextIsString(self):
        """
        Checks if next token is a string literal.
        """
        tk = self.next()
        return tk[0] == '"' and tk[-1] == '"'

    #
    # TOKENIZER helper functions
    #
    # These are used by the 'analysis' method defined below them.
    #
    # The parsing functions EAT the token stream, whereas
    # the lexcial analysis functions CHOMP the source text
    # and ISSUE the individual tokens that form the stream.
    #

    def initIssue(self):
        self.line = 1
        self.column = 1
        self.markIssue()

    def markIssue(self):
        self.mark = (self.line,self.column)

    def issue(self,token):
        self.tokens.append(token)
        self.starts.append(self.mark)
        self.markIssue()

    def nxt(self,lookahead=1):
        if len(self.source) == 0:
            return ''
        else:
            return self.source[lookahead-1]

    def chompSelector(self):
        self.lexassert(self.nxt() == '#' and self.nxt(2).isdigit())
        token = self.chompChar()
        token = '#'
        while self.nxt().isdigit():
            token += self.chompChar()
        self.issue(token)

    def chompWord(self):
        self.lexassert(self.nxt().isalpha() or self.nxt() == '_')
        token = self.chompChar()
        while self.nxt().isalnum() or self.nxt() == '_':
            token += self.chompChar()
        self.issue(token)
        
    def chompInt(self):
        ck = self.nxt().isdigit()
        self.lexassert(ck)
        token = ""
        token += self.chompChar()     # first digit
        while self.nxt().isdigit():
            token += self.chompChar() # remaining digits=
        self.issue(token)
        
    def chompString(self):
        self.lexassert(self.nxt() == '"')
        self.chompChar() # eat quote
        token = ""
        while self.nxt() != '' and self.nxt() != '"':
            if self.nxt() == '\\':
                self.chompChar()
                if self.nxt() == '\n':
                    self.chompWhitespace(True)
                elif self.nxt() == '\\':
                    token += self.chompChar()
                elif self.nxt() == 'n':
                    self.chompChar()
                    token += '\n'
                elif self.nxt() == 't':
                    self.chompChar()
                    token += '\t'
                elif self.nxt() == '"': 
                    self.chompChar()
                    token += '"'
                else:
                    self.raiseLex("Bad string escape character")
            elif self.nxt() == '\n':
                self.raiseLex("End of line encountered within string")
            elif self.nxt() == '\t':
                self.raiseLex("Tab encountered within string")
            else:
                token += self.chompChar()

        if self.nxt() == '':
            self.raiseLex("EOF encountered within string")
        else:
            self.chompChar() # eat endquote
            self.issue('"'+token+'"')

    def chompComment(self):
        self.lexassert(len(self.source)>1 and self.source[0:1] == '(*')
        self.chompChar() # eat (*
        self.chompChar() #
        while len(self.source) >= 2 and self.source[0:1] != '*)':        
            self.chomp()
        if len(self.source) < 2:
            self.raiseLex("EOF encountered within comment")
        else:
            self.chompChar() # eat *)
            self.chompChar() #     

    def chomp(self):
        if self.nxt() in "\n\t\r ":
            self.chompWhitespace()
        else:
            self.chompChar()

    def chompChar(self):
        self.lexassert(len(self.source) > 0)
        c = self.source[0]
        self.source = self.source[1:]
        self.column += 1
        return c

    def chompWhitespace(self,withinToken=False):
        self.lexassert(len(self.source) > 0)
        c = self.source[0]
        self.source = self.source[1:]
        if c == ' ':
            self.column += 1
        elif c == '\t':
            self.column += 4
        elif c == '\n':
            self.line += 1
            self.column = 1
        if not withinToken:
            self.markIssue()
        
    def chompOperator(self):
        token = ''
        while self.nxt() in OPERATORS:
            token += self.chompChar()
        self.issue(token)

    #
    # TOKENIZER
    #
    # This method defines the main loop of the
    # lexical analysis algorithm, one that converts
    # the source text into a list of token strings.

    def analyze(self):
        while self.source != '':
            # CHOMP a string literal
            if self.source[0] == '"':
                self.chompString()
            # CHOMP a comment
            elif self.source[0:1] == '(*':
                self.chompComment()
            # CHOMP whitespace
            elif self.source[0] in ' \t\n\r':
                self.chompWhitespace()
            # CHOMP an integer literal
            elif self.source[0].isdigit():
                self.chompInt()
            # CHOMP a single "delimiter" character
            elif self.source[0] in DELIMITERS:
                self.issue(self.chompChar())
            # CHOMP an operator               
            elif self.source[0] in OPERATORS:
                self.chompOperator()
            # CHOMP a reserved word or a name.
            else:
                self.chompWord()

def evalAll(files):
    try:
        # Load definitions from the specified source files.
        for fname in files:
            print("[opening "+fname+"]")
            f = open(fname,"r")
            src = f.read()
            tks = TokenStream(src,filename=fname)
            interpret(tks)
    except RunTimeError as e:
        print("Error during evaluation.")
        print(e.args[0])
        print("Bailing command-line loading.")
    except RunTimeError as e:
        print("Type error during evaluation.")
        print(e.args[0])
        print("Bailing command-line loading.")
    except SyntaxError as e:
        print("Syntax error during parse.")
        print(e.args[0])
        print("Bailing command-line loading.")
    except ParseError as e:
        print("Failed to consume all the input in the parse.")
        print(e.args[0])
        print("Bailing command-line loading.")
    except LexError as e:
        print("Bad token reached.")
        print(e.args[0])
        print("Bailing command-line loading.")

#
#  usage #1: 
#    python3 miniml.py
#
#      - Waits for a MiniML expression after the prompt
#        evaluates it, and prints the resulting value
#
#
#  usage #2: 
#    python3 miniml.py <file 1> ... <file n>
#
#      - this runs the interpreter on each of the listed
#        source .mml files
#
mtime = str(time.ctime(os.path.getmtime("./parser.py")))
print("LambdaCalc++ of Portlandia v2021F.1 [built: "+mtime+"]")
if len(sys.argv) > 1:
    evalAll(sys.argv[1:])
else:
    print("Enter an expression:")
    interpret(TokenStream(input()))

