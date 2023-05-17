import re
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter
import graphviz
import distutils.spawn

tree = None

class Lexer:
    def __init__(self):
        pass

    def matchKeywords(self, line):
        return re.search(r'^\s*(if|else|int|float)', line)
    
    def matchOperators(self, line):
        return re.search(r'^\s*(=|\+|>|<|\*)', line)

    def matchSeparators(self, line):
        return re.search(r'^\s*(\(|\)|:|"|;)', line)

    def matchIdentifiers(self, line):
        return re.search(r'^\s*([a-zA-Z_]+\w*)', line)

    def matchInt(self, line):
        return re.search(r'^\s*(\d+)(?!\.)', line)

    def matchFloat(self, line):
        return re.search(r'^\s*(\d+\.\d+)', line)

    def matchString(self, line):
        return re.search(r'^\s*(\".*?\")', line)

    def cutOneLine(self, line):
        pairs = list()
        while len(line):
            if match := self.matchKeywords(line):
                pairs.append(("keyword", match.group(1)))
                line = line[match.end(0):]
            elif match := self.matchString(line):
                pairs.append(("string_literal", match.group(1)))
                line = line[match.end(0):]
            elif match := self.matchOperators(line):
                pairs.append(("operator", match.group(1)))
                line = line[match.end(0):]
            elif match := self.matchSeparators(line):
                pairs.append(("seperator", match.group(1)))
                line = line[match.end(0):]
            elif match := self.matchIdentifiers(line):
                pairs.append(("identifier", match.group(1)))
                line = line[match.end(0):]
            elif match := self.matchFloat(line):
                pairs.append(("float_literal", match.group(1)))
                line = line[match.end(0):]
            elif match := self.matchInt(line):
                pairs.append(("int_literal", match.group(1)))
                line = line[match.end(0):]
            else:
                return "ERROR"
                break
        return pairs

class Parser:
    def __init__(self):
        self.currentNode = 0
        self.nextNode = 1
        self.inToken = tuple()
    
    def parse(self, tokens):
        global tree
        self.output = str()
        self.tokens = tokens
        self.inToken = self.tokens.pop(0)
        if self.inToken[0] == "keyword" and self.tokens[0][0] == "identifier" and self.tokens[1][0] == "operator":
            self.output += self.exp()
        elif self.inToken[0] == "keyword" and self.inToken[1] == "if":
            self.output += self.if_exp()
        elif self.inToken[1] == "print":
            self.output += self.print_call()
        else:
            return "Error! unable to parse line"

        if self.inToken[1] not in [";", ":"]:
            self.output += "Error, statement not closed!\n"
        return self.output

    def exp(self):
        global tree
        tree.node(str(self.currentNode), "Expression")
        output = str()
        output += "----parent node exp, finding children nodes:"
        typeT,token = self.inToken
        if typeT=="keyword" and token in ["float", "int"]:
            output += "child node (internal): keyword/type"
            output += "\tidentifier has child node (token):"+token

            tree.node(str(self.nextNode), token)
            tree.edge(str(self.currentNode), str(self.nextNode))
            self.nextNode += 1

            self.accept_token()
        else:
            print("expect a valid type in expression!\n")
            return
        
        typeT,token = self.inToken
        if typeT=="identifier":
            output += "child node (internal): identifier\n"
            output += "\tidentifier has child node (token):"+token+"\n"
            
            tree.node(str(self.nextNode), token)
            tree.edge(str(self.currentNode), str(self.nextNode))
            self.nextNode += 1

            self.accept_token()
        else:
            print("expect identifier as the second element of the expression!\n")
            return

        if(self.inToken[1]=="="):
            output += "child node (token):"+self.inToken[1]+"\n"

            tree.node(str(self.nextNode), '=')
            tree.edge(str(self.currentNode), str(self.nextNode))
            self.nextNode += 1

            self.accept_token()
        else:
            print("expect = as the second element of the expression!")
            return
        
        tree.edge(str(self.currentNode), str(self.nextNode))
        self.currentNode = self.nextNode
        self.nextNode += 1

        output += "Child node (internal): math"
        output += self.math().replace("\n", "\n\t")
        return output

    def if_exp(self):
        global tree
        tree.node(str(self.currentNode), "If Expression")
        output = str()
        output += "----parent node if_exp, finding children nodes:\n"
        if self.inToken[1] == "if":
            output += "child node (internal): " + self.inToken[0] + "\n"
            output += "\t"+self.inToken[0]+" has child node (token):"+self.inToken[1]+"\n"
            self.accept_token()
        else:
            print("error, if_exp expects if")

        if self.inToken[1] != "(":
            print("error, if_exp needs a (")
        self.accept_token()

        tree.edge(str(self.currentNode), str(self.nextNode))
        self.currentNode = self.nextNode
        self.nextNode += 1

        output += self.comparison_exp()
            
        if self.inToken[1] != ")":
            print("error, if_exp needs a )")
        self.accept_token()

        return output

    def comparison_exp(self):
        global tree
        tree.node(str(self.currentNode), "Comparison Expression")
        output = str()
        output += "----parent node comparison_exp, finding children nodes:\n"

        if self.inToken[0] == "identifier":
            output += "child node (internal): " + self.inToken[0] + "\n"
            output += "\t"+self.inToken[0]+" has child node (token):"+self.inToken[1]+"\n"

            tree.node(str(self.nextNode), self.inToken[1])
            tree.edge(str(self.currentNode), str(self.nextNode))
            self.nextNode += 1

            self.accept_token()
        else:
            print("error, comparison expects identifier")

        if self.inToken[1] in [">", "<"]:
            output += "child node (token):"+self.inToken[1]+"\n"

            tree.node(str(self.nextNode), self.inToken[1])
            tree.edge(str(self.currentNode), str(self.nextNode))
            self.nextNode += 1

            self.accept_token()

            output += "child node (internal): comparison_exp\n"
            output += self.comparison_exp().replace("\n", "\n\t")

        return output

    def print_call(self):
        global tree
        tree.node(str(self.currentNode), "Print Call")
        output = str()
        output += "----parent node print_call, finding children nodes:\n"
        if self.inToken[1] != "print":
            return "ERROR! Print call must start with print"
        self.accept_token()

        if self.inToken[1] != "(":
            return "ERROR! if_exp needs a ("
        self.accept_token()

        if self.inToken[0] == "string_literal":
            output += "child node (internal): " + self.inToken[0] + "\n"
            output += "\t"+self.inToken[0]+" has child node (token):"+self.inToken[1]+"\n"

            tree.node(str(self.nextNode), self.inToken[1])
            tree.edge(str(self.currentNode), str(self.nextNode))
            self.nextNode += 1

            self.accept_token()
        else:
            return "error, print expects string literal"

        if self.inToken[1] != ")":
            return "error, if_exp needs a )"
        self.accept_token()

        return output

    def math(self):
        global tree
        tree.node(str(self.currentNode), "Math Expression")
        output = str()
        output += "----parent node math, finding children nodes:\n"

        if self.inToken[0] in ["int_literal", "float_literal"]:
            output += "child node (internal): " + self.inToken[0] + "\n"
            output += "\t"+self.inToken[0]+" has child node (token):"+self.inToken[1]+"\n"

            tree.node(str(self.nextNode), self.inToken[1])
            tree.edge(str(self.currentNode), str(self.nextNode))
            self.nextNode += 1

            self.accept_token()
        else:
            print("error, math expects float or int")

        if self.inToken[1] in ["+", "*"]:
            output += "child node (token):"+self.inToken[1]+"\n"

            tree.node(str(self.nextNode), self.inToken[1])
            tree.edge(str(self.currentNode), str(self.nextNode))
            self.nextNode += 1

            self.accept_token()

            output += "child node (internal): math\n"
            output += self.math().replace("\n", "\n\t")

        return output

    def accept_token(self):
        #print("     accept token from the list:"+self.inToken[1])
        try:
            self.inToken=self.tokens.pop(0)
        except IndexError:
            self.output += "Error! Unexpected end of line"

class LexerGUI:
    def __init__(self, root):
        self.root = root
        self.lexer = Lexer()
        self.parser = Parser()
        self.tokenList = list()
        self.root.title("LexerGUI")
        self.master = ttk.Frame(root, padding="3 3 12 12")
        self.master.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.currentline = 0

        self.textframe = ttk.Frame(self.master, padding="3 3 3 3")
        self.textframe.grid(column=0, row=0, sticky=N)

        self.inputboxlabel = Label(self.textframe, text="Source Code Input:", padx=2, pady=2)
        self.inputboxlabel.grid(column=0, row=0, sticky=W)
        
        self.lexerroutputlabel = Label(self.textframe, text="Lexical Analyzed Result:", padx=2, pady=2)
        self.lexerroutputlabel.grid(column=1, row=0, sticky=W)

        self.parseroutputlabel = Label(self.textframe, text="Parse Tree:", padx=2, pady=2)
        self.parseroutputlabel.grid(column=2, row=0, sticky=W)

        self.inputbox = Text(self.textframe, height=20, width=60, wrap="none", padx=5, pady=5)
        self.inputbox.grid(column=0, row=1, sticky=E)

        self.lexeroutput = Text(self.textframe, height=20, width=20, wrap="none", padx=5, pady=5)
        self.lexeroutput.grid(column=1, row=1, sticky=E)

        self.parseroutput = Text(self.textframe, height=20, width=60, wrap="none", padx=5, pady=5)
        self.parseroutput.grid(column=2, row=1, sticky=E)

        self.treeoutput = Canvas(self.master, height=350, width=1000)
        self.treeoutput.grid(column=0, row=1, sticky=N)

        self.linelabel = Label(self.master, text="Current Line: 0", padx=2, pady=2)
        self.linelabel.grid(column=0, row=3, sticky=W)

        self.advancebutton = Button(self.master, command=self.advance, text="Next Line", padx=1, pady=1)
        self.advancebutton.grid(column=0, row=4, sticky=E)

        self.quitbutton = Button(self.master, command=self.root.destroy, text="Quit", padx=1, pady=1)
        self.quitbutton.grid(column=2, row=4, sticky=E)

        self.resetbutton = Button(self.master, command=self.reset, text="Reset", padx=1, pady=1)
        self.resetbutton.grid(column=2, row=4, sticky=E)

    def formatTuple(self, tuple):
        return "<" + tuple[0] + ", " + tuple[1] + ">"

    def advance(self):
        global tree
        self.currentline += 1
        tree = graphviz.Digraph('Expression')
        #tree.node("0", "Parse Tree")
        input = self.inputbox.get(str(self.currentline) + ".0", str(self.currentline)+".end")
        lexedLine = self.lexer.cutOneLine(input)
        self.tokenList += lexedLine # full token list
        self.lexeroutput.insert(END, "\n".join(map(self.formatTuple, lexedLine))+"\n")

        parsedLine = self.parser.parse(lexedLine) # process one line of tokens
        
        self.parseroutput.insert(END, "###PARSE TREE FOR LINE "+str(self.currentline)+"###\n")
        self.parseroutput.insert(END, parsedLine+"\n")

        self.linelabel.config(text="Current Line: " + str(self.currentline))

        self.currentimage = PhotoImage(data=tree.pipe(format='png'))

        self.treeoutput.create_image(500,0, image=self.currentimage, anchor=N)

    def reset(self):
        self.currentline = 0
        self.linelabel.config(text="Current Line: " + str(self.currentline))
        self.lexeroutput.delete("1.0", END)
        self.parseroutput.delete("1.0", END)

if __name__ == '__main__':   
    root = Tk()
    if distutils.spawn.find_executable('dot.exe') == None:
        tkinter.messagebox.showerror(parent=root, title="error", message="You must install Graphviz and add it to your PATH")
    lexergui = LexerGUI(root)
    root.mainloop()
