.data

true_string: .asciiz "true"
false_string: .asciiz "false"
    
string_0: .asciiz "\nhello, world\n"
string_1: .asciiz "1\tafter-tab '~ 6\" 7\\ \" "
string_2: .asciiz "\n"
string_3: .asciiz "\n"

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

li     $t0 9999999
move   $a0 $t0
li     $v0 1
syscall

la     $t0 string_0
move   $a0 $t0
li     $v0 4
syscall

la     $t0 string_1
move   $a0 $t0
li     $v0 4
syscall

la     $t0 string_2
move   $a0 $t0
li     $v0 4
syscall

li     $t0 1
jal    true_false_string
li     $v0 4
syscall

la     $t0 string_3
move   $a0 $t0
li     $v0 4
syscall

li     $t0 0
jal    true_false_string
li     $v0 4
syscall


halt:

li $v0 10
syscall
