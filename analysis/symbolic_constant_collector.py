import bap
from bap.adt import Visitor

import re

class SymbolicConstantCollector(Visitor):
    def __init__(self):
        self.const_ids = set()
        self.addr_consts = set()
        self.var_type_map = {}
        self.reg_type_map = {}

    def visit_Int(self, adt_int):
        self.const_ids.add(adt_int.value)

    def visit_Var(self, adt_var):
        if '$' in adt_var.name:
            self.var_type_map[adt_var.name] = adt_var.type
        else:
            self.reg_type_map[adt_var.name] = adt_var.type

    def visit_Load(self, adt_load):
        self.run(adt_load.mem)
        self.run(adt_load.endian)
        self.run(adt_load.size)
        if isinstance(adt_load.idx, bap.bil.Int):
            self.addr_consts.add(adt_load.idx.value)
        else:
            self.run(adt_load.idx)

    def visit_Store(self, adt_store):
        self.run(adt_store.mem)
        self.run(adt_store.value)
        self.run(adt_store.endian)
        self.run(adt_store.size)
        if isinstance(adt_store.idx, bap.bil.Int):
            self.addr_consts.add(adt_store.idx.value)
        else:
            self.run(adt_store.idx)

    def clean_keys(self):
        old, cleaned = set(), set()
        for k in self.var_type_map.keys():
            old.add(k)
            cleaned.add(re.sub('#|\$', '', k))
        assert len(old) == len(cleaned), "Cleaned names should not reduce the number of variables"

        new_map = {}
        for k, v in self.var_type_map.items():
            new_name = re.sub('#|\$', '_reg', k)
            new_map[new_name] = v
        self.var_type_map = new_map
