import sys

#Request Type
ISA = {
    "000000" : {
        "Name" : "ADD",
        "Format" : "R",
        "Type"  : "ARITHMETIC",
        "func" : "+"
    },
    "000001" : {
        "Name" : "ADDI",
        "Format" : "I",
        "Type"  : "ARITHMETIC",
        "func" : "+"
    },
    "010001" : {
        "Name" : "HALT",
        "Format" : "I",
        "Type"  : "CONTROL",
        "func" : ""
    }
}
