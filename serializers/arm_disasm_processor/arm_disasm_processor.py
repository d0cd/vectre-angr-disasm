
from lark import Lark


class ArmDisassemblyProcessor:

    def __init__(self):
        self.arm_bb_parser = Lark.open('./disasm_block.lark', rel_to=__file__, parser='lalr', start="block")

    def parse_bb_str(self, bb_str):
        print(bb_str)
        return self.arm_bb_parser.parse(bb_str)
