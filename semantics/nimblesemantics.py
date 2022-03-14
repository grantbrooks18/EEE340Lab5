"""
Author: Greg Phillips

Version: 2022-03-13

The nimblesemantics module contains classes sufficient to perform a semantic analysis
of a subset of Nimble programs, not including function definitions and function calls.

The analysis has two major tasks:

- to infer the types of all expressions in a Nimble program and to add appropriate type
annotations to the program's ANTLR-generated syntax tree by monkey-patching a `type`
attribute (a `symboltable.PrimitiveType`) onto each expression node; and

- to identify and flag all violations of the Nimble semantic specification
using the errorlog module.

There are two phases to the analysis: 1. DefineScopesAndSymbols, and
2. InferTypesAndCheckSemantics.

In the first phase, `symboltable.Scope` objects are created for all scope-defining parse
tree nodes, here the script and the main. These are monkey-patched onto the tree nodes
as `scope` attributes. Also in this phase, all declared variable types are recorded in
the appropriate scope (here the main scope). Restrictions on duplicate definitions are
enforced.

In the second phase, type inference is performed and all other semantic constraints are
checked.
"""

from .errorlog import ErrorLog, Category
from nimble import NimbleListener, NimbleParser
from .symboltable import Scope, PrimitiveType


class DefineScopesAndSymbols(NimbleListener):

    def __init__(self, error_log: ErrorLog):
        self.error_log = error_log
        self.current_scope = None

    def enterScript(self, ctx: NimbleParser.ScriptContext):
        global_scope = Scope('$global', PrimitiveType.Void, None)
        ctx.scope = global_scope
        self.current_scope = global_scope

    def enterFuncDef(self, ctx: NimbleParser.FuncDefContext):
        self.error_log.add(ctx, Category.UNSUPPORTED_LANGUAGE_FEATURE,
                           'this implementation does not support function definitions')

    def enterFuncCall(self, ctx: NimbleParser.FuncCallContext):
        self.error_log.add(ctx, Category.UNSUPPORTED_LANGUAGE_FEATURE,
                           'this implementation does not support function calls')

    def enterMain(self, ctx: NimbleParser.MainContext):
        main_scope = Scope('$main', PrimitiveType.Void, self.current_scope)
        ctx.scope = main_scope
        self.current_scope = main_scope

    def exitMain(self, ctx: NimbleParser.MainContext):
        self.current_scope = self.current_scope.enclosing_scope

    def duplicate_name(self, ctx, name):
        already_declared = self.current_scope.resolve_locally(name)
        if already_declared:
            self.error_log.add(ctx, Category.DUPLICATE_NAME,
                               f"Can't redeclare {name}; already declared as {already_declared}")
            return True
        return False

    def exitVarDec(self, ctx: NimbleParser.VarDecContext):
        name = ctx.ID().getText()
        if not self.duplicate_name(ctx, name):
            _type = PrimitiveType[ctx.TYPE().getText()]
            self.current_scope.define(name, _type)


class InferTypesAndCheckConstraints(NimbleListener):

    def __init__(self, error_log: ErrorLog):
        self.error_log = error_log
        self.current_scope = None

    def enterScript(self, ctx: NimbleParser.ScriptContext):
        self.current_scope = self.current_scope.enclosing_scope

    def enterMain(self, ctx: NimbleParser.MainContext):
        self.current_scope = ctx.scope

    def exitMain(self, ctx: NimbleParser.MainContext):
        self.current_scope = self.current_scope.enclosing_scope

    def exitReturn(self, ctx: NimbleParser.ReturnContext):
        required_type = self.current_scope.return_type
        returned_type = ctx.expr().type if ctx.expr() else PrimitiveType.Void
        if required_type != returned_type:
            self.error_log.add(ctx, Category.INVALID_RETURN,
                               f'Required to return {required_type}, returns {returned_type}')

    def log_invalid_assign(self, ctx, var_name, _type):
        self.error_log.add(ctx, Category.ASSIGN_TO_WRONG_TYPE,
                           f"Can't assign {ctx.expr().type} expression to variable "
                           f"{var_name} of type {_type}")

    def exitVarDec(self, ctx: NimbleParser.VarDecContext):
        _type = PrimitiveType[ctx.TYPE().getText()]
        if ctx.expr() and _type != ctx.expr().type:
            self.log_invalid_assign(ctx, ctx.ID().getText(), _type)

    # --------------------------------------------------------
    # Statements
    # --------------------------------------------------------

    def exitAssignment(self, ctx: NimbleParser.AssignmentContext):
        name = ctx.ID().getText()
        _type = self.current_scope.resolve(name).type
        if not _type:
            self.error_log.add(ctx, Category.UNDEFINED_NAME,
                               f'Assignment target {name} not declared')
        elif _type != ctx.expr().type:
            self.log_invalid_assign(ctx, name, _type)

    def check_boolean_condition(self, ctx, kind):
        if ctx.expr().type != PrimitiveType.Bool:
            self.error_log.add(ctx, Category.CONDITION_NOT_BOOL,
                               f"{kind} condition {ctx.getText()} has type {ctx.expr().type} not Bool")

    def exitWhile(self, ctx: NimbleParser.WhileContext):
        self.check_boolean_condition(ctx, 'While')

    def exitIf(self, ctx: NimbleParser.IfContext):
        self.check_boolean_condition(ctx, 'If')

    def exitPrint(self, ctx: NimbleParser.PrintContext):
        if ctx.expr().type == PrimitiveType.ERROR:
            self.error_log.add(ctx, Category.UNPRINTABLE_EXPRESSION,
                               f"Can't print expression {ctx.getText()} as it has type ERROR")

    def exitFuncCallStmt(self, ctx: NimbleParser.FuncCallStmtContext):
        ctx.type = ctx.funcCall().type

    # --------------------------------------------------------
    # Expressions
    # --------------------------------------------------------

    def exitIntLiteral(self, ctx: NimbleParser.IntLiteralContext):
        ctx.type = PrimitiveType.Int

    def exitNeg(self, ctx: NimbleParser.NegContext):
        if ctx.op.text == '-' and ctx.expr().type == PrimitiveType.Int:
            ctx.type = PrimitiveType.Int
        elif ctx.op.text == '!' and ctx.expr().type == PrimitiveType.Bool:
            ctx.type = PrimitiveType.Bool
        else:
            ctx.type = PrimitiveType.ERROR
            self.error_log.add(ctx, Category.INVALID_NEGATION,
                               f"Can't apply {ctx.op.text} to {ctx.expr().type.name}")

    def exitParens(self, ctx: NimbleParser.ParensContext):
        ctx.type = ctx.expr().type

    def binary_on_ints(self, ctx, result_type):
        if ctx.expr(0).type == PrimitiveType.Int and ctx.expr(1).type == PrimitiveType.Int:
            ctx.type = result_type
        else:
            ctx.type = PrimitiveType.ERROR
            self.error_log.add(ctx, Category.INVALID_BINARY_OP,
                               f"Can't apply {ctx.op.text} to {ctx.expr(0).type} and {ctx.expr(1).type}")

    def exitMulDiv(self, ctx: NimbleParser.MulDivContext):
        self.binary_on_ints(ctx, PrimitiveType.Int)

    def exitAddSub(self, ctx: NimbleParser.AddSubContext):
        if (ctx.op.text == '+' and
                ctx.expr(0).type == PrimitiveType.String and
                ctx.expr(1).type == PrimitiveType.String):
            ctx.type = PrimitiveType.String
        else:
            self.binary_on_ints(ctx, PrimitiveType.Int)

    def exitCompare(self, ctx: NimbleParser.CompareContext):
        self.binary_on_ints(ctx, PrimitiveType.Bool)

    def exitVariable(self, ctx: NimbleParser.VariableContext):
        name = ctx.getText()
        _type = self.current_scope.resolve(name).type
        if not _type:
            ctx.type = PrimitiveType.ERROR
            self.error_log.add(ctx, Category.UNDEFINED_NAME,
                               f'Name {name} is not declared')
        else:
            ctx.type = _type

    def exitStringLiteral(self, ctx: NimbleParser.StringLiteralContext):
        ctx.type = PrimitiveType.String

    def exitBoolLiteral(self, ctx: NimbleParser.BoolLiteralContext):
        ctx.type = PrimitiveType.Bool

    def exitFuncCallExpr(self, ctx: NimbleParser.FuncCallExprContext):
        ctx.type = ctx.funcCall().type
