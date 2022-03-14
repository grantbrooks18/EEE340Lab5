"""
Compiles all Nimble files found in the nimble_source subdirectory, and
generates corresponding MIPS assembler files in a generated_mips subdirectory
(creating the subdirectory if necessary).

If syntax or semantic errors are found, displays them to the console and writes
them to the target output file. In these cases, code generation will never
be executed.

If errors occur in the code generation phase, will normally be output to the
console only.

Author: Greg Phillips

Version: 2022-03-14
"""

import os
import sys

from antlr4 import ParseTreeWalker
from generic_parser import parse, SyntaxErrors
from nimble import NimbleParser, NimbleLexer
from nimble2MIPS import MIPSGenerator
from semantics import do_semantic_analysis, NimbleSemanticErrors


def compile_nimble_source_files():
    source_dir = os.path.join(os.getcwd(), 'nimble_source')
    output_dir = os.path.join(os.getcwd(), 'generated_mips')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    source_files = os.listdir(source_dir)
    for name in source_files:
        error_found = False
        output = ''
        try:
            nimble_filename = os.path.join(source_dir, name)
            tree = parse(nimble_filename, 'script', NimbleLexer, NimbleParser, from_file=True)
            do_semantic_analysis(tree)
            ParseTreeWalker().walk(MIPSGenerator(), tree)
            output = tree.mips
        except FileNotFoundError as fnf:
            output = fnf
            error_found = True
        except SyntaxErrors as se:
            output = f'\nSyntax error(s) in {name}\n{se}'
            error_found = True
        except NimbleSemanticErrors as nse:
            output = f'\nSemantic error(s) in {name}\n{nse}'
            error_found = True
        finally:
            if error_found:
                print(output, file=sys.stderr)
            mips_filename = os.path.join(output_dir, f'{name.split(".")[0]}.asm')
            with open(mips_filename, 'w') as mf:
                mf.write(output)


if __name__ == '__main__':
    compile_nimble_source_files()
