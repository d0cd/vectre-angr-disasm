#!/usr/bin/env python3

from analysis import *
from serializers import *

# CMU Binary Analysis Platform
import bap
import os


class VectreDisassembler:
    # Constructor
    def __init__(self):
        self.program = None
        self.adt_symbolic_parser = SymbolicConstantCollector()
        self.entry_points = {}

    def read_binary(self, binary_file_path):
        binary = bap.run(binary_file_path)
        self.program = binary.program

    # Returns the BAP function ADT named function_name
    def parse_program(self):
        if self.program == None:
            raiseRuntimeException("No program found.")
        for sub in self.program.subs:
            # Parse constants and variables of subroutine
            for i, blk in enumerate(sub.blks):
                # Add entry point to entry point dictionary
                if i == 0:
                    self.entry_points[sub.id.name] = f"{sub.name}_block{i}"
                self.entry_points[blk.id.name] = f"{sub.name}_block{i}"
                for defn in blk.defs:
                    self.adt_symbolic_parser.run(defn.lhs)
                    self.adt_symbolic_parser.run(defn.rhs)
        # Clean up names in the map
        print("Addresses from loads and stores: \n" + str(self.adt_symbolic_parser.addr_consts))
        print("Constants from binary operations: \n" + str(self.adt_symbolic_parser.const_ids))
        print("Registers: \n" + str(self.adt_symbolic_parser.reg_type_map))
        print("Intermediate variables: \n" + str(self.adt_symbolic_parser.var_type_map))

    # Takes a BIL function ADT and translates it into a UCLID5 model
    # string with the secure speculation property
    def transpile(self, output_file_path: str):
        self.parse_program()
        serializer = UCLIDSerializer(self.program, self.entry_points, self.adt_symbolic_parser)
        # ================== Generate commons module ==========================
        uclid5_common_module = serializer.generate_commons_module()
        common_file = open(os.path.join(output_file_path, "common.ucl"), "w+")
        common_file.write(uclid5_common_module)
        # ================== Generate main module =============================
        uclid5_program_module = serializer.generate_program_module()
        program_file = open(os.path.join(output_file_path, "program.ucl"), "w+")
        program_file.write(uclid5_program_module)
        # ================== Generate main module =============================
        uclid5_main_module = serializer.generate_main_module()
        main_file = open(os.path.join(output_file_path, "main.ucl"), "w+")
        main_file.write(uclid5_main_module)



