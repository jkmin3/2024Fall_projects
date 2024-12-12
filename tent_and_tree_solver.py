from itertools import permutations, product
from collections import deque
import random
from copy import deepcopy

def get_position(board):
	positions = {}
	for i, row in enumerate(board):
		for j, item in enumerate(row):
			if item in positions.keys():
				positions[item].append((i,j))
			else:
				positions[item] = [(i,j)]
	return positions

def are_w_connected(grid, positions):
	# Find all 'W' positions
	rows, cols = len(grid), len(grid[0])
	w_positions = positions.get('W', [])
	if not w_positions:
		return True  # No 'W's, so they are trivially connected.

	# Start BFS from the first 'W' found
	visited = set()
	queue = deque([w_positions[0]])

	visited.add(w_positions[0])


	while queue:
		position = queue.popleft()
		for orth_water in connecting_positions(position):
			if orth_water not in visited:
				if orth_water in positions['0'] or orth_water in positions['W']:  # '0' can be used as connectors
					queue.append(orth_water)
					visited.add(orth_water)

	# Check if all 'W's were visited
	return all(pos in visited for pos in w_positions)


def connecting_positions(pos, diagonal=False):
	x, y = pos[0], pos[1]
	possible_positions = [(x+1,y), (x,y+1), (x-1, y), (x, y-1)]
	if diagonal:
		possible_positions.extend([(x-1, y+1), (x-1, y-1), (x+1, y+1), (x+1, y-1)])
	return possible_positions

def dfs(node, connections, visited):
	visited.add(node)
	for position in connections.get(node, []):
		if position not in visited:
			dfs(position, connections, visited)

def is_connected(connections):
	visit = set()

	dfs(next(iter(connections)), connections, visit)

	return len(visit) == len(connections)

def tree_and_tent(connections):
	visit = set()

	count = 0
	while len(visit) != len(connections):
		for connection in connections.values():
			if len(connection) == 1:
				visit.add(connection[0])
			else:
				for pos in connection:
					if pos in visit:
						connection.remove(pos)
				if len(connection) == 1:
					visit.add(connection[0])
			count += 1
			if count > 300:
				return False
	return True

def get_view(board, row=0, column=0):
	if row:
		return board[row-1]
	elif column:
		column_view = []
		for row in board:
			column_view.append(row[column-1])
		return column_view
	
def get_hints(board):
	hints = {}
	hints['row'] = {}
	hints['column'] = {}
	hints['row']['trees'] = []
	hints['column']['trees'] = []
	hints['row']['water'] = []
	hints['column']['water'] = []
	y = len(board)
	x = len(board[0])
	for i in range(1, x+1):
		view = get_view(board, row=i)
		tree_count = 0
		water_count = 0
		for item in view:
			if item == 'T':
				tree_count += 1
			if item == 'W':
				water_count += 1
		hints['row']['trees'].append(tree_count)
		hints['row']['water'].append(water_count)
	for i in range(1, y):
		view = get_view(board, column=i)
		tree_count = 0
		water_count = 0    
		for item in view:
			if item == 'T':
				tree_count += 1
			if item == 'W':
				water_count += 1
		hints['column']['trees'].append(tree_count)
		hints['column']['water'].append(water_count)
	
	return hints

def check_tents(positions, tree_tent_connections):

	for tent in positions['T']:
		# Check for all tents not being next to each other
		for pos_tent in connecting_positions(tent, True):
			if pos_tent in positions['T']:
				valid = False
				print(f"Found two tents next to each other at positions {tent} and {pos_tent}")
				return False
			else:
				valid = True

		tree_tent_connections[tent] = []
		valid = False
		for orth_tent in connecting_positions(tent):
			# Check for all tents having open land
			if orth_tent in positions['0']:
				valid = True
			else:
				if valid == True:
					pass
				else:
					valid = False
			# Check if each tent has a unique tree
			if orth_tent in positions['R']:
				tree_tent_connections[tent].append(orth_tent)
		if valid == False:
			print("False at tent position", tent)
			return False

	valid = tree_and_tent(tree_tent_connections)
	if not valid:
		print("Tree and tent does not have a unique pair")
		return valid

	return valid
	
def check_trees(positions, with_zeros=False):
	# Check for all trees have a water source
	for tree in positions['R']:
		for orth_tree in connecting_positions(tree):
			if orth_tree in positions['W']:
				valid = True
				break
			if with_zeros:
				if orth_tree in positions['0']:
					valid = True
					break
			else:
				valid = False
		if valid == False:
			print("False at tree position", tree)
			return False
	return valid
		
def check_water(positions, with_zeros=False, board=None):
	# Check if water is orthogonally connected
	if with_zeros:
		return are_w_connected(board, positions)
	water_connections = {}
	zero_positions = []
	for water in positions['W']:
		temp_connections = []
		for orth_water in connecting_positions(water):
			if orth_water in positions['W']:
				temp_connections.append(orth_water)
			if with_zeros:
				zero_positions.append(orth_water)
				temp_connections.append(orth_water)
		water_connections[water] = temp_connections

	valid = is_connected(water_connections)
	if not valid:
		print("water in not connected")
		return valid
	return valid

def get_puzzle_from_board(completed_board):
	board = [['0' for i in range(len(completed_board[0]))] for j in range(len(completed_board))]
	tree_pos = {}
	for i, row in enumerate(completed_board):
		tree_pos[i] = []
		for j, item in enumerate(row):
			if item == "R":
				board[i][j] = 'R'
				tree_pos[i].append(j)
				
	return tree_pos, board

def get_permutations(board, hints, tree_pos):
	row_clues = {}
	for i, row in enumerate(board):
		
		row_clue = ""
		row_clue += 'T' * hints['row']['trees'][i]
		row_clue += "W" * hints['row']['water'][i]
		for item in row:
			if item == 'R':
				row_clue += "R"
		row_zeroes = 8 - len(row_clue)
		row_clue += "0" * row_zeroes
		row_clues[i] = row_clue

	row_perms = {}
	for key, item in row_clues.items():
		row_perm = permutations(item, 8)
		row_perms[key] = set()
		for p in row_perm:
			in_position = True
			for pos in tree_pos[key]:
				if p[pos] != 'R':
					in_position = False
			if in_position == True:
				row_perms[key].add(p)
	return row_perms


def check_valid_solution_v2(board, hints, check_hints=False, partial_solution=False):
	positions = get_position(board)
	if not partial_solution:
		valid = len(positions['R']) == len(positions['T'])
		if valid:
			pass
		else:
			print("There are not an equal amount of trees and tents")
			return False

	# Check for all trees have a water source
	valid = check_trees(positions, partial_solution)
	if not valid:
		return valid
	print("Trees passed")
	# Check for all tents having open land
	# Check for all tents not being next to each other
	# Check if each tent has a unique tree
	tree_tent_connections = {}
	valid = check_tents(positions, tree_tent_connections)
	if not valid:
		return valid
	print("Tents passed")
	
	# Check if water is orthogonally connected
	valid = check_water(positions, partial_solution, board=board)
	if not valid:
		return valid
	print("Water passed")
	# Check if hints match up with puzzle
	if check_hints:
		board_hints = get_hints(board)
		valid = board_hints == hints
	
	return valid

def print_board(board):
	for row in board:
		print(row)

def backtrack(clues, depth, possible_board, puzzle_board, skip_solution=[]):
	
	keys = list(clues.keys())
	if depth == len(clues):
		if possible_board in skip_solution:
			print("board is same in skip")
			return None 
		print("GOT HERE")
		hints = get_hints(possible_board)
		if check_valid_solution_v2(possible_board, hints, check_hints=True):
			return possible_board
		else:
			possible_board[depth-1] = puzzle_board[depth-1]
			return None
	
	for item in clues[keys[depth]]:
		possible_board[depth] = item
		print("depth", depth, "board")
		print_board(possible_board)
		if check_valid_solution_v2(possible_board, hints=None, partial_solution=True):
			result = backtrack(clues, depth+1, possible_board, puzzle_board, skip_solution)
			if result:
				return result
		else:
			possible_board[depth] = puzzle_board[depth]
	possible_board[depth] = puzzle_board[depth]
	return None

def generate_new_puzzle():
	trees_and_tents = 11
	x, y = 8, 8
	bank = [i for i in range(8)]
	blank_board = [['0' for _ in range(x)] for _ in range(y)]
	visited = set()

	while trees_and_tents > 0:
		rx = random.choice(bank)
		ry = random.choice(bank)
		if blank_board[rx][ry] == '0':  # Check if the cell is empty
			tx, ty = random.choice(connecting_positions((rx, ry)))
			if 0 <= tx < 8 and 0 <= ty < 8:  # Ensure valid position
				if blank_board[tx][ty] == '0':  # Tent cell must be empty
					# Place the tree ('R') and the tent ('T')
					blank_board[rx][ry] = 'R'
					blank_board[tx][ty] = 'T'
					trees_and_tents -= 1
					
					# Check the validity of the board
					tree_tent_connections = {}
					positions = get_position(blank_board)
					
					if check_tents(positions, tree_tent_connections):
						# Valid placement; continue
						pass
					else:
						# Invalid placement; rollback
						blank_board[rx][ry] = '0'
						blank_board[tx][ty] = '0'
						trees_and_tents += 1  # Revert the counter

	return blank_board

def insert(list, item, position):
  return (*list[:position], item, *list[position:])

def create_iterations(generated_puzzle,):
	item = product("W0", repeat=6)
	iterations = {}
	for i, row in enumerate(generated_puzzle):
		zero_count = 0
		for item in row:
			if item == '0':
				zero_count += 1
		product_iterations = product("W0", repeat=zero_count)
		iterations[i] = []
		for iteration in product_iterations:
			iterations[i].append(iteration)

	iterations_v2 = {}
	for k, v in iterations.items():
		iterations_v2[k] = []
		for row in v:
			new_row = row
			for j, item in enumerate(generated_puzzle[k]):
				if item != '0':
					new_row = insert(new_row, item, j)
			iterations_v2[k].append(new_row)
	return iterations_v2

def generate_new_puzzle_v2():
	trees_and_tents = 11
	x, y = 8, 8
	bank = [i for i in range(8)]
	blank_board = [['0' for _ in range(x)] for _ in range(y)]
	visited = set()

	while trees_and_tents > 0:
		rx = random.choice(bank)
		ry = random.choice(bank)
		if blank_board[rx][ry] == '0':  # Check if the cell is empty
			tx, ty = random.choice(connecting_positions((rx, ry)))
			if 0 <= tx < 8 and 0 <= ty < 8:  # Ensure valid position
				if blank_board[tx][ty] == '0':  # Tent cell must be empty
					# Place the tree ('R') and the tent ('T')
					blank_board[rx][ry] = 'R'
					blank_board[tx][ty] = 'T'
					trees_and_tents -= 1
					
					# Check the validity of the board
					tree_tent_connections = {}
					positions = get_position(blank_board)
					
					if check_tents(positions, tree_tent_connections):
						# Valid placement; continue
						pass
					else:
						# Invalid placement; rollback
						blank_board[rx][ry] = '0'
						blank_board[tx][ty] = '0'
						trees_and_tents += 1  # Revert the counter

	return blank_board


def check_tents_water(positions):
	for tent in positions.get('T', []):
		for orth_tent in connecting_positions(tent):
			# Check for all tents having open land
			if orth_tent in positions.get('0', []):
				valid = True
				break
			else:
				valid = False
		if valid == False:
			return valid
	return valid

def check_valid_solution_for_generated(board, partial_solution=False):
	positions = get_position(board)

	# Check for all trees have a water source
	valid = check_trees(positions, partial_solution)
	if not valid:
		return valid
	print("Trees passed")
	# Check for all tents having open land
	# Check for all tents not being next to each other
	# Check if each tent has a unique tree
	valid = check_tents_water(positions)
	if not valid:
		return valid
	print("Tents passed")
	
	# Check if water is orthogonally connected
	valid = check_water(positions, partial_solution, board=board)
	if not valid:
		return valid
	print("Water passed")
	return valid

def backtrack_water(clues, depth, possible_board, puzzle_board, skip_solution=[]):
	keys = list(clues.keys())
	if depth == len(clues):
		if possible_board in skip_solution:
			print("board is same in skip")
			return None 
		print("GOT HERE")
		if check_valid_solution_for_generated(possible_board, ):
			return possible_board
		else:
			possible_board[depth-1] = puzzle_board[depth-1]
			return None
	
	for item in clues[keys[depth]]:
		possible_board[depth] = item
		print("depth", depth, "board")
		print_board(board)
		if check_valid_solution_for_generated(possible_board, partial_solution=True):
			result = backtrack_water(clues, depth+1, possible_board, puzzle_board, skip_solution)
			if result:
				return result
		else:
			possible_board[depth] = puzzle_board[depth]
	possible_board[depth] = puzzle_board[depth]
	return None



blank = [['0' for i in range(8)] for i in range(8)]
blank[0][6] = 'R'
blank[1][1] = 'R'
blank[2][0] = 'R'
blank[2][5] = 'R'
blank[4][0] = 'R'
blank[4][7] = 'R'
blank[5][4] = 'R'
blank[5][7] = 'R'
blank[7][0] = 'R'
blank[7][2] = 'R'
blank[7][6] = 'R'
blank[0][1] = 'W'
blank[0][2] = 'W'
blank[0][3] = 'W'
blank[0][4] = 'W'
blank[0][5] = 'W'
blank[1][4] = 'W'
blank[2][4] = 'W'
blank[3][4] = 'W'
blank[3][0] = 'W'
blank[3][1] = 'W'
blank[3][2] = 'W'
blank[3][3] = 'W'
blank[3][5] = 'W'
blank[3][6] = 'W'
blank[4][3] = 'W'
blank[4][6] = 'W'
blank[5][3] = 'W'
blank[6][1] = 'W'
blank[6][2] = 'W'
blank[6][3] = 'W'
blank[6][4] = 'W'
blank[6][5] = 'W'
blank[6][6] = 'W'
blank[6][7] = 'W'
blank[7][1] = 'W'
blank[0][7] = 'T'
blank[1][0] = 'T'
blank[1][2] = 'T'
blank[1][5] = 'T'
blank[3][7] = 'T'
blank[4][1] = 'T'
blank[4][4] = 'T'
blank[5][6] = 'T'
blank[6][0] = 'T'
blank[7][3] = 'T'
blank[7][5] = 'T'

tree_pos, board = get_puzzle_from_board(blank)
tree_pos, puzzle_board = get_puzzle_from_board(blank)
hints = get_hints(blank)
row_perms = get_permutations(board, hints, tree_pos)
skip = []
skip.append([('0', 'W', 'W', 'W', 'W', 'W', 'R', 'T'),
										('T', 'R', 'T', '0', 'W', 'T', '0', '0'),
										('R', '0', '0', '0', 'W', 'R', '0', '0'),
										('W', 'W', 'W', 'W', 'W', 'W', 'W', 'T'),
										('R', 'T', 'W', '0', 'T', '0', 'W', 'R'),
										('0', '0', 'W', '0', 'R', '0', 'T', 'R'),
										('T', 'W', 'W', 'W', 'W', 'W', 'W', 'W'),
										('R', 'W', 'R', 'T', '0', 'T', 'R', '0')])


solved_board = backtrack(row_perms, 0, board, puzzle_board, skip)

print("\n", "Solved")
print_board(solved_board)

# Generate puzzles

generated_puzzle = generate_new_puzzle_v2()
print("\n", "Generated Puzzle")
print_board(generated_puzzle)
iterations = create_iterations(generated_puzzle)
generated_puzzle_copy = deepcopy(generated_puzzle)
generated_puzzle_with_water = backtrack_water(iterations, 0, generated_puzzle_copy, generated_puzzle)
print("\n", "Generated Puzzle with Water")
print_board(generated_puzzle_with_water)
