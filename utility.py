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
    "000010" : {
        "Name" : "SUB",
        "Format" : "R",
        "Type"  : "ARITHMETIC",
        "func" : "-"
    },
    "000011" : {
        "Name" : "SUBI",
        "Format" : "I",
        "Type"  : "ARITHMETIC",
        "func" : "-"
    },
    "000100" : {
        "Name" : "MUL",
        "Format" : "R",
        "Type"  : "ARITHMETIC",
        "func" : "*"
    },
    "000101" : {
        "Name" : "MULI",
        "Format" : "I",
        "Type"  : "ARITHMETIC",
        "func" : "*"
    },
     "000110" : {

        "Name" : "OR",

        "Format" : "R",

        "Type"  : "LOGICAL",

        "func" : "|"
    },
    "000111" : {

        "Name" : "ORI",

        "Format" : "I",

        "Type"  : "LOGICAL",

        "func" : "|"
    },
     "001000" : {

        "Name" : "AND",

        "Format" : "R",

        "Type"  : "LOGICAL",

        "func" : "&"

    },
    "001001" : {
        "Name" : "ANDI",
        "Format" : "I",
        "Type"  : "LOGICAL",
        "func" : "&"
    },
    "001010" : {

        "Name" : "XOR",

        "Format" : "R",

        "Type"  : "LOGICAL",

        "func" : "^"

    },

    "001011" : {

        "Name" : "XORI",

        "Format" : "I",

        "Type"  : "LOGICAL",

        "func" : "^"

    },
    "001100" : {
        "Name" : "LDW",
        "Format" : "I",
        "Type"  : "MEMACCESS",
        "func" : "+"
    },
    "001101" : {
        "Name" : "STW",
        "Format" : "I",
        "Type"  : "MEMACCESS",
        "func" : "+"
    },
    "001110" : {
        "Name" : "BZ",
        "Format" : "I",
        "Type"  : "CONTROL",
        "func" : "+"
    },
    "001111" : {
        "Name" : "BEQ",
        "Format" : "I",
        "Type"  : "CONTROL",
        "func" : "+"
    },
    "010000" : {
        "Name" : "JR",
        "Format" : "I",
        "Type"  : "CONTROL",
        "func" : "+"
    },
    "010001" : {
        "Name" : "HALT",
        "Format" : "I",
        "Type"  : "CONTROL",
        "func" : ""
    }
}
