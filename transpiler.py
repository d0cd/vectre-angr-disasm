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

    # Takes a BIL function ADT and translates it into a UCLID5 model
    # string with the secure speculation property
    def disassemble(self, output_file_path: str):
        self.parse_program()
        serializer = VectreProgDefSerializer(self.program, self.entry_points, self.adt_symbolic_parser)
        # ================== Generate main module =============================
        prog_def = serializer.generate_main_module()
        prog_file = open(output_file_path, "w+")
        prog_file.write(prog_def)
        prog_file.close()




