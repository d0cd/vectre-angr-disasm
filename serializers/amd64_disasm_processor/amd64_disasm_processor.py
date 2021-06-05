
from lark import Lark

from .rename_instructions import RenameInstructions
from .vectre_serializer import VectreSerializer


class AMD64DisassemblyProcessor:

    def __init__(self):
        self.arm_bb_parser = Lark.open('amd64_disasm_block.lark', rel_to=__file__, parser='lalr', start="block")

    def serialize_basic_block(self, bb_str):
        tree = self.arm_bb_parser.parse(bb_str)
        RenameInstructions().transform(tree)
        serialized = VectreSerializer().transform(tree)
        return serialized

    def generate_inst_def_skeleton(self, inst_str):
        pass

    def generate_platform_def_skeleton(self, inst_str):
        pass
