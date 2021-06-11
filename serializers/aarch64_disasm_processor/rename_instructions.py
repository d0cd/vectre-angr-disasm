from lark import Transformer, Tree

import re

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
                    tag += self._create_reg_tag("__r", operand)
                elif operand.data == 'number':
                    tag += "__n"
                elif operand.data == 'arr':
                    arr_length = operand.children[0].children[0].data
                    if arr_length == "sing_arr":
                        tag += "__t_1"
                        tag += self._create_tuple_tag(operand.children[0].children[0].children[:1])
                    elif arr_length == "doub_arr":
                        tag += "__t_2"
                        tag += self._create_tuple_tag(operand.children[0].children[0].children[:2])
                    elif arr_length == "trip_arr":
                        tag += "__t_2"
                        tag += self._create_tuple_tag(operand.children[0].children[0].children[:2])
                        tail = operand.children[0].children[0].children[2:]
                        tag += f"_{tail[0].children[0].value}"
                        if len(tail) == 2:
                            tag += tail[1].children[0].value
                    else:
                        raise Exception(f"Unsupported array length: {arr_length}")

                    # Only tags for pre-index addressing are added, post-indexed instructions can be found by the instruction signature
                    if operand.children[0].data == 'pre_index':
                        tag += "_pre"  #
                    elif operand.children[0].data == 'direct':
                        continue
                    else:
                        raise Exception(f"Unknown indexing scheme: {operand.children[0].data}")

                else:
                    raise Exception(f"Unknown operand type: {operand.data}")
            op.children[0].value += tag
            op.children[0].value = op.children[0].value.replace(".", "_")

    def _create_tuple_tag(self, args):
        tag = ""
        for arg in args:
            if arg.data == "reg":
                tag += self._create_reg_tag("_r", arg)
            elif arg.data == "number":
                tag += "_n"
            else:
                raise Exception(f"Unknown tuple arg: {arg.data}")
        return tag

    def _create_reg_tag(self, prefix, operand):
        tag = prefix
        name = operand.children[0].value
        if (re.match("x\d+", name)):
            tag += "64"
            operand.children[0].value = f"gpr_{name.replace('x', '')}"
        elif (re.match("w\d+", name)):
            tag += "32"
            operand.children[0].value = f"gpr_{name.replace('w', '')}"
        elif (re.match("sp", name)):
            tag += "64"
        elif (re.match("wsp", name)):
            tag += "32"
        elif (re.match("xzr", name)):
            tag += "64"
        elif (re.match("wzr", name)):
            tag += "32"
        else:
            raise Exception(f"Unknown register name: {name}")
        return tag





