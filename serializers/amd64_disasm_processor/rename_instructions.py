from lark import Transformer, Tree


class RenameInstructions(Transformer):
    """
    Renames instructions to contain name and operand tags.
    Tags are of the form e (denoting an expression), or p (denoting a pointer)
    """

    def line(self, args):
        assert len(args) == 2 or len(args) == 3, f"Malformed line: {args}"
        op = args[1]

        # If the instruction has operands transform it
        if len(args) == 3:
            operands = args[2].children
            tag = ""
            for operand in operands:
                if operand.data == 'expr':
                    tag += "__w"
                elif operand.data == 'term':
                    tag += "__w"
                elif operand.data == 'number':
                    tag += "__w"
                elif operand.data == 'id':
                    tag += "__r"
                elif operand.data == 'ptr':
                    width = operand.children[0].children[0].value
                    tag += f"__p_{width}"
                else:
                    raise Exception(f"Unknown operand type: {operand.data}")
            op.children[0].value += tag
            op.children[0].value = op.children[0].value.replace(".", "_")





