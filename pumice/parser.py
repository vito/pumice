import py
import sys

from pypy.rlib.parsing.ebnfparse import parse_ebnf, make_parse_function
from pypy.rlib.parsing.parsing import ParseError, Rule
from pypy.rlib.parsing.tree import RPythonVisitor, Symbol, Nonterminal

from pumice.values import *

sys.setrecursionlimit(10000)

GFILE = py.path.local(__file__).dirpath().join('grammar.txt')

try:
    t = GFILE.read(mode='U')
    regexs, rules, ToAST = parse_ebnf(t)
except ParseError,e:
    print e.nice_error_message(filename=str(GFILE),source=t)
    raise

parsef = make_parse_function(regexs, rules, eof=True)

def parse(code, sourcename = "(eval)"):
    t = parsef(code)
    return ASTBuilder(sourcename).dispatch(ToAST().transform(t))


class ASTBuilder(RPythonVisitor):
    def __init__(self, sourcename):
        self.sourcename = sourcename

    def visit_program(self, node):
        return self.dispatch(node.children[0])

    def visit_sexps(self, node):
        return VTree([self.dispatch(c) for c in node.children])

    def visit_number(self, node):
        sym = node.children[0]
        if sym.symbol == 'DECINTEGERLITERAL':
            return VNumber(int(sym.additional_info))
        elif sym.symbol == 'HEXINTEGERLITERAL':
            return VNumber(int(sym.additional_info, 16))
        elif sym.symbol == 'OCTINTEGERLITERAL':
            return VNumber(int(sym.additional_info, 8))
        else:
            # should be impossible
            return VNumber(0)

    def visit_string(self, node):
        sym = node.children[0]
        return VString(_parse_string(sym.additional_info))

    def visit_constant(self, node):
        sym = node.children[0]
        if sym.symbol == 'CTRUE':
            return VTrue()
        elif sym.symbol == 'CFALSE':
            return VFalse()
        elif sym.symbol == 'CIGNORE':
            return VIgnore()
        elif sym.symbol == 'CINERT':
            return VInert()
        else:
            # should be impossible
            return VIgnore()

    def visit_symbol(self, node):
        return VSymbol(node.children[0].additional_info)

    def visit_list(self, node):
        if node.children:
            return self.dispatch(node.children[0])
        else:
            return VNull()

    def visit_pair(self, node):
        if len(node.children) == 2:
            return VPair(self.dispatch(node.children[0]), self.dispatch(node.children[1]))
        elif len(node.children) == 1:
            return VPair(self.dispatch(node.children[0]), VNull())
        else:
            # should be impossible
            return VNull()


Escapes = {
    "n": "\n",
    "s": " ",
    "r": "\r",
    "t": "\t",
    "v": "\v",
    "f": "\f",
    "b": "\b",
    "a": "\a",
    "e": "\033",
    "\\": "\\",
    "\"": "\"",
    "BS": "\b",
    "HT": "\t",
    "LF": "\n",
    "VT": "\v",
    "FF": "\f",
    "CR": "\r",
    "SO": "\016",
    "SI": "\017",
    "EM": "\031",
    "FS": "\034",
    "GS": "\035",
    "RS": "\036",
    "US": "\037",
    "SP": " ",
    "NUL": "\000",
    "SOH": "\001",
    "STX": "\002",
    "ETX": "\003",
    "EOT": "\004",
    "ENQ": "\005",
    "ACK": "\006",
    "BEL": "\a",
    "DLE": "\020",
    "DC1": "\021",
    "DC2": "\022",
    "DC3": "\023",
    "DC4": "\024",
    "NAK": "\025",
    "SYN": "\026",
    "ETB": "\027",
    "CAN": "\030",
    "SUB": "\032",
    "ESC": "\033",
    "DEL": "\177",
}

def _parse_string(str):
    strs = []

    pos = 1
    last = len(str) - 1
    while pos < last:
        ch = str[pos]
        if ch == '\\':
            pos += 1
            for x in range(1, 4):
                esc = str[pos:pos+x]
                if esc in Escapes:
                    strs.append(Escapes[esc])
                    pos += x
                    break
        else:
            strs.append(ch)
            pos += 1

    return ''.join(strs)
