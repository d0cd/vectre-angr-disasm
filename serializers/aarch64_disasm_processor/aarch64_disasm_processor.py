
from lark import Lark

from .remove_trip_arr import RemoveTripleArrays
from .rename_instructions import RenameInstructions
from .vectre_serializer import VectreSerializer

"""
Processing Logic:
1. Append tags to instruction names denoting the types of arguments they take. Normalize complex addressing modes
2. Serialize into Vectre string
"""

class AArch64DisassemblyProcessor:

    def __init__(self):
        self.arm_bb_parser = Lark.open('aarch64_disasm_block.lark', rel_to=__file__, parser='lalr', start="block")

    def serialize_basic_block(self, bb_str):
        tree = self.arm_bb_parser.parse(bb_str)
        RenameInstructions().transform(tree)
        cleaned = RemoveTripleArrays().transform(tree)
        serialized = VectreSerializer().transform(cleaned)
        return serialized




