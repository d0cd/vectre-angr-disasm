
from lark import Lark

from .collect_inst_sigs import CollectInstructionNames
from .remove_trip_arr import RemoveTripleArrays
from .rename_instructions import RenameInstructions
from .vectre_serializer import VectreSerializer

from ..templates import inst_def_template

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

    def generate_inst_def_skeleton(self, inst_str):
        tree = self.arm_bb_parser.parse(inst_str)
        RenameInstructions().transform(tree)
        cleaned = RemoveTripleArrays().transform(tree)

        collector = CollectInstructionNames()
        collector.visit(cleaned)

        inst_specs = []
        for inst in collector.inst_info:
            params = []
            arg_types = inst.split("__")[1:]
            for (i, typ) in enumerate(arg_types):
                if typ == "r":
                    params.append(f"arg{i}: reg_index_t")
                elif typ == "n":
                    params.append(f"arg{i}: word_t")
                elif typ[0] == "t":
                    num_elems = int(typ[2])
                    assert num_elems > 0
                    tup_typs = typ[4:3 + num_elems * 2].split("_")
                    tup_typ_strs = []
                    for t in tup_typs:
                        if t == 'r':
                            tup_typ_strs.append("reg_index_t")
                        elif t == 'n':
                            tup_typ_strs.append("word_t")
                        else:
                            raise Exception(f"Unknown tuple type: {t}")
                    params.append(f"arg{i}: {{{', '.join(tup_typ_strs)}}}")
            arg_sig = ", ".join(params)
            inst_specs.append(inst_def_template.substitute(INST_NAME=inst, ARG_SIG=arg_sig))

        return "\n\n".join(inst_specs)

    def generate_platform_def_skeleton(self, inst_str):
        pass


