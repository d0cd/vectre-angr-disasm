
from lark import Lark


class AArch64DisassemblyProcessor:

    def __init__(self):
        self.arm_bb_parser = Lark.open('aarch64_disasm_block.lark', rel_to=__file__, parser='lalr', start="block")

    def parse_bb_str(self, bb_str):
        print(bb_str)
        tree = self.arm_bb_parser.parse(bb_str)
        return tree
