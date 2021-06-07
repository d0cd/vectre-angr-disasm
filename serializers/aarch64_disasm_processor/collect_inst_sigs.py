from lark import Visitor


class CollectInstructionSignatures(Visitor):
    inst_info = {}

    def line(self, args):
        print(args)