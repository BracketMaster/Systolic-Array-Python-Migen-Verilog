import os
from migen import *
import numpy as np
from systolic_array import Systolic_Array

weights= np.array([
[0,1,2,3],
[4,5,6,7],
[8,9,10,11],
[12,13,14,15]
])

inputs= np.array([
[0,1,2,3],
[4,5,6,7],
[8,9,10,11],
[12,13,14,15]
])

WIDTH = 16
rows = cols = 4
_file = "systolic_array.vcd"
_write_dir = '_sim_out'

def set_ports(val_list, port_list):
	"""
	sets the input in the port_list
	to the values provided in the val_list
	"""
	for index,value in enumerate(val_list):
		yield port_list[index].eq(value)

def peek_array(array):
	arr = np.zeros((4,4))
	for r in range(rows):
		for c in range(cols):
			arr[r,c] = (yield array[r][c].SUM)

	print(arr)
	print()

			
def systolic_array_test(dut):
	#multiply the weights and inputs matrix
	#solution accumulates in the SUM signal of each cell of the systolic array
	cycle_count=0
	for cycle in range(4):
		yield from set_ports(inputs[:,cycle].tolist(),dut.list_L_in)
		yield from set_ports(weights[cycle,:].tolist(),dut.list_Top_in)
		yield
		cycle_count = cycle_count + 1

	#after we have dispatched our weight and input matrix, we hold 
	#the systolic array inputs to 0 to prevent further accumulation
	#values will fill in across the diagonals of the systolic array
	yield from set_ports([0,0,0,0],dut.list_Top_in)
	yield from set_ports([0,0,0,0],dut.list_L_in)

	for count in range(7):
		yield
		cycle_count = cycle_count + 1
	
	print("SYSTOLIC ARRAY OUTPUT:")
	yield from peek_array(dut.arr)
	print("NUMPY OUTPUT:")
	print(np.matmul(inputs,weights))
	print()
	print("EXECUTED FOR {} CYCLES".format(cycle_count))


if __name__ == "__main__":
	if(_write_dir not in os.listdir(os.getcwd())):
		os.makedirs(_write_dir)
	dut = Systolic_Array(rows=rows,cols=cols,WIDTH=WIDTH)
	run_simulation(dut, systolic_array_test(dut), vcd_name=_write_dir + "/" + _file)
	print("Verilog written to " + _write_dir + "/" + _file)	
