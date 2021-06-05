from .templates import *
from .aarch64_disasm_processor import AArch64DisassemblyProcessor
from .amd64_disasm_processor import AMD64DisassemblyProcessor

import angr
import re


class VectrePlatformDefSerializer:
    angr_project: angr.Project

    def __init__(self, _project):
        self.angr_project = _project
        if self.angr_project.arch == angr.archinfo.ArchAArch64():
            self.disas_processor = AArch64DisassemblyProcessor()
        elif self.angr_project.arch == angr.archinfo.ArchAMD64():
            self.disas_processor = AMD64DisassemblyProcessor()
        else:
            self.disas_processor = None

    def serialize_platform_def(self):
        pass


