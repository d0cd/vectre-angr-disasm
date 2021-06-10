from lark import Visitor


class CollectInstructionNames(Visitor):
    inst_info = set()

    def line(self, args):
        self.inst_info.add(args.children[1].children[0].value)
