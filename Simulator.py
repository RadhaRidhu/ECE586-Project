# File: Simulator.py
# Name: Radha Natesan
# Date: 5/19/19
# Course: ECE 586 - Computer Architecture
# Desc: MIPS-lite simulator test
# Usage: python Simulator.py

import sys
from utility import *
import linecache

#Global variables
pc = 1		    #Program Counter
reg = [None] * 32	#Registers
P = []		    #Pipeline stages
I = []		    #Instructions
Mem = {}
i_index = 0

#Instruction count
I_count = 0
A_count = 0
L_count = 0
M_count = 0
C_count = 0

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
	    self.Address = 0

def fetch():
	global i_index, p_index, pc, I_count
	# Read input file
	I.insert(i_index,Instruction(bin(int(linecache.getline('proj_trace.txt', pc).strip(), 16))[2:].zfill(32)))
	pc = pc + 1
	P.insert(0,I[i_index])
	i_index = i_index + 1
	I_count = I_count + 1
	#Circular buffer
	if i_index == 5:
		i_index = 0

def decode():
	global A_count,L_count,M_count,C_count
	#decode the opcode and parse operands
	#If HALT command is found, print result and exit
	if ISA[P[1].opcode]["Name"] == "HALT":
		C_count = C_count + 1
		printReport()
		inFile.close()
		sys.exit()

	P[1].rs = int(P[1].operands[:5],2)
	P[1].rt = int(P[1].operands[5:10],2)
	if ISA[P[1].opcode]["Format"] == "R":
		P[1].rd = int(P[1].operands[10:15],2)
		print (ISA[P[1].opcode]["Name"] , " R" , P[1].rd , ", R" ,  P[1].rs , ", R" ,  P[1].rt)
	else:
		P[1].imm = int(P[1].operands[10:],2)
		print (ISA[P[1].opcode]["Name"] , " R" , P[1].rt , ", R" ,  P[1].rs , ",",  P[1].imm)

	#Read source register values
	P[1].rs_value = reg[P[1].rs]
	P[1].rt_value = reg[P[1].rt]

	if ISA[P[1].opcode]["Type"] == "ARITHMETIC":
		A_count = A_count + 1
	if ISA[P[1].opcode]["Type"] == "LOGICAL":
		L_count = L_count + 1
	if ISA[P[1].opcode]["Type"] == "MEMACCESS":
		M_count = M_count + 1
	if ISA[P[1].opcode]["Type"] == "CONTROL":
		C_count = C_count + 1


def execute():
	#Perform ALU operation
	global pc
	if ISA[P[2].opcode]["Format"] == "R":
		result = eval("P[2].rs_value"+ISA[P[2].opcode]["func"]+"P[2].rt_value")
		P[2].rd_value = result
	else:
		if ISA[P[2].opcode]["Name"] == "BEQ" and P[2].rs_value == P[2].rt_value:
			pc = pc + P[2].imm -1
		if ISA[P[2].opcode]["Name"] == "BZ" and P[2].rs_value == 0:
			pc = pc + P[2].imm-1 
		if ISA[P[2].opcode]["Name"] == "JR":
			pc = P[2].rs_value//4 + 1
		if ISA[P[2].opcode]["Name"] == "LDW" or ISA[P[2].opcode]["Name"] == "STW":
			P[2].Address = P[2].rs_value + P[2].imm 
		else:
			result = eval("P[2].rs_value"+ISA[P[2].opcode]["func"]+"P[2].imm")
			P[2].rt_value = result
			
	
def memory():
	global Mem
	#Memory access for load/store instructions
	print (linecache.getline('proj_trace.txt', P[3].Address))
	if ISA[P[3].opcode]["Name"] == "LDW":
		if str(P[3].Address) in list(Mem.keys()):
			P[3].rt_value = Mem[str(P[3].Address)]
		else:
			P[3].rt_value = int(linecache.getline('proj_trace.txt', P[3].Address//4 +1).strip(), 16)
	if ISA[P[3].opcode]["Name"] == "STW":
		print (P[3].Address)
		Mem[str(P[3].Address)] = reg[P[3].rt]
	
def writeback():
	#write the result to register
	if ISA[P[4].opcode]["Type"] != "CONTROL" and ISA[P[4].opcode]["Name"] != "STW":
		if ISA[P[4].opcode]["Format"] == "R":
			reg[P[4].rd] = P[4].rd_value
		else:
			reg[P[4].rt] = P[4].rt_value

	#print(reg)
def printReport():

	print ('Total number of instructions:', I_count)
	print ('Arithmetic instructions:', A_count)
	print ('Logical instructions:', L_count)
	print ('Memory access instructions:', M_count)
	print ('Control transfer instructions:', C_count)
	
	print(reg)
	print(Mem)

#Convert 16 bit decimal to signed integer
def twos_complement(value):
	if value & (1 << (16-1)):
		value -= 1 << 16
	return value

inFile = open("proj_trace.txt","r")

reg[0] = 0

	
while 1 : 
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
	P[4] = None

