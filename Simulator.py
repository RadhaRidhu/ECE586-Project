# File: Simulator.py
# Name: Radha Natesan, Alpa Chaudhary
# Date: 5/19/19
# Course: ECE 586 - Computer Architecture
# Desc: MIPS-lite simulator test
# Usage: python Simulator.py <0 (without forwarding)/1 (with forwarding)>

import sys
from utility import *
import linecache

#Global variables
pc = 1		    	#Program Counter
reg = [None] * 32	#Registers
P = []	    		#Pipeline stages
I = []				#Instructions
Mem = {}			#List of Memory altered
i_index = 0
dest_reg = [None] * 32 #Store the destination registers values to fix RAW hazard
halt = 0 			#halt flag
hazard = 0			#hazard flag
cycles = 0 			#cycle count
branch_stall = 0 	#Branch penalty flag
dest = [] 			#Store the destination registers to fix RAW hazard

#Instruction count
I_count = 0			#Instructions
A_count = 0			#Arithmetic Instructions
L_count = 0			#Logical Instructions
M_count = 0			#Memory access Instructions
C_count = 0			#Control Instructions 
S_count = 0  		#Stall
BP_count = 0 		#Branch penalty count
H_count = 0			#Hazard count

input_trace = 'final_proj_trace.txt'
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

#Fetch stage. Read instruciton from the memory corresponding to the PC and store in pipeline array
def fetch():
	global i_index, p_index, pc
	# Read input trace
	I.insert(i_index,Instruction(bin(int(linecache.getline(input_trace, pc).strip(), 16))[2:].zfill(32)))
	pc = pc + 1

	#Insert into pipeline array
	del P[0]
	P.insert(0,I[i_index])
	i_index = i_index + 1
	
	#Circular buffer
	if i_index == 5:
		i_index = 0

#Decode stage. Decode the Opcode and read source operand values. This stage also checks for any RAW hazard and stalls
#If required.
def decode():
	global C_count,S_count,halt,hazard,H_count
	#If HALT command is found, do nothing
	if ISA[P[1].opcode]["Name"] == "HALT":
		halt = 1
		return
	#Parse operands
	P[1].rs = int(P[1].operands[:5],2)
	P[1].rt = int(P[1].operands[5:10],2)
	if ISA[P[1].opcode]["Format"] == "R":
		P[1].rd = int(P[1].operands[10:15],2)
		destination = P[1].rd
		print (ISA[P[1].opcode]["Name"] + " R" + str(P[1].rd) + ", R" +  str(P[1].rs) + ", R" +  str(P[1].rt))
	else:
		P[1].imm = twos_complement(int(P[1].operands[10:],2),16)
		destination = P[1].rt
		print (ISA[P[1].opcode]["Name"] + " R" + str(P[1].rt) + ", R" +  str(P[1].rs) + ","+  str(P[1].imm))

	#forward logic
	if fwd_flag and P[1].rs in dest and dest_reg[P[1].rs] != None:
		P[1].rs_value = dest_reg[P[1].rs]
		dest.remove(P[1].rs)
		dest_reg[P[1].rs] = None
	else:
		P[1].rs_value = reg[P[1].rs]

	if fwd_flag and dest_reg[P[1].rt] != None and ((P[1].rt in dest) and ((ISA[P[1].opcode]["Format"] == "R") or (ISA[P[1].opcode]["Name"] == "BEQ"))):
		P[1].rt_value = dest_reg[P[1].rt]
		dest.remove(P[1].rt)
		dest_reg[P[1].rt] = None
	else:
		#Read source register values	
		P[1].rt_value = reg[P[1].rt]

	#If RAW HAZARD, return from decode
	if ((ISA[P[1].opcode]["Format"] == "R") and ((P[1].rs in dest) or (P[1].rt in dest))) \
	or ((ISA[P[1].opcode]["Format"] == "I") and (P[1].rs in dest)) \
	or ((ISA[P[1].opcode]["Name"] == "BEQ") and (P[1].rt in dest)):
		S_count = S_count + 1
		if (hazard == 0):
			H_count = H_count + 1
			hazard = 1
		print ('Hazard $$$$$$')
		return 1;

	if ISA[P[1].opcode]["Name"] != "STW" and  ISA[P[1].opcode]["Type"] != "CONTROL" :
		dest.append(destination)


	return 0;

#Execute stage. Perform ALU operation on the operand.
def execute():
	global pc,BP_count,branch_stall,dest_reg
	#If HALT command is found, do nothing
	if ISA[P[2].opcode]["Name"] == "HALT":
		return

	if ISA[P[2].opcode]["Format"] == "R":
		result = eval("P[2].rs_value"+ISA[P[2].opcode]["func"]+"P[2].rt_value")
		P[2].rd_value = result
		destination = P[2].rd
		dest_reg[P[2].rd] = P[2].rd_value
	else:
		if ISA[P[2].opcode]["Name"] == "BEQ" and P[2].rs_value == P[2].rt_value:
			pc = pc + P[2].imm -2
			P[1] = None
			BP_count = BP_count + 2
			branch_stall = 2
		if ISA[P[2].opcode]["Name"] == "BZ" and P[2].rs_value == 0:
			pc = pc + P[2].imm-2
			P[1] = None
			BP_count = BP_count + 2
			branch_stall = 2
		if ISA[P[2].opcode]["Name"] == "JR":
			pc = P[2].rs_value//4 + 1
			P[1] = None
			BP_count = BP_count + 2
			branch_stall = 2
		if ISA[P[2].opcode]["Name"] == "LDW" or ISA[P[2].opcode]["Name"] == "STW":
			P[2].Address = P[2].rs_value + P[2].imm 
		else:
			result = eval("P[2].rs_value "+ISA[P[2].opcode]["func"]+" P[2].imm")
			P[2].rt_value = result
			destination = P[2].rt
			dest_reg[P[2].rt] = P[2].rt_value
			
#Memory stage. Load/Store data from/to Memory
def memory():
	global Mem
	#If HALT command is found, do nothing
	if ISA[P[3].opcode]["Name"] == "HALT":
		return
	#Memory access for load/store instructions
	if ISA[P[3].opcode]["Name"] == "LDW":
		if str(P[3].Address) in list(Mem.keys()):
			P[3].rt_value = Mem[str(P[3].Address)]	
		else:
			P[3].rt_value = twos_complement(int(linecache.getline(input_trace, P[3].Address//4 +1).strip(), 16),32)
		#Forwarding Mem -> Ex
		if fwd_flag:
			dest_reg[P[3].rt] = P[3].rt_value

	if ISA[P[3].opcode]["Name"] == "STW":
		Mem[str(P[3].Address)] = reg[P[3].rt]

#Write back stage. Store the ALU result in the destination register.	
def writeback():
	global A_count,L_count,M_count,C_count,I_count
	#If HALT command is found, print report and exit
	if ISA[P[4].opcode]["Name"] == "HALT":
		C_count = C_count + 1
		I_count = I_count + 1
		printReport()
		sys.exit()
	#write the result to register
	if ISA[P[4].opcode]["Type"] != "CONTROL" and ISA[P[4].opcode]["Name"] != "STW":
		if ISA[P[4].opcode]["Format"] == "R":
			reg[P[4].rd] = P[4].rd_value
			#Remove destination register from list
			if (P[4].rd in dest):
				dest.remove(P[4].rd)
		else:
			reg[P[4].rt] = P[4].rt_value
			#Remove destination register from list
			if (P[4].rt in dest):
				dest.remove(P[4].rt)

	if ISA[P[4].opcode]["Type"] == "ARITHMETIC":
		A_count = A_count + 1
	if ISA[P[4].opcode]["Type"] == "LOGICAL":
		L_count = L_count + 1
	if ISA[P[4].opcode]["Type"] == "MEMACCESS":
		M_count = M_count + 1
	if ISA[P[4].opcode]["Type"] == "CONTROL":
		C_count = C_count + 1
	I_count = I_count + 1
	
#Print report
def printReport():
	print ('Total number of instructions:' + str(I_count))
	print ('Arithmetic instructions:'+ str(A_count))
	print ('Logical instructions:'+ str(L_count))
	print ('Memory access instructions:'+ str( M_count))
	print ('Control transfer instructions:'+ str(C_count))
  
	print ('\nFinal Register state:')
	print ('Program Counter :' + str( (pc-1)*4))
	for i in range(len(reg)):
		if reg[i] != None and i !=0:
			print 'R',i,':',reg[i]
	print '\nFinal Memory state:'
	for key in sorted(Mem):
		print 'Address:',key,', Contents:',Mem[key]
	if fwd_flag:
		print('\nTiming Simulator with forwarding:')
	else:
		print('\nTiming Simulator without forwarding:')
	print('Execution time in cycles: ' + str(cycles))
	print('Total stalls for data hazard: ' + str(S_count))
	print('Branch Penalty: '+str(BP_count))
	print('Pipeline fill and drain delay: '+str(4))
	print('Total data hazard: '+str(H_count))
	print('Average stalls penalty per hazard: '+str(float(S_count)/H_count))
	print('\n')

#Convert decimal to signed integer using 2's compliment
def twos_complement(value,bits):
	if value & (1 << (bits-1)):
		value -= 1 << bits

	return value

#Retrieve the forward flag from user input
fwd_flag = int(sys.argv[1])

reg[0] = 0

P.insert(0,None)
P.insert(1,None)
P.insert(2,None)
P.insert(3,None)
P.insert(4,None)

#Start pipelining
while 1 : 
	cycles = cycles + 1
	if P[4] != None:
		#WB stage
		writeback()
		P[4]=None

	if P[3] != None:
		#MEM stage
		memory()
		del P[4]
		P.insert(4,P[3])
		P[3]=None
	

	if P[2] != None:		
		#EX stage
		execute()
		del P[3]
		P.insert(3,P[2])
		P[2]=None
	
	if branch_stall > 0:
		branch_stall=branch_stall-1

	if P[1] != None and branch_stall == 0:
		stall = decode()
		#ID stage
		if stall:
			continue
		del P[2]
		P.insert(2,P[1])
		P[1]=None

	if P[0] == None and not halt and branch_stall == 0:
		#IF stage
		hazard = 0
		fetch()
		del P[1]
		P.insert(1,P[0])
		P[0] = None


	

	

	

