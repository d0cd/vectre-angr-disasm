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
        return Tree("line", args)






