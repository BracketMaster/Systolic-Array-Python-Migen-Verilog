import os
import sys
from migen import *
from migen.fhdl import verilog
from systolic_array import Systolic_Array

WIDTH=8
rows = cols = 4
_write_dir = '_rtl_out'
_file = "systolic_array.v"

dut = Systolic_Array(WIDTH=WIDTH,rows=4,cols=4)

#does an RTL output directory already exist?
if(_write_dir not in os.listdir(os.getcwd())):
	os.makedirs(_write_dir)

#populate rtl input list
input_list = []
for r in range(rows):
	input_list.append(dut.list_L_in[r])
for c in range(cols):
	input_list.append(dut.list_Top_in[c])

#populate rtl output list
output_list = []
for r in range(rows):
	for c in range(cols):
		output_list.append(dut.arr[r][c].SUM)

port_list = set(input_list + output_list)
verilog.convert(dut, port_list).write(_write_dir + '/' + _file)
print("Verilog written to " + _write_dir + "/" + _file)



