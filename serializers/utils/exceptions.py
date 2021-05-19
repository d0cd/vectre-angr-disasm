
class RuntimeException(Exception):
    pass

class UnimplementedException(Exception):
    pass


def raiseRuntimeException(string):
    raise RuntimeException(string)

def raiseUnimplementedException(string):
    raise UnimplementedException(string)




