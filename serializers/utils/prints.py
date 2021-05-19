import bap
import pprint

def print_blocks(binary_file_path, function_name):
    binary = None
    try:
        binary = bap.run(binary_file_path)
    except:
        print("Invalid path to binary!")
        exit(1)
    victim_fun = binary.program.subs.find(function_name)
    pp = pprint.PrettyPrinter(indent=1)
    # Print blocks of victim function
    for blk in victim_fun.blks:
        print('================================ BLOCK ===================================');
        # Definitions
        print("Statements: ==============")
        for defn in blk.defs:
            pp.pprint(str(defn))
        # Jumps
        print("Jumps: ==============")
        for jmp in blk.jmps:
            pp.pprint(str(jmp))

