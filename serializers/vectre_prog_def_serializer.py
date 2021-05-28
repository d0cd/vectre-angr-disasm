from .templates import *

import angr
import re


class VectreProgDefSerializer:
    angr_project: angr.Project

    def __init__(self, _project):
        self.angr_project = _project

    def serialize_binary(self):
        cfg = self.angr_project.analyses.CFGFast()
        nodes = cfg.graph.nodes()
        basic_blocks = []
        for node in nodes:
            basic_blocks.append(self.serialize_cfg_node(node))
        prog_name = self.angr_project.filename.replace(".o", "").replace("/", "_").replace(".", "")
        bb_str = "\n".join(basic_blocks)
        return prog_def_template.substitute(PROG_NAME=prog_name, BASIC_BLOCKS=bb_str)

    def serialize_cfg_node(self, node: angr.knowledge_plugins.cfg.CFGNode):
        header = f"ENTRY_{node.block_id}:"
        fixed_strs = []
        disasm_str = str(node.block.disassembly)
        inst_strs = disasm_str.split('\n')
        assert len(node.block.instruction_addrs) == len(inst_strs)
        for (addr, inst_str) in zip(node.block.instruction_addrs, inst_strs):
            decimal_addr_str = re.sub(r'^0x\d+', str(addr), inst_str).strip()
            fixed_str = f"    {decimal_addr_str};"
            fixed_strs.append(fixed_str)
        body = '\n'.join(fixed_strs)
        return f"{header}\n{body}"
