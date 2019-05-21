# File: Simulator.py
# Name: Radha Natesan
# Date: 5/19/19
# Course: ECE 586 - Computer Architecture
# Desc: MIPS-lite simulator
# Usage: python Simulator.py

import sys
from utility import *

#Global variables
pc = 0		    #Program Counter
reg = [0] * 32	#Registers
P = []		    #Pipeline stages
I = []		    #Instructions
i_index = 0

#Class to store decoded instruction attributes
class Instruction:
	def __init__(self, rawInstr):
	    self.opcode = rawInstr[:6]
	    self.operands = rawInstr[6:]
	    self.rs = ""
	    self.rs_value = 0
	    self.rt = ""
	    self.rt_value = 0
	    self.rd = ""
	    self.rd_value = 0
	    self.imm = 0

def fetch():
	global i_index, p_index
	# Read input file
	I.insert(i_index,Instruction(bin(int(inFile.readline().strip(), 16))[2:].zfill(32)))
	P.insert(0,I[i_index])
	i_index = i_index + 1

	#Circular buffer
	if i_index == 5:
		i_index = 0

def decode():
	#decode the opcode and parse operands
	P[1].rs = int(P[1].operands[:5],2)
	P[1].rt = int(P[1].operands[5:10],2)
	if ISA[P[1].opcode]["Format"] == "R":
		P[1].rd = int(P[1].operands[10:15],2)
	else:
		P[1].imm = int(P[1].operands[10:],2)

	#Read source register values
	P[1].rs_value = reg[P[1].rs]
	P[1].rt_value = reg[P[1].rt]

	print("rs val rt val rd imm x is ", P[1].rs,P[1].rs_value,P[1].rt,P[1].rt_value,P[1].rd,P[1].imm)

def execute():
	#Perform ALU operation
	if ISA[P[2].opcode]["Type"] == "ARITHMETIC":
		if ISA[P[2].opcode]["Format"] == "R":
			result = eval("P[2].rs_value"+ISA[P[2].opcode]["func"]+"P[2].rt_value")
			P[2].rd_value = result
		else:
			result = eval("P[2].rs_value"+ISA[P[2].opcode]["func"]+"P[2].imm")
			P[2].rt_value = result
	
	print("result is ", result)
def memory():
	#decode the opcode and parse operands
	print('memory')
	
def writeback():
	#write the result to register
	if ISA[P[4].opcode]["Type"] == "ARITHMETIC":
		if ISA[P[4].opcode]["Format"] == "R":
			reg[P[4].rd] = P[4].rd_value
		else:
			reg[P[4].rt] = P[4].rt_value

	print(reg)

inFile = open("proj_trace.txt","r")

#IF stage
fetch()
P.insert(1,P[0])
P[0] = None

#ID stage
decode()
P.insert(2,P[1])
P[1] = None

#EX stage
execute()
P.insert(3,P[2])
P[2] = None

#MEM stage
memory()
P.insert(4,P[3])
P[3] = None

#WB stage
writeback()

inFile.close()
