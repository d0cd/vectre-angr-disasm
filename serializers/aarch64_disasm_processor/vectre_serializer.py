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

    def operands(self, operands):
        return ', '.join(operands)

    def addr(self, args):
        return args[0].replace("bv64", "")

    def op(self, args):
        return args[0].value

    def reg(self, args):
        return args[0].value

    def number(self, args):
        return args[0]

    def HEX_NUMBER(self, args):
        return f"{args}bv64"

    def DEC_NUMBER(self, args):
        return args

    def arr(self, args):
        arr_args = args[0].children[0].children
        return f"({', '.join(arr_args)})"
