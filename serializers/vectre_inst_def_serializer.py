from .aarch64_disasm_processor import AArch64DisassemblyProcessor
from .amd64_disasm_processor import AMD64DisassemblyProcessor

import angr


class VectreInstDefSerializer:
    angr_project: angr.Project

    def __init__(self, _project):
        self.angr_project = _project
        if self.angr_project.arch == angr.archinfo.ArchAArch64():
            self.disas_processor = AArch64DisassemblyProcessor()
        elif self.angr_project.arch == angr.archinfo.ArchAMD64():
            self.disas_processor = AMD64DisassemblyProcessor()
        else:
            self.disas_processor = None

    def serialize_inst_def(self):
        bb_strs = []
        cfg = self.angr_project.analyses.CFGFast()
        nodes = cfg.graph.nodes()
        for node in nodes:
            if node.block is not None:
                bb_strs.append(str(node.block.disassembly))
        inst_str = "\n".join(bb_strs)
        return self.disas_processor.generate_inst_def_skeleton(inst_str)
