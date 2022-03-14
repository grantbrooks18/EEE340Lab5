"""
Given a semantically-correct, type-annotated Nimble parse tree,
generates equivalent MIPS assembly code. Does not consider function
definitions, function calls, or return statements.

Authors: TODO: Your names here

Date: TODO: Submission date here
"""

import templates
from nimble import NimbleListener, NimbleParser
from semantics import PrimitiveType


class MIPSGenerator(NimbleListener):

    def __init__(self):
        self.label_index = -1
        self.string_literals = {}
        self.current_scope = None

    def unique_label(self, base):
        """
        Given a base string "whatever", returns a string of the form "x_whatever",
        where the x is a unique integer. Useful for generating unique labels.
        """
        self.label_index += 1
        return f'{base}_{self.label_index}'

    # ---------------------------------------------------------------------------------
    # Provided for you
    # ---------------------------------------------------------------------------------

    def enterMain(self, ctx: NimbleParser.MainContext):
        self.current_scope = ctx.scope

    def exitScript(self, ctx: NimbleParser.ScriptContext):
        ctx.mips = templates.script.format(
            string_literals='\n'.join(f'{label}: .asciiz {string}'
                                      for label, string in self.string_literals.items()),
            main=ctx.main().mips
        )

    def exitMain(self, ctx: NimbleParser.MainContext):
        ctx.mips = ctx.body().mips

    def exitBlock(self, ctx: NimbleParser.BlockContext):
        ctx.mips = '\n'.join(s.mips for s in ctx.statement())

    def exitBoolLiteral(self, ctx: NimbleParser.BoolLiteralContext):
        value = 1 if ctx.BOOL().getText() == 'true' else 0
        ctx.mips = 'li     $t0 {}'.format(value)

    def exitIntLiteral(self, ctx: NimbleParser.IntLiteralContext):
        ctx.mips = 'li     $t0 {}'.format(ctx.INT().getText())

    def exitStringLiteral(self, ctx: NimbleParser.StringLiteralContext):
        label = self.unique_label('string')
        self.string_literals[label] = ctx.getText()
        ctx.mips = 'la     $t0 {}'.format(label)

    def exitPrint(self, ctx: NimbleParser.PrintContext):
        """
        Bool values have to be handled separately, because we print 'true' or 'false'
        but the values are encoded as 1 or 0
        """
        if ctx.expr().type == PrimitiveType.Bool:
            ctx.mips = templates.print_bool.format(expr=ctx.expr().mips)
        else:
            # in the SPIM print syscall, 1 is the service code for Int, 4 for String
            ctx.mips = templates.print_int_or_string.format(
                expr=ctx.expr().mips,
                service_code=1 if ctx.expr().type == PrimitiveType.Int else 4
            )

    # ---------------------------------------------------------------------------------
    # Partially provided for you - see lab instructions for suggested order
    # ---------------------------------------------------------------------------------

    def exitBody(self, ctx: NimbleParser.BodyContext):
        # TODO: extend to include varBlock
        ctx.mips = ctx.block().mips

    def exitAddSub(self, ctx: NimbleParser.AddSubContext):
        # TODO: extend for String concatenation
        ctx.mips = templates.add_sub.format(
            operation='add' if ctx.op.text == '+' else 'sub',
            expr0=ctx.expr(0).mips,
            expr1=ctx.expr(1).mips
        )

    def exitIf(self, ctx: NimbleParser.IfContext):
        # TODO: extend to support `else`
        ctx.mips = templates.if_.format(
            condition=ctx.expr().mips,
            true_block=ctx.block(0).mips,
            endif_label=self.unique_label('endif')
        )

    # ---------------------------------------------------------------------------------
    # Yours to implement - see lab instructions for suggested order
    # ---------------------------------------------------------------------------------

    def exitVarBlock(self, ctx: NimbleParser.VarBlockContext):
        pass

    def exitVarDec(self, ctx: NimbleParser.VarDecContext):
        pass

    def exitAssignment(self, ctx: NimbleParser.AssignmentContext):
        pass

    def exitWhile(self, ctx: NimbleParser.WhileContext):
        pass

    def exitNeg(self, ctx: NimbleParser.NegContext):
        pass

    def exitParens(self, ctx: NimbleParser.ParensContext):
        pass

    def exitCompare(self, ctx: NimbleParser.CompareContext):
        pass

    def exitVariable(self, ctx: NimbleParser.VariableContext):
        pass

    def exitMulDiv(self, ctx: NimbleParser.MulDivContext):
        pass
