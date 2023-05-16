from tkinter import *
import re

root = Tk()
num = 0

parserTok = []
inToken = ("empty", "empty")


# parse


def print_exp():
    global inToken
    typeT, token = inToken
    if (inToken[1] == ";"):
        parse.insert(END, "child node (token):" + inToken[1] + "\n")
        parse.insert(END, " accept token form the list:" + inToken[1] + "\n")
        return
    if (token == "print"):
        parse.insert(END, "\nchild node (internal): keyword")
        parse.insert(END, " keyword has child node (token):" + inToken[1] + "\n")
        accept_token()
    if (inToken[0] == "sep"):
        parse.insert(END, "child node (internal): separator")
        parse.insert(END, " separator has child node (token):" + inToken[1] + "\n")
        accept_token()
        print_exp()
    if (inToken[0] == 'id'):
        parse.insert(END, "child node (internal): identifier")
        parse.insert(END, " identifier has child node (token):" + inToken[1] + "\n")
        accept_token()
        print_exp()


def accept_token():
    global inToken
    parse.insert(END, "    accept token from the list:" + inToken[1] + "\n")
    inToken = parserTok.pop(0)


def mult():
    parse.insert(END, "\n----parent node mult, finding children nodes: " + "\n")
    global inToken
    if (inToken[0] == "float"):
        parse.insert(END, "child node (internal): float" + "\n")
        parse.insert(END, " float has child node (token): " + inToken[1] + "\n")
        accept_token()

    elif (inToken[0] == "int"):
        parse.insert(END, "child node (internal): int" + "\n")
        parse.insert(END, " int has child node (token): " + inToken[1] + "\n")
        accept_token()

        if (inToken[1] == "*"):
            parse.insert(END, "child node (token): " + inToken[1])
            accept_token()

            parse.insert(END, "child node (internal): mulit")
            mult()


def math():
    global inToken
    parse.insert(END, "\n----parent node math, finding children nodes:" + "\n")
    # parse.insert(END,"child node (internal): mult"+"\n")
    mult()
    if (inToken[1] == "+"):
        parse.insert(END, "child node (internal): +" + "\n")
        accept_token()
    mult()


def exp():
    parse.insert(END, "\n----parent node exp, finding children nodes:" + "\n")
    global inToken
    typeT, token = inToken
    if (inToken[0] == "keyword"):
        parse.insert(END, "child node (internal): keyword" + "\n")
        parse.insert(END, " keyword has child node (token):" + inToken[1] + "\n")
        accept_token()
    else:
        parse.insert(END, "expect keyword as the first element of the expression!\n" + "\n")
        return

    if (inToken[0] == "id"):
        parse.insert(END, "child node (internal): identifier" + "\n")
        parse.insert(END, " identifier has child node (token):" + inToken[1] + "\n")
        accept_token()
    else:
        parse.insert(END, "expect identifier as the first element of the expression!\n" + "\n")
        return

    if (inToken[1] == "="):
        parse.insert(END, "child node (token): " + inToken[1] + "\n")
        accept_token()
    else:
        parse.insert(END, "expect = as the third element of the expression!" + "\n")
        return

    parse.insert(END, "child node (internal): math" + "\n")
    math()


def comparison_exp():
    global inToken
    if (inToken[0] == "id"):
        parse.insert(END, "child node (internal): id" + 'n')
        parse.insert(END, " child node (token):" + inToken[1] + "\n")
        accept_token()
        comparison_exp()
    if (inToken[0] == "op"):
        parse.insert(END, "child node (internal): op\n")
        parse.insert(END, " fchild node (token):" + inToken[1] + "\n")
        accept_token()
        comparison_exp()


def exp2():
    parse.insert(END, "\nparent node if_exp, finding children nodes:\n")
    global inToken
    typeT, token = inToken
    if (token == "if"):
        parse.insert(END, "child node (internal): keyword\n")
        parse.insert(END, " char has child node (token): " + token + "\n")
        accept_token()

    if (token == "("):
        parse.insert(END, "child node (token): " + inToken[1])
        accept_token()

    parse.insert(END, "child node (internal): comparison_exp\n")
    parse.insert(END, "\n----parent node comparison_exp, finding children nodes:\n")
    comparison_exp()

    parse.insert(END, "\n----parent node if_exp, finding children nodes:\n")
    if (inToken[1] == ")"):
        parse.insert(END, "child node (token): " + inToken[1] + "\n")
        accept_token()


def if_exp():
    global inToken
    if not parserTok:
        return
    else:
        inToken = parserTok.pop(0)
        exp2()
    return


def parser():
    global inToken
    # global parserTok
    inToken = parserTok.pop(0)
    typeT, token = inToken
    if (token == "if"):
        if_exp()
        if (inToken[1] == ":"):
            parse.insert(END, "\nparse tree building sucess!\n")
    elif (token == "print"):
        print_exp()
        parse.insert(END, "\nparse tree building sucess!\n")
    else:
        exp()
        if (inToken[1] == ";"):
            parse.insert(END, "\nparse tree building success!\n" )


def next_line():
    global num
    global parserTok
    # parserTok = []
    # global parser
    # Getting the text from the input side
    # "1.0" means that the input should be read from line one, character zero, second paramter is till end of line
    #output.delete("0.0", END)
    #parse.delete("0.0", END)
    #str = Input.get('1.0', END)
    str = Input.get("1.0", END).split("\n")
    stringlex = str[num]


    if num == len(str) - 1:
        exit()
    # cleaning the current line text box
    keyword = re.compile("if|else|int|float")
    operator = re.compile("=|\+|>|\*")
    separator = re.compile("\(|\)|:|\"|;")
    identifier = re.compile("[a-zA-Z]+[0-9]*")
    float = re.compile("^[0-9]+\.[0-9]+")
    int = re.compile("\d+")
    string = re.compile("\".+\"")
    i = 0
    # global parserTok
    # Loop until the string is empty
    ####Parse tree
    count = i + 1;
    parse.insert(END, "\n###PARSE TREE for line ")
    parse.insert(END, num + 1)
    parse.insert(END, "###\n")

    while stringlex:

        # Check for float
        Float = float.match(stringlex)
        if Float:
            token = stringlex[Float.start():Float.end()]
            output.insert(END, ("<float_literal," + token + ">\n\n"))
            parserTok.append(tuple(("float", token)))
            stringlex = stringlex[len(token):].strip()
            continue
        # Check for keywords
        Keyword = keyword.match(stringlex)
        if Keyword:
            token = stringlex[Keyword.start():Keyword.end()]
            output.insert(END, ("<keyword," + token + ">\n\n"))
            parserTok.append(tuple(("keyword", token)))
            # cut substring to find next token
            stringlex = stringlex[len(token):].strip()
            continue
        # Check for operators
        Operator = operator.match(stringlex)
        if Operator:
            token = stringlex[Operator.start():Operator.end()]
            output.insert(END, ("<operator," + token + ">\n\n"))
            parserTok.append(tuple(("op", token)))
            stringlex = stringlex[len(token):].strip()
            continue
        # Check for separators
        Separator = separator.match(stringlex)
        if Separator:
            token = stringlex[Separator.start():Separator.end()]
            output.insert(END, ("<seperator," + token + ">\n\n"))
            parserTok.append(tuple(("sep", token)))
            stringlex = stringlex[len(token):].strip()
            continue
        # Check for identifiers
        Identifier = identifier.match(stringlex)
        if Identifier:
            token = stringlex[Identifier.start():Identifier.end()]
            output.insert(END, ("<identifier," + token + ">\n\n"))
            parserTok.append(tuple(("id", token)))
            stringlex = stringlex[len(token):].strip()
            continue
        # Check for int
        Int = int.match(stringlex)
        if Int:
            token = stringlex[Int.start():Int.end()]
            output.insert(END, ("<int_literal," + token + ">\n\n"))
            parserTok.append(tuple(("int", token)))
            stringlex = stringlex[len(token):].strip()
            continue
        # Check for string
        String = string.match(stringlex)
        if String:
            token = stringlex[String.start():String.end()]
            output.insert(END, ("<string_literal," + token + ">\n\n"))
            parserTok.append(tuple(("str", token)))
            stringlex = stringlex[len(token):].strip()

        #stringlex += 1


    processing_line.delete(0, END)

    # inserting the next line output side
    processing_line.insert(END, num + 1)
    num += 1
    parser()


# closes program
def Exit():
    root.quit()


# size of page
title = root.title("My Title")
root.title("Lexical Analyzer for TinyPie")
size = Canvas(root, height=800, width=1650)
size.pack()

# source code input box
label_1 = Label(root, text='Source Code Input:')
label_1.place(x=50, y=50)
leftbox = LabelFrame(root, height=400, width=400, bg="yellow")
leftbox.place(relx=0.1, rely=0.1, x=-50)
Input = Text(leftbox)
Input.place(relwidth=1, relheight=1)

# current processing line box
label_2 = Label(root, text='Current Processing Line:')
label_2.place(x=40, y=500)
processing_line = Entry(root)
# processing_line.size()
processing_line.place(x=200, y=500)
ip_next_button = Button(root, text='NextLine', bg="light blue", command=next_line)
ip_next_button.place(x=200, y=530)

# Lexical Analyzed result box
rightbox = LabelFrame(root, height=400, width=400, bg="yellow")
rightbox.place(relx=0.1, rely=0.1, x=400, y=200, anchor='w')
output = Text(rightbox)
output.place(relwidth=1, relheight=1)
Label_3 = Label(root, text='Lexical Analysed Result:')
Label_3.place(x=500, y=50)

# parser box
Label_4 = Label(root, text='PARSER:')
Label_4.place(x=1000, y=50)
parserbox = LabelFrame(root, height=400, width=480, bg="yellow")
parserbox.place(relx=0.1, rely=0.1, x=850, y=200, anchor='w')
parse = Text(parserbox)
parse.place(relwidth=1, relheight=1)

# exit
next_button = Button(root, text='Quit', bg="light blue", command=Exit)
next_button.place(x=1100, y=520)

root.mainloop()