from .templates import *
from .utils import *

import bap
import re


class UCLIDSerializer:

    def __init__(self, _program, _entry_points, _adt_symbolic_parser):
        self.program = _program
        self.entry_points = _entry_points
        self.adt_symbolic_parser = _adt_symbolic_parser
        self.temp_var_counter = 0
        self.reg_type_map = {}
        for k, v in self.adt_symbolic_parser.reg_type_map.items():
            new_name = re.sub('#', '_reg', k)
            self.reg_type_map[new_name] = v

    # Generates a new temporary variable name
    def get_temp_var_name(self):
        var_name = "t" + str(self.temp_var_counter)
        self.temp_var_counter = self.temp_var_counter + 1;
        return var_name

    def int_to_const(self, val):
        return "const_" + str(val)

    def int_to_addr(self, val):
        return "addr_" + str(val)

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
    ###################### VARIABLE DECLARATION HELPERS ################################
    ####################################################################################

    # Prints variable declaration with type
    def var_decl(self, decl, name, typ):
        ret = "    " + decl + " " + name + ": "
        if isinstance(typ, bap.bil.Imm):
            if typ.size == 1:
                ret += "word_t;"
            else:
                ret += "word_t;"
        elif isinstance(typ, bap.bil.Mem):
            ret += "mem_t;"
        ret += "\n"
        return ret

    # Prints speculative variable declaration with type
    def spec_var_decl(self, decl, name, typ):
        ret = "    " + decl + " spec_" + name + ": "
        if isinstance(typ, bap.bil.Imm):
            if typ.size == 1:
                ret += "spec_flag_reg_t;"
            else:
                ret += "spec_reg_t;"
        elif isinstance(typ, bap.bil.Mem):
            ret += "spec_mem_t;"
        ret += "\n"
        return ret

    # Prints speculative variable declaration with type
    def spec_var_init(self, name, typ):
        ret = "        spec_" + name + " = common."
        if isinstance(typ, bap.bil.Imm):
            if typ.size == 1:
                ret += "spec_flag_reg_init;"
            else:
                ret += "spec_reg_init;"
        elif isinstance(typ, bap.bil.Mem):
            ret += "spec_mem_init;"
        ret += "\n"
        return ret

    ####################################################################################
    ####################### GENERATE UCLID5 MODELS #####################################
    ####################################################################################

    def generate_commons_module(self):
        pcs = "type pc_t = enum {\n"
        # PC type (blocks as entry points)
        for v in self.entry_points.values():
            pcs += "        " + v + ",\n"
        pcs += ("        halt\n"
                "    };\n")

        num_consts = []
        for constant in self.adt_symbolic_parser.const_ids:
            num_consts.append("const " + self.int_to_const(constant) + ": word_t;\n")
        num_consts = '    '.join(num_consts)

        init_consts = []
        for addr in self.adt_symbolic_parser.addr_consts:
            init_consts.append("const " + self.int_to_const(addr) + ": addr_t;\n")
        init_consts = '    '.join(init_consts)

        init_states = ""
        for var, typ in self.reg_type_map.items():
            init_states += self.var_decl("const", str(var) + "_init", typ)

        assume_distinct = "assume distinct("
        for addr in self.adt_symbolic_parser.addr_consts:
            assume_distinct += str(self.int_to_const(addr)) + ", "
        assume_distinct += "secret_addr);\n"

        return common_template.substitute(PCS=pcs,
                                          NUM_CONSTS=num_consts,
                                          INIT_CONSTS=init_consts,
                                          INIT_STATES=init_states,
                                          ASSUME_DISTINCT=assume_distinct)

    def generate_main_module(self):
        same_nospec = "    invariant same_when_not_speculating_t1_t3: (t3.spec_level == common.spec_idx0 ==> (t1.spec_level == t3.spec_level && t1.pc == t3.pc && " + " && ".join(
                        map(lambda kv: "t1." + kv[0] + " == t3." + kv[0], self.reg_type_map.items())) + "));\n"
        same_nospec += "    invariant same_when_not_speculating_t2_t4: (t4.spec_level == common.spec_idx0 ==> (t2.spec_level == t4.spec_level && t2.pc == t4.pc && " + " && ".join(
                          map(lambda kv: "t2." + kv[0] + " == t4." + kv[0], self.reg_type_map.items())) + "));\n"
        return main_template.substitute(SAME_NOSPEC=same_nospec)

    def generate_program_module(self):
        print("=============== Program ==================")
        ret = "module program {\n"
        # Set up variables
        ret += self.generate_program_preamble()
        # Write the helper functions for branch prediction and processor operations
        ret += self.generate_program_helper()
        # Write the basic blocks as uclid procedures
        ret += self.generate_program_basic_block_procedures()
        # Initialize program
        ret += self.generate_program_init_block()
        # Write transition relation
        ret += self.generate_program_next_block()
        ret += "}\n"
        return ret

    ####################################################################################
    ################# GENERATE MODULE HELPERS ##########################################
    ####################################################################################

    def generate_program_preamble(self):
        # Speculation, pc, memeory, and observable states
        ret = ("    type * = common.*;\n"
               "    const * = common.*;\n\n"
               "    input spec_enabled: boolean;\n\n"
               "    var pc: pc_t;\n"
               "    var br_pred_state : br_pred_state_t;\n"
               "    var obs_mem: obs_mem_t;\n\n")
        # Register vars
        for var, typ in self.reg_type_map.items():
            ret += self.var_decl("var", var, typ)
        ret += "\n"
        # Speculation stack for saving register values at branch checkpoints
        ret += "    var spec_pc: spec_pc_t;\n"
        ret += "    var spec_level: spec_idx_t;\n"
        for var, typ in self.reg_type_map.items():
            ret += self.spec_var_decl("var", var, typ)
        ret += "\n"
        return ret

    def generate_program_helper(self):
        var_list = self.reg_type_map
        spec_var_list = list(map(lambda name: "spec_" + name, self.reg_type_map.keys()))
        ret = ("""    procedure direct_branch(cond : word_t, pc_if : pc_t, pc_else : pc_t) 
        modifies pc, mem, br_pred_state, spec_level, spec_pc, """
               + ", ".join(var_list) + ", " + ", ".join(spec_var_list) + """;
    {
        var pred : boolean;

        br_pred_state = common.update_br_pred(br_pred_state, cond);
        pred = common.br_pred(br_pred_state, pc);

        if (common.word_to_bool(cond)) {
            if (spec_enabled && pred) {
                call save_reg_states(pc_if);
                spec_level = spec_level + common.spec_idx1;
                pc = pc_else;
            } else {
                pc = pc_if;
            }
        } else {
            if (spec_enabled && pred) {
                call save_reg_states(pc_else);
                spec_level = spec_level + common.spec_idx1;
                pc = pc_if;
            } else {
                pc = pc_else;
            }
        }
    }
    

    // Add speculation checkpoint to speculation checkpoint stack
    procedure save_reg_states(resolvePC : pc_t)
        modifies spec_pc, """ + ", ".join(spec_var_list) + """;
    {\n"""
               + "\n".join(
                    map(lambda spec_var, var: "        " + spec_var + "[spec_level] = " + var + ";", spec_var_list,
                        var_list)) + """\n
        spec_pc[spec_level] = resolvePC;
        spec_mem[spec_level] = mem;
    }

    procedure restore_state()
        modifies pc, """ + ", ".join(var_list) + """;
    {\n"""
               + "\n".join(
                    map(lambda spec_var, var: "        " + var + " = " + spec_var + "[spec_level];", spec_var_list,
                        var_list)) + """\n
        pc  = spec_pc[spec_level];
        mem = spec_mem[spec_level];
    }

    // Handles walking back misspeculation
    procedure do_resolve()
        modifies pc, mem, spec_level, """ + ", ".join(var_list) + """;
    {
        var prev_spec_level : spec_idx_t;
        // Non deterministic choice of walkback level
        assume (prev_spec_level == common.walk_back(br_pred_state, pc, spec_level));
        assume (common.spec_idx0 <=_u prev_spec_level && prev_spec_level <_u spec_level);
        // Walkback
        spec_level = prev_spec_level;
        call restore_state();
    }

    procedure load_mem(addr : word_t)
        returns (value : word_t)
        modifies obs_mem;
    {
        value = common.read(mem, addr);
        obs_mem = common.update_obs_mem(obs_mem, addr);
    }

    procedure store_mem(addr : word_t, value : word_t)
        modifies mem, obs_mem;
    {
        var old_mem : mem_t;

        old_mem = mem;
        mem = common.write(mem, addr, value);
        // TOA Axiom 1
        assume (common.read(mem, addr) == value);
        // TOA Axiom 2
        assume (forall (addr_ : addr_t) :: addr_ != addr ==> common.read(old_mem, addr_) == common.read(mem, addr_));

        obs_mem = common.update_obs_mem(obs_mem, addr);
    }""")
        ret += "\n\n"
        return ret

    def generate_program_basic_block_procedures(self):
        ret = ""
        for sub in self.program.subs:
            for i, blk in enumerate(sub.blks):
                ret += f"    procedure execute_{sub.name}_block{i}()\n"
                temp_var_decls = ""
                body = ""
                self.temp_vars = []
                self.write_set = set()
                for defn in blk.defs:
                    self.temp_access = {}
                    uclid5_stmt = self.adt_expr_to_uclid5(defn)
                    # Create temporary variables for memory accesses
                    for tmp, idx in self.temp_access.items():
                        temp_var_decls += "        var " + tmp + ": word_t;\n"
                        body += "        call (" + tmp + ") = load_mem(" + idx + ");\n"
                    body += uclid5_stmt
                if len(blk.jmps) == 2:
                    body += self.adt_expr_to_uclid5(blk.jmps)
                elif len(blk.jmps) == 1:
                    body += self.adt_expr_to_uclid5(blk.jmps[0])
                else:
                    raiseRuntimeException("Should not have more than 2 jumps!")
                if len(self.write_set) > 0:
                    ret += "        modifies " + ", ".join(list(self.write_set)) + ";\n"
                ret += "    {\n"
                ret += temp_var_decls
                ret += body
                ret += "    }\n\n"
        ret += "\n"
        return ret

    def generate_program_init_block(self):
        ret = ("        var secret_value: word_t;\n"
               "        obs_mem = common.obs_mem_init;\n"
               "        br_pred_state = common.br_pred_init;\n"
               "        spec_level = common.spec_idx0;\n"
               "        spec_pc = common.spec_pc_init;\n"
               "        pc = main_block0;\n")
        var_list = self.reg_type_map
        for var, typ in var_list.items():
            ret += "        " + var + " = common." + var + "_init;\n"
        for var, typ in var_list.items():
            ret += self.spec_var_init(var, typ)
        ret += "        assume (forall (addr_ : addr_t, spec_level_ : spec_idx_t) :: common.read(common.mem_init, addr_) == common.read(spec_mem[spec_level_], addr_));\n"
        ret += "        call store_mem(common.secret_addr, secret_value);\n"
        return "    init {\n" + ret + "    }\n"

    def generate_program_next_block(self):
        ret = ("    next {\n"
               "        if (spec_level != common.spec_idx0 && common.br_resolve(br_pred_state, pc)) {\n"
               "            call do_resolve();\n"
               "        } else {\n"
               "            case\n")
        for v in self.entry_points.values():
            ret += "                (pc == " + v + ") : { call execute_" + v + "(); }\n"
        ret += "                (pc == halt) : {}\n"
        ret += ("            esac\n"
                "        }\n"
                "    }\n")
        return ret