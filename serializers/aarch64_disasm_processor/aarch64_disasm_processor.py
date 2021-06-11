
from lark import Lark

from .collect_inst_sigs import CollectInstructionNames
from .collect_register_names import CollectRegisterNames
from .normalize_conditional_instructions import NormalizeConditionalInstructions
from .remove_trip_arr import RemoveTripleArrays
from .rename_instructions import RenameInstructions
from .vectre_serializer import VectreSerializer

from ..templates import inst_def_template, platform_def_template

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
        normalized = NormalizeConditionalInstructions().transform(tree)
        RenameInstructions().transform(normalized)
        cleaned = RemoveTripleArrays().transform(normalized)
        serialized = VectreSerializer().transform(cleaned)
        return serialized

    def generate_inst_def_skeleton(self, inst_str):
        tree = self.arm_bb_parser.parse(inst_str)
        normalized = NormalizeConditionalInstructions().transform(tree)
        RenameInstructions().transform(normalized)
        cleaned = RemoveTripleArrays().transform(normalized)

        collector = CollectInstructionNames()
        collector.visit(cleaned)

        inst_specs = []
        for inst in sorted(collector.inst_info):
            params = []
            arg_types = inst.split("__")[1:]
            for (i, typ) in enumerate(arg_types):
                if typ[0] == "r":
                    params.append(f"arg{i}: bv64")
                elif typ[0] == "n":
                    params.append(f"arg{i}: bv64")
                elif typ[0] == "t":
                    num_elems = int(typ[2])
                    assert num_elems > 0
                    tup_typs = typ[4:].split("_")[:num_elems]
                    tup_typ_strs = []
                    for t in tup_typs:
                        if t[0] == 'r':
                            tup_typ_strs.append(f"bv64")
                        elif t[0] == 'n':
                            tup_typ_strs.append("bv64")
                        else:
                            raise Exception(f"Unknown tuple type: {t}")
                    params.append(f"arg{i}: {{{', '.join(tup_typ_strs)}}}")
                else:
                    raise Exception(f"Unknown type annotation found when generating instruction definitions: {typ}")
            arg_sig = ", ".join(params)
            inst_specs.append(inst_def_template.substitute(INST_NAME=inst, ARG_SIG=arg_sig))
        return "\n\n".join(inst_specs)

    def generate_platform_def_skeleton(self, inst_str):
        tree = self.arm_bb_parser.parse(inst_str)
        normalized = NormalizeConditionalInstructions(tree)
        RenameInstructions().transform(normalized)
        cleaned = RemoveTripleArrays().transform(normalized)

        collector = CollectRegisterNames()
        collector.visit(cleaned)

        platform_name = "aarch64"
        arch_vars = []
        for reg in sorted(collector.reg_names):
            arch_vars.append(f"// TODO: Model ${reg}")
        body = '\n'.join(arch_vars)
        return platform_def_template.substitute(PLATFORM_NAME=platform_name, BODY=body)

