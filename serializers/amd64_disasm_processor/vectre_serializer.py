from lark import Transformer, Tree
from string import Template


class VectreSerializer(Transformer):
    def block(self, args):
        return "\n".join(args)

    def line(self, args):
        assert len(args) == 2 or len(args) == 3
        addr = args[0]
        op = args[1]
        operands = f" {args[2]}" if len(args) == 3 else ""
        line_template = Template("    $ADDR: $OP$OPERANDS;")
        return line_template.substitute(ADDR=addr, OP=op, OPERANDS=operands)

    def addr(self, args):
        return args[0].value

    def op(self, args):
        return args[0].value

    def operands(self, operands):
        return ', '.join(operands)

    def ptr(self, args):
        return args[1]

    def expr(self, args):
        return " ".join(args)

    def operator(self, args):
        return args[0].value

    def number(self, args):
        return args[0].value

    def id(self, args):
        return args[0].value

