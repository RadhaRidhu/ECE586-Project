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
dest_reg = [None] * 32	#dest Registers to store value for forwarding
P = []	    #Pipeline stages
I = []		    #Instructions
Mem = {}
i_index = 0
dest = [] #Store the destination registers to fix RAW hazard
dest_mem = [] #Store the destination for memory in use for LDW harzrd
halt = 0
cycles = 0
stall=0

 
#Instruction count
I_count = 0
A_count = 0
L_count = 0
M_count = 0
C_count = 0
S_count = 0  #Stall count
BP_count = 0 #Branch penalty count

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
	global i_index, p_index, pc
	# Read input file
	I.insert(i_index,Instruction(bin(int(linecache.getline('proj_trace.txt', pc).strip(), 16))[2:].zfill(32)))
	pc = pc + 1
	del P[0]
	P.insert(0,I[i_index])
	i_index = i_index + 1
	
	#Circular buffer
	if i_index == 5:
		i_index = 0

def decode():
	global C_count,halt
	#decode the opcode and parse operands
	#If HALT command is found, print result and exit
	if ISA[P[1].opcode]["Name"] == "HALT":
		halt = 1
		return
		
	P[1].rs = int(P[1].operands[:5],2)
	P[1].rt = int(P[1].operands[5:10],2)
	if ISA[P[1].opcode]["Format"] == "R":
		P[1].rd = int(P[1].operands[10:15],2)
		print (ISA[P[1].opcode]["Name"] + " R" + str(P[1].rd) + ", R" +  str(P[1].rs) + ", R" +  str(P[1].rt))
	else:
		P[1].imm = int(P[1].operands[10:],2)
		print (ISA[P[1].opcode]["Name"] + " R" + str(P[1].rt) + ", R" +  str(P[1].rs) + ","+  str(P[1].imm))

		
def execute():
	#Perform ALU operation
	global pc,BP_count,S_count
	if ISA[P[2].opcode]["Name"] == "HALT":
		return

	if ((ISA[P[2].opcode]["Format"] == "R") and ((P[2].rs in dest_mem) or (P[2].rt in dest_mem))) \
	or ((ISA[P[2].opcode]["Format"] == "I") and (P[2].rs in dest_mem)) \
	or ((ISA[P[2].opcode]["Name"] == "BEQ") and (P[2].rt in dest_mem)):
		print ('Hazard***')
		S_count = S_count + 1
		print (dest_mem)
		return 1;
	
#If RAW HAZARD, return from decode
	if P[2].rs in dest:
		P[2].rs_value = dest_reg[P[2].rs]
	else:
		P[2].rs_value = reg[P[2].rs]
	#Read source register values

	if ((P[2].rt in dest) and (ISA[P[2].opcode]["Format"] == "R")):
		P[2].rt_value = dest_reg[P[2].rt]
	else:
		P[2].rt_value = reg[P[2].rt]

	
	if ISA[P[2].opcode]["Format"] == "R":
		result = eval("P[2].rs_value"+ISA[P[2].opcode]["func"]+"P[2].rt_value")
		P[2].rd_value = result
		destination = P[2].rd
		dest_reg[P[2].rd] = P[2].rd_value
		dest.append(destination)		
	else:
		if ISA[P[2].opcode]["Name"] == "BEQ" and P[2].rs_value == P[2].rt_value:
			pc = pc + P[2].imm -2
			print (pc)
			P[1] = None
			BP_count = BP_count + 2
		if ISA[P[2].opcode]["Name"] == "BZ" and P[2].rs_value == 0:
			pc = pc + P[2].imm-2 
			P[1] = None
			BP_count = BP_count + 2
		if ISA[P[2].opcode]["Name"] == "JR":
			print ('Jump Register is ' + str(P[2].rs_value))
			pc = P[2].rs_value//4 + 1
			print (pc)
			P[1] = None
			BP_count = BP_count + 2
		if ISA[P[2].opcode]["Name"] == "LDW" or ISA[P[2].opcode]["Name"] == "STW":
			P[2].Address = P[2].rs_value + P[2].imm 					
		else:
			print ("P[2].rs_value "+ISA[P[2].opcode]["func"]+" P[2].imm")
			result = eval("P[2].rs_value "+ISA[P[2].opcode]["func"]+" P[2].imm")
			P[2].rt_value = result
			destination = P[2].rt
			dest_reg[P[2].rt] = P[2].rt_value
			dest.append(destination)

	return 0;	
	
def memory():
	global Mem
	if ISA[P[3].opcode]["Name"] == "HALT":
		return
	#Memory access for load/store instructions
	print (linecache.getline('proj_trace.txt', P[3].Address))
	if ISA[P[3].opcode]["Name"] == "LDW":
		if str(P[3].Address) in list(Mem.keys()):
			P[3].rt_value = Mem[str(P[3].Address)]
			destination = P[3].rt
			dest_reg[P[3].rt] = P[3].rt_value
			dest.append(destination)	
			dest_mem.append(destination)
		else:
			P[3].rt_value = twos_complement(int(linecache.getline('proj_trace.txt', P[3].Address//4 +1).strip(), 16))
			destination = P[3].rt
			dest_reg[P[3].rt] = P[3].rt_value
			dest.append(destination)
			dest_mem.append(destination)
	if ISA[P[3].opcode]["Name"] == "STW":
		print (P[3].Address)
		Mem[str(P[3].Address)] = reg[P[3].rt]
			
def writeback():
	global A_count,L_count,M_count,C_count,I_count
	if ISA[P[4].opcode]["Name"] == "HALT":
		print ('Halting')
		C_count = C_count + 1
		I_count = I_count + 1
		printReport()
		inFile.close()
		sys.exit()
	#write the result to register
	if ISA[P[4].opcode]["Type"] != "CONTROL" and ISA[P[4].opcode]["Name"] != "STW":
		if ISA[P[4].opcode]["Format"] == "R":
			reg[P[4].rd] = P[4].rd_value
			#Remove destination register from list
			dest.remove(P[4].rd)
			if P[4].rd in dest_mem:
				dest_mem.remove(P[4].rd)
		else:
			reg[P[4].rt] = P[4].rt_value
			#Remove destination register from list
			dest.remove(P[4].rt)
			if P[4].rt in dest_mem:
				dest_mem.remove(P[4].rt)			

	if ISA[P[4].opcode]["Type"] == "ARITHMETIC":
		A_count = A_count + 1
	if ISA[P[4].opcode]["Type"] == "LOGICAL":
		L_count = L_count + 1
	if ISA[P[4].opcode]["Type"] == "MEMACCESS":
		M_count = M_count + 1
	if ISA[P[4].opcode]["Type"] == "CONTROL":
		C_count = C_count + 1
	I_count = I_count + 1
	

	#print(reg)
def printReport():
	print ('Total number of instructions:', I_count)
	print ('Arithmetic instructions:', A_count)
	print ('Logical instructions:', L_count)
	print ('Memory access instructions:', M_count)
	print ('Control transfer instructions:', C_count)
  
	print ('\nFinal Register state:')
	print ('Program Counter :' , (pc-1)*4)
	for i in range(len(reg)):
		if reg[i] != None:
			print ('R',i,':',reg[i])
	print ('\nFinal Memory state:')
	for key in Mem:
		print ('Address:',key,', Contents:',Mem[key])

	print('\nTiming Simulator without forwarding:')
	print('Execution time in cycles: ' + str(cycles))
	print('Total stalls: ' + str(S_count))
	print('Branch Penalty: '+str(BP_count))
	print('Pipeline fill and drain delay: '+str(4))
	print('\n')

#Convert 16 bit decimal to signed integer
def twos_complement(value):
	if value & (1 << (16-1)):
		value -= 1 << 16
	return value

inFile = open("proj_trace.txt","r")

reg[0] = 0

P.insert(0,None)
P.insert(1,None)
P.insert(2,None)
P.insert(3,None)
P.insert(4,None)

while 1 : 
	cycles = cycles + 1

	if P[4] != None:
		#WB stage
		print ("wb")
		writeback()
		P[4]=None

	if P[3] != None:
		#MEM stage
		print("mem")
	
		memory()
		del P[4]
		P.insert(4,P[3])
		P[3]=None
	

	if P[2] != None:		
		#EX stage
		print("execute")
		
		stall = execute()
		if stall:
			continue		
		del P[3]
		P.insert(3,P[2])		
		P[2]=None

	if P[1] != None:
		print("decode")
		decode()
		#ID stage
		del P[2]
		P.insert(2,P[1])
		P[1]=None

	if P[0] == None and not halt:
		#IF stage
		fetch()
		del P[1]
		P.insert(1,P[0])
		P[0] = None


	print('current cycle:',cycles)
	

	

	

