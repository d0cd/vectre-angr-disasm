from string import Template

common_template = Template("module common {\n"
                       # Types
                           "    type byte_t;\n"
                           "    type word_t;\n"
                           "    type addr_t = word_t;\n"
                           "    type mem_t;\n"
                           "    ${PCS}\n"
                       # Observable state types
                           "    type obs_mem_t;\n"
                           "    function update_obs_mem(mem_obs: obs_mem_t, addr : word_t): obs_mem_t;\n\n"
                           "    type br_pred_state_t;\n"
                           "    function word_to_bool(w : word_t) : boolean;\n"
                           "    function update_br_pred(state : br_pred_state_t, cond : word_t): br_pred_state_t;\n"
                           "    function br_pred(state : br_pred_state_t, pc : pc_t) : boolean;\n"
                           "    function br_resolve(state : br_pred_state_t, pc : pc_t) : boolean;\n\n"
                       # Speculation levels
                           "    type spec_idx_t = integer;\n"
                           "    function walk_back(state : br_pred_state_t, pc : pc_t, spec_idx : spec_idx_t) : spec_idx_t;\n\n" 
                       # Speculative memory (checkpoints at each speculative depth)
                           "    type spec_mem_t      = [spec_idx_t]mem_t;       // Stores memory across speculation so it can be restored\n"
                           "    type spec_reg_t      = [spec_idx_t]word_t;      // Stores shadow registers as we deepen speculation\n"
                           "    type spec_flag_reg_t = [spec_idx_t]word_t;     // Stores flag registers values for speculation checkpoints\n"
                           "    type spec_pc_t       = [spec_idx_t]pc_t;        // Stores the PC value that would have been correct\n\n"
                       # Functions
                           "    function multiply(x : word_t, y : word_t) : word_t;\n"
                           "    function add(x : word_t, y : word_t) : word_t;\n"
                           "    function sub(x : word_t, y : word_t) : word_t;\n"
                           "    function xor(x : word_t, y : word_t) : word_t;\n"
                           "    function left_shift(shift : word_t, x : word_t) : word_t;\n"
                           "    function right_shift(shift: word_t, x : word_t) : word_t;\n"
                           "    function mask(x : word_t, num_bits : word_t) : word_t;\n"
                           "    function lessthan(x : word_t, y : word_t) : word_t;\n"
                           "    function equals(x : word_t, y : word_t) : word_t;\n"
                           "    function and (x : word_t, y : word_t) : word_t;\n"
                           "    function or (x : word_t, y : word_t) : word_t;"
                           "    function not(x : word_t) : word_t;\n"
                           "    function high(size : word_t, y : word_t) : word_t;\n"
                           "    function low(size : word_t, y : word_t) : word_t;\n"
                           "    function read(mem : mem_t, addr : addr_t) : word_t;\n"
                           "    function write(mem : mem_t, addr : addr_t, value : word_t) : mem_t;\n\n"
                       # Numeric constants (word_t type)
                           "    ${NUM_CONSTS}\n"
                       # Initial program variable constants
                           "    ${INIT_CONSTS}\n"
                       # Initial pc and observational states
                           "    const obs_mem_init: obs_mem_t;\n"
                           "    const br_pred_init: br_pred_state_t;\n"
                           "    const spec_mem_init: spec_mem_t;\n"
                           "    const spec_reg_init: spec_reg_t;\n"
                           "    const spec_flag_reg_init: spec_flag_reg_t;\n"
                           "    const spec_pc_init: spec_pc_t;\n\n"
                       # Initial variable states
                           "${INIT_STATES}\n"
                       # Distinct addresses
                           "    assume word_to_bool(const_1) == true;\n"
                           "    assume word_to_bool(const_0) == false;\n"
                           "    ${ASSUME_DISTINCT}\n"
                           "}")
