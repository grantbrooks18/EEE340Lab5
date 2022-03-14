"""
Templates used by the nimble2MIPS.py module

Authors: TODO: your names here

Date: TODO: submission date here
"""

script = """\
.data

true_string: .asciiz "true"
false_string: .asciiz "false"
    
{string_literals}

.text

true_false_string:
beq    $t0 $zero choose_false
la     $a0 true_string
j      end_true_false_string
choose_false:
la     $a0 false_string
end_true_false_string:
jr     $ra

main: 

{main}

halt:

li $v0 10
syscall
"""

add_sub = """\
{expr0}
sw     $t0 0($sp) 
addiu  $sp $sp -4 
{expr1}
lw     $s1 4($sp) 
{operation}    $t0 $s1 $t0 
addiu  $sp $sp 4
"""

if_ = """\
{condition}
li     $t1 0
beq    $t0 $t1 {endif_label}
{true_block}
{endif_label}:
"""

print_int_or_string = """\
{expr}
move   $a0 $t0
li     $v0 {service_code}
syscall
"""

# for printing booleans, we want to print true/false rather than 1/0
# so we start by loading the corresponding string address in to $a0
# using the true_false_string subroutine
#
# alternate approach: embed the true_false_subroutine code directly
# in the `print_bool` template, removing the `jr` instruction at the
# end and with unique, dynamically generated `choose_false` and
# `end_true_false_string` labels

print_bool = """\
{expr}
jal    true_false_string
li     $v0 4
syscall
"""
