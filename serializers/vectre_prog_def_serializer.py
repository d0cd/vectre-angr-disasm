from .templates import *
from .utils import *

import bap
import re


class VectreProgDefSerializer:

    def __init__(self, _program, _entry_points, _adt_symbolic_parser):
        self.program = _program
        self.entry_points = _entry_points
        self.adt_symbolic_parser = _adt_symbolic_parser
        self.reg_type_map = {}
        for k, v in self.adt_symbolic_parser.reg_type_map.items():
            new_name = re.sub('#', '_reg', k)
            self.reg_type_map[new_name] = v



    ####################################################################################
    ################### EXPRESSION TREE HELPERS ########################################
    ####################################################################################

    # Translates adt expression into UCLID5 expression
    def adt_expr_to_uclid5(self, stmt):
        if isinstance(stmt, bap.bir.Def):
            if isinstance(stmt.rhs, bap.bil.Store):
                self.write_set.add("mem")
                self.write_set.add("obs_mem")
                return "        " + self.adt_expr_to_uclid5(stmt.rhs) + ";\n"
            else:
                assigned_lhs = self.adt_expr_to_uclid5(stmt.lhs)
                self.write_set.add(assigned_lhs)
                if isinstance(stmt.rhs, bap.bir.Unknown):
                    return f"        havoc {assigned_lhs};\n"
                else:
                    return "        " + assigned_lhs + " = " + self.adt_expr_to_uclid5(stmt.rhs) + ";\n"
        elif isinstance(stmt, bap.bir.Jmps):
            self.write_set.add("pc")
            self.write_set.add("br_pred_state")
            for var in self.reg_type_map.keys():
                self.write_set.add(var)
                self.write_set.add("spec_" + var)
            self.write_set.add("spec_level")
            self.write_set.add("spec_pc")

            self.write_set.add("mem")
            cond = self.adt_expr_to_uclid5(stmt[0].cond)
            ret = "        call direct_branch(" + cond + ", " + self.adt_expr_to_uclid5(
                stmt[0].target) + ", " + self.adt_expr_to_uclid5(stmt[1].target) + ");\n"
            return ret
        elif isinstance(stmt, bap.bir.Jmp):
            self.write_set.add("pc")
            self.write_set.add("br_pred_state")
            cond = self.adt_expr_to_uclid5(stmt.cond)
            # TODO: Might need to handle these better
            if isinstance(stmt, bap.bir.Call):
                ret = "        if (common.word_to_bool(" + cond + ")) { pc = " + self.adt_expr_to_uclid5(stmt.target[0]) + "; }\n"
            else:
                ret = "        if (common.word_to_bool(" + cond + ")) { pc = " + self.adt_expr_to_uclid5(stmt.target) + "; }\n"
            ret += "        br_pred_state = common.update_br_pred(br_pred_state," + cond + ");\n"
            return ret
        else:
            ##### CONSTANT EVALUATIONS AND VARIABLES #############
            if isinstance(stmt, bap.bil.Int):
                return self.int_to_const(stmt.value)
            elif isinstance(stmt, bap.bil.Var):
                return re.sub('#', '_reg', stmt.name)
            ############ BINARY OPERATORS ########################
            elif isinstance(stmt, bap.bil.PLUS):
                return "common.add(" + self.adt_expr_to_uclid5(stmt.lhs) + ", " + self.adt_expr_to_uclid5(
                    stmt.rhs) + ")"
            elif isinstance(stmt, bap.bil.MINUS):
                return "common.sub(" + self.adt_expr_to_uclid5(stmt.lhs) + ", " + self.adt_expr_to_uclid5(
                    stmt.rhs) + ")"
            elif isinstance(stmt, bap.bil.LSHIFT):
                return "common.left_shift(" + self.adt_expr_to_uclid5(stmt.lhs) + ", " + self.adt_expr_to_uclid5(
                    stmt.rhs) + ")"
            elif isinstance(stmt, bap.bil.RSHIFT):
                return f"common.right_shift({self.adt_expr_to_uclid5(stmt.lhs)}, {self.adt_expr_to_uclid5(stmt.rhs)})"
            elif isinstance(stmt, bap.bil.AND):
                return "common.and(" + self.adt_expr_to_uclid5(stmt.lhs) + ", " + self.adt_expr_to_uclid5(
                    stmt.rhs) + ")"
            elif isinstance(stmt, bap.bil.NOT):
                return "common.not(" + self.adt_expr_to_uclid5(stmt.arg) + ")"
            elif isinstance(stmt, bap.bil.OR):
                return f"common.or({self.adt_expr_to_uclid5(stmt.lhs)}, {self.adt_expr_to_uclid5(stmt.rhs)})"
            elif isinstance(stmt, bap.bil.XOR):
                return "common.xor(" + self.adt_expr_to_uclid5(stmt.lhs) + ", " + self.adt_expr_to_uclid5(stmt.rhs) + ")"
            elif isinstance(stmt, bap.bil.LT):
                return "common.lessthan(" + self.adt_expr_to_uclid5(stmt.lhs) + ", " + self.adt_expr_to_uclid5(
                    stmt.rhs) + ")"
            elif isinstance(stmt, bap.bil.EQ):
                return f"common.equals({self.adt_expr_to_uclid5(stmt.lhs)}, {self.adt_expr_to_uclid5(stmt.rhs)})"
            ######### CASTS ######################################
            elif isinstance(stmt, bap.bil.Cast):
                if isinstance(stmt, bap.bil.HIGH):
                    return "common.high(" + self.int_to_const(stmt.size) + ", " + self.adt_expr_to_uclid5(stmt.expr) + ")"
                elif isinstance(stmt, bap.bil.LOW):
                    return "common.low(" + self.int_to_const(stmt.size) + ", " + self.adt_expr_to_uclid5(stmt.expr) + ")"
            ########## LETS ######################################
            elif isinstance(stmt, bap.bir.Let):
                val = self.adt_expr_to_uclid5(stmt.value)
                expr = self.adt_expr_to_uclid5(stmt.expr)
                return expr.replace(stmt.var.name, val)
            ########## UNKNOWN ###################################
            elif isinstance(stmt, bap.bir.Unknown):
                #TODO
                return ""
            ########## MEMORY STORE AND LOAD #####################
            elif isinstance(stmt, bap.bil.Load):
                temp_var = self.get_temp_var_name()
                self.temp_access[temp_var] = self.adt_expr_to_uclid5(stmt.idx)
                self.temp_vars += temp_var
                self.write_set.add("obs_mem")
                return temp_var
            elif isinstance(stmt, bap.bil.Store):
                return "call store_mem(" + self.adt_expr_to_uclid5(stmt.idx) + ", " + self.adt_expr_to_uclid5(
                    stmt.value) + ")"
            ############ JUMPS ###################################
            elif isinstance(stmt, bap.bir.Direct):
                if stmt.arg.name in self.entry_points:
                    return self.entry_points[stmt.arg.name]
                else:
                    raise AssertionError("Direct branch should always have an identifiable target")
            elif isinstance(stmt, bap.bir.Indirect):
                return "halt"  # FIXME: Currently does not support indirect jumps
            else:
                # return ""
                raise NotImplementedError(f"Translation for expression: {stmt} is not implemented")


    ####################################################################################
    ####################### GENERATE VECTRE MODELS #####################################
    ####################################################################################

    def generate_prog_def(self, prog_name, basic_blocks):
        return prog_def_template.substitute(PROGNAME=prog_name, BASIC_BLOCKS=basic_blocks)


    ####################################################################################
    ####################### HELPERS ####################################################
    ####################################################################################


    def generate_basic_block(self, block):
        pass
