.data

true_string: .asciiz "true"
false_string: .asciiz "false"
    
string_1: .asciiz "\n"
string_3: .asciiz "done"

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

li     $t0 1
li     $t1 0
beq    $t0 $t1 endif_0
li     $t0 1
move   $a0 $t0
li     $v0 1
syscall

endif_0:

la     $t0 string_1
move   $a0 $t0
li     $v0 4
syscall

li     $t0 0
li     $t1 0
beq    $t0 $t1 endif_2
li     $t0 99
move   $a0 $t0
li     $v0 1
syscall

endif_2:

la     $t0 string_3
move   $a0 $t0
li     $v0 4
syscall


halt:

li $v0 10
syscall
