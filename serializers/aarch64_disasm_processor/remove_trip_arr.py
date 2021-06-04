from lark import Transformer, Tree


class RemoveTripleArrays(Transformer):

    def trip_arr(self, args):
        return Tree('doub_arr', args[:2])

