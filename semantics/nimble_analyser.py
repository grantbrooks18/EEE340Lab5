from antlr4 import ParseTreeWalker
from .errorlog import ErrorLog
from .nimblesemantics import InferTypesAndCheckConstraints, DefineScopesAndSymbols


class NimbleSemanticErrors(Exception):

    def __init__(self, error_log):
        self.error_log = error_log

    def __repr__(self):
        return repr(self.error_log)


def do_semantic_analysis(tree):
    errors = ErrorLog()
    walker = ParseTreeWalker()
    walker.walk(DefineScopesAndSymbols(errors), tree)
    walker.walk(InferTypesAndCheckConstraints(errors), tree)
    if errors.total_entries():
        raise NimbleSemanticErrors(errors)
    else:
        return tree
