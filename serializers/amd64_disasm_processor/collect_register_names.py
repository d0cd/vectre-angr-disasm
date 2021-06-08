from lark import Visitor


class CollectRegisterNames(Visitor):
    reg_names = set()

    def id(self, args):
        self.reg_names.add(args.children[0].value)