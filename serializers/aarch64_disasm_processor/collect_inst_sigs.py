from lark import Visitor


class CollectInstructionNames(Visitor):
    inst_info = set()

    def reg(self, args):
        self.inst_info.add(args.children[0].value)