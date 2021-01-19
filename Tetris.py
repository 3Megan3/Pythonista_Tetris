from scene import *
from random import randrange
from time import time

red = [[[-1,1],[0,0],[0,1],[1,0]],[[-1,0],[-1,1],[0,1],[0,2]],[[-1,2],[0,1],[0,2],[1,1]],[[0,0],[0,1],[1,1],[1,2]]]
orange = [[[-1,2],[0,0],[0,1],[0,2]],[[-1,1],[0,1],[1,1],[1,2]],[[0,0],[0,1],[0,2],[1,0]],[[-1,0],[-1,1],[0,1],[1,1]]]
yellow = [[[0,0],[0,1],[1,0],[1,1]] for x in range(4)]
lightgreen = [[[-1,0],[0,0],[0,1],[1,1]],[[-1,1],[-1,2],[0,0],[0,1]],[[-1,1],[0,1],[0,2],[1,2]],[[0,1],[0,2],[1,0],[1,1]]]
cyan = [[[-1,2],[0,2],[1,2],[2,2]],[[1,0],[1,1],[1,2],[1,3]],[[-1,1],[0,1],[1,1],[2,1]],[[0,0],[0,1],[0,2],[0,3]]]
blue = [[[-1,0],[-1,1],[-1,2],[0,2]],[[-1,2],[0,2],[1,2],[1,1]],[[0,0],[1,0],[1,1],[1,2]],[[-1,0],[-1,1],[0,0],[1,0]]]
purple = [[[-1,1],[0,0],[0,1],[1,1]],[[-1,1],[0,0],[0,1],[0,2]],[[-1,1],[0,1],[0,2],[1,1]],[[0,0],[0,1],[0,2],[1,1]]]
blocks = [red, orange, yellow, lightgreen, cyan, blue, purple]
colors = ["red","orange","yellow","lightgreen","cyan","blue","purple"]

fpc = [48,43,38,33,28,23,18,13,8,6,5,5,5,4,4,4,3,3,3,2,2,2,2,2,2,2,2,2,2,1]

##################################################################################

class MyScene (Scene):
	def setup(self):
		self.first = True
		self.newgame()

	def newgame(self):
		self.w = int(self.size.w*3/4+2)
		self.h = int(self.size.w*3/2+2)
		self.contact = 0
		self.fastfall = False
		self.speed = 0.5

		self.grid = [[None for x in range(10)] for y in range(20)]
		self.next = [self.next_block(), self.next_block(), self.next_block()]
		self.hold = None
		self.orientation = 0
		self.stopped = 0
		self.new_block()
		
		self.f = 0
		self.fp = 0
		self.alive = False
		self.score = 0
		self.lines = 0
		self.level = 1
		self.hiscore = 0

##################################################################################

	def stop(self):
		pass

	def did_change_size(self):
		pass

	def update(self):
		pass

##################################################################################

	def next_block(self):
		index = randrange(7)
		self.orientation = 0
		return index

	def new_block(self):
		self.index = self.next[0]
		self.next.pop(0)
		self.next.append(self.next_block())
		self.block = blocks[self.index][self.orientation]
		self.place_block()
		top = False
		while top is False:
			for tile in self.tiles:
				if tile[1] == 19: top = True
			if top is False:
				for i in range(4): self.tiles[i][1] += 1
		self.change_grid(self.index)

	def place_block(self):
		self.tiles = [None,None,None,None]
		for i in range(4): self.tiles[i] = [4+self.block[i][0],16+self.block[i][1]]

	def change_grid(self, c):
		try:
			for tile in self.tiles: 
				if self.grid[tile[1]][tile[0]] != None:
					if self.grid[tile[1]][tile[0]] != self.index:
						self.alive = False
						return
			for tile in self.tiles: self.grid[tile[1]][tile[0]] = c
		except IndexError: pass
	
	def hold_block(self):
		i = self.index
		o = self.orientation
		self.change_grid(None)
		for j in range(4):
			self.tiles[j][0] -= self.block[j][0]
			self.tiles[j][1] -= self.block[j][1]
		self.orientation = 0
		if self.hold is None:
			self.hold = self.index
			self.new_block()
		else:
			i = self.index
			self.index = self.hold
			self.hold = i
			self.block = blocks[self.index][0]
			self.place_block()

##################################################################################

	def fall(self):
		for tile in self.tiles:
			below = tile[1]-1
			if below < 0:
				self.stopped += 1
				return
			if self.grid[below][tile[0]] != None:
				if [tile[0],below] not in self.tiles:
					self.stopped += 1
					return

		if self.fastfall: self.score += 1
		self.change_grid(None)
		for tile in self.tiles: tile[1] -= 1
		self.change_grid(self.index)

	def move(self, direction):
		if self.stopped > 0: self.stopped = 0
		for tile in self.tiles:
			if direction is 1:
				if (tile[0] >= 9): return
				if self.grid[tile[1]][tile[0]+1] != None:
					if [tile[0]+1,tile[1]] not in self.tiles: return
			elif direction is -1:
				if (tile[0] <= 0): return
				if self.grid[tile[1]][tile[0]-1] != None: 
					if [tile[0]-1,tile[1]] not in self.tiles: return
			
		self.change_grid(None)
		for tile in self.tiles: tile[0] += direction
		self.change_grid(self.index)

	def rotate(self):
		if not self.alive: return
		i = self.index
		if self.orientation+1 >= 4: o = 0
		else: o = self.orientation+1
		
		for j in range(4):
			x = self.tiles[j][0]-self.block[j][0]+blocks[i][o][j][0]
			y = self.tiles[j][1]-self.block[j][1]+blocks[i][o][j][1]
			if ((x < 0) or (x > 9) or (y < 0) or (y > 20)): return
			try:
				if (self.grid[y][x] != None) and ([x,y] not in self.tiles): return
			except IndexError: pass
		
		if self.stopped > 0: self.stopped = 0
		self.orientation = o
		self.change_grid(None)

		for j in range(4):
			self.tiles[j][0] -= self.block[j][0]
			self.tiles[j][1] -= self.block[j][1]
		self.block = blocks[i][o]

		for j in range(4):
			self.tiles[j][0] += self.block[j][0]
			self.tiles[j][1] += self.block[j][1]
		self.change_grid(i)

	def crash(self):
		self.change_grid(None)
		bottom = False
		while not bottom:
			for i in range(4):
				if self.tiles[i][1]-1 < 0: bottom = True
				elif self.grid[self.tiles[i][1]-1][self.tiles[i][0]] != None:
					if [self.tiles[i][0],self.tiles[i][1]-1] not in self.tiles:
						bottom = True
			if not bottom:
				for i in range(4): self.tiles[i][1] -= 1
				self.score += 2
		self.change_grid(self.index)
		self.stopped = 3

#################################################################################

	#Counts number of non-empty tiles in a row
	def count_tiles(self, row):
		full = False
		count = 0
		for cell in range(10):
			if self.grid[row][cell] is not None: count += 1
		if count is 10: full = True
		return full

	#Shift all tiles down a row
	def shift_down(self, startrow):
		for row in range(20):
			if row < startrow: continue
			for cell in range(10): 
				if (row < 19): self.grid[row][cell]=self.grid[row+1][cell]
				else: self.grid[row][cell] = None
		#self.print_grid()

	#Updates score in the case of a full row
	def full_row(self):
		score = 0
		shift = 0
		row = 0
		for row in range(20):
			full = self.count_tiles(row)
			while full:
				shift += 1
				self.shift_down(row)
				full = self.count_tiles(row)

		self.lines += shift
		if (shift != 0) and (self.lines%10 == 0): self.level += 1
		if shift is 4: score += 800
		elif shift is 3: score += 500
		elif shift is 2: score += 300
		elif shift is 1: score += 100
		self.score += score*self.level

	def onestep(self):
		if not self.alive: return
		if self.stopped is 0: self.fall()

		for tile in self.tiles:
			if (tile[1] <= 0) or ((self.grid[tile[1]-1][tile[0]]\
			!= None) and [tile[0],tile[1]-1] not in self.tiles):
				if self.stopped >= 2:
					self.full_row()
					self.new_block()
					self.stopped = 0
				else: self.stopped += 1
				return

	#Print values held in grid; for debugging
	def print_grid(self):
		for row in self.grid:
			s = ""
			for cell in row:
				if cell is None: s += '-'
				else: s += str(cell)
			print(s)

##################################################################################

	def touch_began(self, touch):
		self.touch_start = touch.location
		self.moved = False

	def touch_moved(self, touch):
		self.moved = True
		if self.contact is not 4:
			self.contact += 1
			return
		self.contact = 0
	
		touch_loc = touch.location
		touch_dx = touch_loc[0]-self.touch_start[0]
		touch_dy = touch_loc[1]-self.touch_start[1]
		self.touch_start = touch_loc

		if abs(touch_dx) > abs(touch_dy):
			if touch_dx > 0: self.move(1)
			elif touch_dx < 0: self.move(-1)
		else:
			if touch_dy < 0: self.fastfall = True
			elif touch_dy > 0: 
				self.crash()
				return

		self.stopped = 0

	def touch_ended(self, touch):
		if self.fastfall: 
			self.fastfall = False

		self.stopped = 0
		if not self.moved:
			touchx,touchy=touch.location
			if (touchx > self.size.w*0.8+2) and (touchy<self.size.h*0.75): self.hold_block()
			else: self.rotate()
			
		if not self.alive:
			if self.first: self.first = False
			else: self.newgame()
			self.alive = True
			return

##################################################################################

	def draw(self):
		self.f += 1
		level = self.level
		if level > 29: level = 29
		speed = fpc[level]
		if self.fastfall: speed = speed//2
		if self.f > self.fp+speed:
			self.fp = self.f
			self.onestep()

		"""speed = self.speed/self.level
		if self.fastfall: speed = self.speed/2
		if self.t > self.tp + speed:
			self.tp = self.t
			self.onestep()"""

		######Game######
		#Outline
		no_fill()
		stroke("white")
		stroke_weight(1)
		rect(self.size.w*0.05,self.size.h/10, self.w, self.h)
		
		#Game Tiles
		tilexy = (self.w-2)/10-2
		translate(self.size.w*0.05+2, self.size.h*0.1+2)
		for row in self.grid:
			for cell in row:
				if cell != None: fill(colors[cell])
				else: no_fill()
				no_stroke()
				rect(0,0,tilexy,tilexy)
				translate(tilexy+2, 0)
			translate(-(self.w-2),tilexy+2)
		translate(-(self.size.w*0.05+2),-2*(self.w-2)-(self.size.h*0.1+2))
		
		######Next Blocks######
		#Text
		translate(self.size.w, self.size.h)
		xnext = -(self.size.w*0.95-self.w)/2
		ynext = -(self.size.h*0.9-self.h+7)
		text('NEXT:',font_name="GillSans",font_size=20,x=xnext,y=ynext)

		#Outline
		xoutline = xnext-(self.w-2)/20+1
		youtline = 3.5*ynext+5
		no_fill()
		stroke("white")
		stroke_weight(1)
		rect(xoutline-2,youtline,(self.w-2)/10+2,(self.w-2)*3/10+2)

		#Blocks
		for block in self.next:
			if block != None: fill(colors[block])
			else: no_fill()
			no_stroke()
			rect(xoutline,youtline/1.75-2,(self.w-2)/10-2,(self.w-2)/10-2)
			translate(0,-(self.w-2)/10)
		translate(0,(self.w-2)*3/10)

		######Hold######
		#Text
		text("HOLD:",font_name="GillSans",font_size=20,x=xnext,y=-self.size.h*0.25)
		#Outline
		no_fill()
		stroke("white")
		stroke_weight(1)
		rect(xoutline-2,-self.size.h*0.315,tilexy+4,tilexy+4)
		#Block
		if self.hold != None: fill(colors[self.hold])
		else: no_fill()
		no_stroke()
		rect(xoutline,-self.size.h*0.315+2,tilexy,tilexy)
		translate(-self.size.w,-self.size.h)
		###############
		
		#fill("red") #no_fill()
		#no_stroke()
		#rect(self.size.w*0.8+2,self.size.h*0.25,self.size.w*0.2-2,self.size.h*0.5)
		
		"""yholdt = -self.size.h/2
		yholdo = yholdt-1.5*tilexy-4
		text("HOLD:",font_name="GillSans",font_size=20,x=xnext,y=yholdt)
		#Outline
		no_fill()
		stroke("white")
		stroke_weight(1)
		rect(xoutline-2,yholdo,tilexy+4,tilexy+4)
		#Block
		if self.hold != None: fill(colors[self.hold])
		else: no_fill()
		no_stroke()
		rect(xoutline,yholdo+2,tilexy,tilexy)
		"""

		######Scores######
		xscore = self.size.w/2
		yscore = self.size.h*0.075
		ylevel = self.size.h*0.035

		text("SCORE: {}".format(self.score),font_name="GillSans",font_size=20,x=xscore,y=yscore)
		txt = "LEVEL: {}\tLINES: {}".format(self.level, self.lines)
		text(txt,font_name="GillSans",font_size=20,x=xscore,y=ylevel)
		

		######Start Screen######
		if not self.alive:
			translate(self.size.w/2, self.size.h/2)
			txt = 'TETRIS' if self.first else 'GAME OVER'
			text(txt, font_size=48)
			translate(-self.size.w/2, -self.size.h/2)

if __name__ == '__main__':
	run(MyScene(), show_fps=True)
