from lark import Transformer, Tree

import re


class NormalizeConditionalInstructions(Transformer):

    def line(self, args):
        assert len(args) == 2 or len(args) == 3, f"Malformed line: {args}"
        op = args[1]

        if op.children[0].value == 'cset':
            operands = args[2]
            assert len(operands.children) == 2, "Unexpected number of operands for cset"
            condition = operands.children[1].children[0].value
            operands.children = operands.children[:1]
            op.children[0].value = f"{op.children[0].value}_{condition}"
        elif op.children[0].value == 'tbnz':
            operands = args[2]
            assert len(operands.children) == 3, "Unexpected number of operands for tbnz"
            bit_index = operands.children[1].children[0].value
            op.children[0].value = op.children[0].value + f"_{bit_index}"
            operands.children = [operands.children[0], operands.children[2]]
        return Tree("line", args)






