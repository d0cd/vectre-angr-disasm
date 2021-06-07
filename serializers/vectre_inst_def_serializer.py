from .aarch64_disasm_processor import AArch64DisassemblyProcessor
from .amd64_disasm_processor import AMD64DisassemblyProcessor

from typing import List

import angr


class VectreInstDefSerializer:
    angr_projects: List[angr.Project]

    def __init__(self, _projects):
        self.angr_projects = _projects

        # All projects must have the same arch
        assert len(_projects) > 0, "Need at least one ANGR project"
        arch = self.angr_projects[0].arch
        for proj in self.angr_projects:
            if proj.arch != arch:
                raise Exception("VectreInstDefSerializer must be initialized with a list of ANGR projects that all use the same architecture.")

        if self.angr_projects[0].arch == angr.archinfo.ArchAArch64():
            self.disas_processor = AArch64DisassemblyProcessor()
        elif self.angr_projects[0].arch == angr.archinfo.ArchAMD64():
            self.disas_processor = AMD64DisassemblyProcessor()
        else:
            self.disas_processor = None

    def serialize_inst_def(self):
        bb_strs = []
        for proj in self.angr_projects:
            cfg = proj.analyses.CFGFast()
            nodes = cfg.graph.nodes()
            for node in nodes:
                if node.block is not None:
                    bb_strs.append(str(node.block.disassembly))
        inst_str = "\n".join(bb_strs)
        serialized_spec = self.disas_processor.generate_inst_def_skeleton(inst_str)
        print(serialized_spec)
        return serialized_spec
