import pygame as pg

#import gui objects
import sys
sys.path.insert(1, '/Python Projects/GuiObjects')

from GUIObjects import *

width, height = 1200, 900

screen = pg.display.set_mode((width, height))


class Cell:
	def __init__(self, pos, size, color, piece=None, selectedColor=lightBlue):
		self.pos = pos
		self.size = size
		self.color = color

		self.selectedColor = selectedColor

		self.selected = False

		self.piece = piece

	def Draw(self):
		pg.draw.rect(screen, self.color, (self.pos[0], self.pos[1], self.size[0], self.size[1]))

		if self.selected:
			if self.piece == None:
				pg.gfxdraw.filled_ellipse(screen, int(self.pos[0] + self.size[0] // 2), int(self.pos[1] + self.size[1] // 2), int(self.size[0] // 4), int(self.size[1] // 4), self.selectedColor)
			else:
				pg.draw.rect(screen, self.selectedColor, (self.pos[0], self.pos[1], self.size[0], self.size[1]))


	def Select(self):
		self.selected = True

	def UnSelect(self):
		self.selected = False

	def SwapSelect(self):
		self.selected = not self.selected

	def ChangePiece(self, piece):
		self.piece = piece


class Piece:
	def __init__(self, pos, size, color, isKinged=False, kingedColor=black):
		self.pos = pos
		self.size = size
		self.color = color
		self.isKinged = isKinged
		self.kingedColor = kingedColor

	def Draw(self):
		pg.gfxdraw.filled_ellipse(screen, int(self.pos[0] + self.size[0] // 2), int(self.pos[1] + self.size[1] // 2), int(self.size[0] // 2), int(self.size[1] // 2), self.color)
		if self.isKinged:
			pg.gfxdraw.filled_ellipse(screen, int(self.pos[0] + self.size[0] // 2), int(self.pos[1] + self.size[1] // 2), int(self.size[0] // 4), int(self.size[1] // 4), self.kingedColor)

	def King(self):
		self.isKinged = True

	def Move(self, pos):
		self.pos = pos


class Board:
	def __init__(self, pos, gridSize, numOfCells, colors, numOfPieces=12):
		self.pos = pos
		self.gridSize = gridSize
		self.numOfCells = numOfCells

		self.numOfPieces = numOfPieces

		self.color_1 = colors[0]
		self.color_2 = colors[1]

		self.borderColor = colors[2]

		self.pieceColor_1 = colors[3]
		self.pieceColor_2 = colors[4]

		self.selectedCell = False
		self.piecesToRemove = []

		self.moves = []
		self.midTurn = False

		self.activePlayer = self.pieceColor_1

		self.cellSize = (self.gridSize[0] // self.numOfCells[0], self.gridSize[1] // self.numOfCells[1])

		self.endTurnButton = None
		self.restartButton = None
		self.winLabel = None

		self.CreateGrid()

	def CreateGrid(self):
		self.grid = [[] for x in range(self.numOfCells[0])]
		color = self.color_2

		for x in range(self.numOfCells[0]):
			if color == self.color_1:
				color = self.color_2
			elif color == self.color_2:
				color = self.color_1

			for y in range(self.numOfCells[1]):
				if color == self.color_1:
					color = self.color_2
				elif color == self.color_2:
					color = self.color_1

				self.grid[x].append(Cell((self.pos[0] + (self.cellSize[0] * x), self.pos[1] + (self.cellSize[1] * y)), self.cellSize, color))

		self.CreatePieces()

	def CreatePieces(self):
		self.pieces = []

		piecesAdded = 0

		for i, row in enumerate(self.grid):
			for cell in row:
				if cell.color == self.color_2:
					# player 1
					if i < 3:
						self.pieces.append(Piece((cell.pos[0] + 20, cell.pos[1] + 20), (cell.size[0] - 40, cell.size[1] - 40), self.pieceColor_1))
						cell.ChangePiece(self.pieces[-1])
						piecesAdded += 1

					# player 2
					if i > 4:
						self.pieces.append(Piece((cell.pos[0] + 20, cell.pos[1] + 20), (cell.size[0] - 40, cell.size[1] - 40), self.pieceColor_2))
						cell.ChangePiece(self.pieces[-1])
						piecesAdded += 1

				if piecesAdded >= self.numOfPieces * 2:
					return

	def Draw(self):
		pg.draw.rect(screen, self.borderColor, (self.pos[0] - self.cellSize[0] / 7, self.pos[1] - self.cellSize[1] / 7, self.gridSize[0] + (self.cellSize[0] / 7) * 2, self.gridSize[1] + (self.cellSize[1] / 7) * 2))

		for row in self.grid:
			for cell in row:
				cell.Draw()

		for piece in self.pieces:
			piece.Draw()

	def HandleEvent(self, event):
		if self.endTurnButton != None:
			self.endTurnButton.HandleEvent(event)

			if self.endTurnButton.active:
				self.EndTurn()
				self.DestroyEndTurnButton()

		if self.restartButton != None:
			self.restartButton.HandleEvent(event)

			if self.restartButton.active:
				self.Restart()
				self.DestroyWinner()

		if event.type == pg.MOUSEBUTTONDOWN:
			if event.button == 1:

				if not self.midTurn:
					self.CalculateMoves(self.GetSelectedCell(pg.mouse.get_pos()))
				else:
					if self.GetSelectedCell(self.selectedCell.pos)[0].selected and self.GetSelectedCell(pg.mouse.get_pos())[0] != None:
						if self.GetSelectedCell(pg.mouse.get_pos())[0].piece == None:
							self.CalculateMoves(self.GetSelectedCell(pg.mouse.get_pos()))
					else:
						self.CalculateMoves(self.GetSelectedCell(self.selectedCell.pos))

	def GetSelectedCell(self, pos):
		for i, row in enumerate(self.grid):
			for j, cell in enumerate(row):
				if pg.Rect(cell.pos[0], cell.pos[1], cell.size[0], cell.size[1]).collidepoint(pos):
					if cell.piece != None:
						if self.activePlayer == cell.piece.color:
							return (cell, (i, j))
					else:
						if cell.selected:
							self.Move(cell, i, j)

		return (None, (0, 0))

	def Move(self, cell, i, j):
		if self.selectedCell != None:
			if self.selectedCell.piece != None:
				startPos = self.selectedCell.pos
				self.selectedCell.piece.Move((cell.pos[0] + 20, cell.pos[1] + 20))
				cell.piece = self.selectedCell.piece
				self.selectedCell.piece = None

				if cell.pos in self.moves:
					self.RemovePieces(startPos, cell.pos)
					self.moves = []
					self.CalculateMoves(self.GetSelectedCell(cell.pos))
					if len(self.moves) == 0:
						self.midTurn = False
						self.GetSelectedCell(cell.pos)[0].UnSelect()
						self.EndTurn()
						self.DestroyEndTurnButton()
					else:
						self.midTurn = True
						self.CreateEndTurnButton()
						self.selectedCell = self.GetSelectedCell(cell.pos)[0]
				else:
					self.EndTurn()
					self.DestroyEndTurnButton()
					self.midTurn = False

				self.moves = []

				self.CheckForKing(cell, i, j)
				winner = self.CheckWin()
				if winner != None:
					self.DisableInput()
					self.ShowWinner(winner)
					self.DestroyEndTurnButton()

	def EndTurn(self):
		if self.activePlayer == self.pieceColor_1:
			self.activePlayer = self.pieceColor_2
		elif self.activePlayer == self.pieceColor_2:
			self.activePlayer = self.pieceColor_1

	def RemovePieces(self, startPos, endPos):
		for cell in self.piecesToRemove:
			if cell.pos == ((startPos[0] + endPos[0]) // 2, (startPos[1] + endPos[1]) // 2):
				if cell.piece in self.pieces:
					self.pieces.remove(cell.piece)
					cell.piece = None

		self.piecesToRemove = []

	def CheckForKing(self, cell, i, j):
		if i == 0 and cell.piece.color == self.pieceColor_2:
			cell.piece.King()
		if i == len(self.grid) - 1 and cell.piece.color == self.pieceColor_1:
			cell.piece.King()

	def CalculateMoves(self, cellData):
		cell = cellData[0]
		i, j = cellData[1]
		for row in self.grid:
			for c in row:
				if c != cell:
					c.UnSelect()
				else:
					c.Select()

		self.piecesToRemove = []

		if cell != None:
			if not cell.selected:
				self.selectedCell = None
				return
			else:
				self.selectedCell = cell

			self.CheckMove(cell, i, j)

	def CheckMove(self, cell, i, j):
		if cell != None:
			if not cell.piece.isKinged:
				if cell.piece.color == self.pieceColor_1:
					direction = [[1], [1, -1]]
				elif cell.piece.color == self.pieceColor_2:
					direction = [[-1], [1, -1]]
				else:
					direction = [[1], [1, -1]]
			else:
				direction = [[1, -1], [1, -1]]

			for x in direction[0]:
				for y in direction[1]:
					if j + y >= 0 and j + y < len(self.grid) and i + x >= 0 and i + x < len(self.grid):
						if self.grid[i + x][j + y].piece == None:
							self.grid[i + x][j + y].Select()
						else:
							if self.grid[i + x][j + y].piece.color != cell.piece.color:
								self.CheckForTake(i, x * 2, j, y * 2)

	def CheckForTake(self, i, x, j, y):
		if j + y >= 0 and j + y < len(self.grid) and i + x >= 0 and i + x < len(self.grid):
			if self.grid[i + x][j + y].piece == None:
				self.grid[i + x][j + y].Select()
				self.piecesToRemove.append(self.grid[i + x // 2][j + y // 2])
				self.moves.append(self.grid[i + x][j + y].pos)

	def CheckWin(self):
		colors = []
		for piece in self.pieces:
			colors.append(piece.color)

		if colors.count(self.pieceColor_1) == 0:
			winner = "Player 2"
		elif colors.count(self.pieceColor_2) == 0:
			winner = "Player 1"
		else:
			winner = None

		return winner

	def CreateEndTurnButton(self):
		self.endTurnButton = Button(screen, "end turn", (width - 175, height - 100, 150, 50), (lightBlack, lightGray, lightRed), "End turn",
		("arial", 24, white), isHoldButton=True, drawData={"borderWidth": 4, "roundedCorners": True, "roundness": 16})

	def DestroyEndTurnButton(self):
		if self.endTurnButton in allButtons:
			allButtons.remove(self.endTurnButton)

		self.endTurnButton = None

	def DisableInput(self):
		self.inputEnabled = False

	def ShowWinner(self, winner):
		self.winLabel = Label(screen, "winner", (width // 2 - 400, height // 2 - 100, 800, 200), (lightBlack, darkWhite), f"{winner} is the winner!", ("arial", 80, white), drawData={"borderWidth": 3, "roundedCorners": True, "roundness": 15})

		self.restartButton = Button(screen, "restart", (width // 2 - 200, height // 2 + 125, 400, 50), (lightBlack, lightGray, darkWhite), "Restart",
		("arial", 24, white), isHoldButton=True, drawData={"borderWidth": 3, "roundedCorners": True, "roundness": 15})

	def DestroyWinner(self):
		if self.winLabel in allLabels:
			allLabels.remove(self.winLabel)

		if self.restartButton in allButtons:
			allButtons.remove(self.restartButton)

		self.restartButton = None
		self.winLabel = None

	def Restart(self):
		self.activePlayer = self.pieceColor_1
		self.CreateGrid()


board = Board((width / 2 - 400, height / 2 - 400), (800, 800), (8, 8), (lightBlack, darkWhite, (120, 120, 120), red, blue), numOfPieces=12)


def DrawLoop():
	screen.fill(darkGray)

	board.Draw()

	DrawGui()

	pg.display.update()


while running:
	clock.tick_busy_loop(fps)

	for event in pg.event.get():
		if event.type == pg.QUIT:
			running = False
		if event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				running = False

		board.HandleEvent(event)

	DrawLoop()
