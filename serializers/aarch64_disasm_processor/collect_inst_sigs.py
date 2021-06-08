from lark import Visitor


class CollectInstructionNames(Visitor):
    inst_info = set()

    def reg(self, args):
        print(args)
        self.inst_info.add(args.children[1].children[0].value)