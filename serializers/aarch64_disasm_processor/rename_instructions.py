from lark import Transformer, Tree


class RenameInstructions(Transformer):
    """
    Renames instructions to contain name and operand tags.
    Tags are of the form r (denoting a register), n (denoting a number), or t<n> (denoting a tuple of n elements)
    Note that a tuple tag may be followed by <op>(#(HEX|DEC))? which indicates a specific addressing/wb mode. (See ARM docs)
    """

    def line(self, args):
        assert len(args) == 2 or len(args) == 3, f"Malformed line: {args}"
        op = args[1]

        # If the instruction has operands transform it
        if len(args) == 3:
            operands = args[2].children
            tag = ""
            for operand in operands:
                if operand.data == 'reg':
                    tag += "__r"
                elif operand.data == 'number':
                    tag += "__n"
                elif operand.data == 'arr':
                    arr_length = operand.children[0].children[0].data
                    if arr_length == "sing_arr":
                        tag += "__t1"
                    elif arr_length == "doub_arr":
                        tag += "__t2"
                    elif arr_length == "trip_arr":
                        tag += "__t2"
                        tail = operand.children[0].children[0].children[2:]
                        tag += f"_{tail[0].children[0].value}"
                        if len(tail) == 2:
                            tag += tail[1].children[0].value
                    else:
                        raise Exception(f"Unsupported array length: {arr_length}")

                    if operand.children[0].data == 'pre_index':
                        tag += "_pre"  #
                    elif operand.children[0].data == 'post_index':
                        tag += '_post'
                    else:
                        raise Exception(f"Unknown indexing scheme: {operand.children[0].data}")

                else:
                    raise Exception(f"Unknown operand type: {operand.data}")
            op.children[0].value += tag




