from migen import *

class Buffer(Module):
	def __init__(self,WIDTH=8):
		self.input = Signal((WIDTH,True))
		self.output = Signal((WIDTH,True))
		self.sync += self.output.eq(self.input)

class Fifo(Module):
	def __init__(self,LENGTH=1,WIDTH=8):
		self.In = Signal((WIDTH,True))
		self.Out = Signal((WIDTH,True))
		if(LENGTH>1):
			#fifo = LENGTH*[Buffer(WIDTH=WIDTH)]
			fifo = []
			for n in range(LENGTH):
				fifo.append(Buffer(WIDTH=WIDTH))
			self.submodules += fifo
			for index in range(LENGTH):
					if(index >0):
						self.comb += fifo[index].input.eq(fifo[index-1].output)
			self.comb += fifo[0].input.eq(self.In)
			self.comb += self.Out.eq(fifo[-1].output)
		elif (LENGTH == 1):
			buf = Buffer(WIDTH=WIDTH)
			self.submodules += buf
			self.comb += buf.input.eq(self.In)
			self.comb += self.Out.eq(buf.output)
		else:
			self.comb += self.Out.eq(self.In)
			

class Cell(Module):
	def __init__(self,WIDTH=8):
		#inputs
		self.Top_in = Signal((WIDTH,True))
		self.L_in = Signal((WIDTH,True))

		#outputs
		self.F_down = Signal((WIDTH,True))
		self.F_right = Signal((WIDTH,True))

		self.SUM = Signal((WIDTH,True))
		self.sync += self.SUM.eq(self.SUM+(self.Top_in*self.L_in))
		self.sync += self.F_right.eq(self.L_in)
		self.sync += self.F_down.eq(self.Top_in)

class Systolic_Array(Module):
	def __init__(self,rows,cols,WIDTH=8):

		#access the inputs to the left of the systolic array
		#with (yield Systolic_Array.list_L_in[n].eq(some_value)) to set
		#a value during testbench
		#with (yield Systolic_Array.list_L_in[n].eq(some_value)) to read
		#a value during testbench
		self.list_L_in = []
		for n in range(rows):
			L_in = Signal((WIDTH,True))
			self.list_L_in.append(L_in)

		self.list_Top_in = []
		for n in range(rows):
			Top_in = Signal((WIDTH,True))
			self.list_Top_in.append(Top_in)

		#instantiate cells in systolic array
		self.arr = arr = []
		for r in range(rows):
			temp = []
			for c in range(cols):
				temp.append(Cell(WIDTH=WIDTH))
			arr.append(temp)

		for r in range(rows):
			for c in range(cols):
				self.submodules += arr[r][c]

		#wire cells in systolic array to one another
		for r in range(rows):
			for c in range(cols):
				if(c>0):
					self.comb += arr[r][c].L_in.eq(arr[r][c-1].F_right)
				if(r>0):
					self.comb += arr[r][c].Top_in.eq(arr[r-1][c].F_down)
		
		#wire list_L_in to left input of systolic array
		for r in range(rows):
			fifo_inst = Fifo(WIDTH=WIDTH,LENGTH=r)
			self.submodules += fifo_inst
			self.comb += fifo_inst.In.eq(self.list_L_in[r])
			self.comb += arr[r][0].L_in.eq(fifo_inst.Out)

		#wire list_Top_in to left input of systolic array
		for c in range(cols):
			fifo_inst = Fifo(WIDTH=WIDTH,LENGTH=c)
			self.submodules += fifo_inst
			self.comb += fifo_inst.In.eq(self.list_Top_in[c])
			self.comb += arr[0][c].Top_in.eq(fifo_inst.Out)
