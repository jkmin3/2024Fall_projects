def get_position(board):
  positions = {}
  for i, row in enumerate(board):
    for j, item in enumerate(row):
      if item in positions.keys():
        positions[item].append((i,j))
      else:
        positions[item] = [(i,j)]
  return positions

def connecting_positions(pos, diagonal=False):
  x, y = pos[0], pos[1]
  possible_positions = [(x+1,y), (x,y+1), (x-1, y), (x, y-1)]
  if diagonal:
    possible_positions.extend([(x-1, y+1), (x-1, y-1), (x+1, y+1), (x+1, y-1)])
  return possible_positions

def dfs(node, connections, visited):
  visited.add(node)
  for position in connections.get(node):
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


def check_valid_solution(board):
  """
  There has to be a check for each tree having a single tent
  There has to check for each tree having a water source, this can be shared
  There has to be a check for each tent having an open space of land, this can also be shared
  """
  positions = get_position(board)
  valid = len(positions['R']) == len(positions['T'])
  if valid:
    pass
  else:
    print("There are not an equal amount of trees and tents")
    return False


  # Check for all trees have a water source
  for tree in positions['R']:
    for orth_tree in connecting_positions(tree):
      if orth_tree in positions['W']:
        valid = True
        break
      else:
        valid = False
    if valid == False:
      print("False at tree position", tree)
      return False
  
  # Check for all tents having open land
  for tent in positions['T']:
    for orth_tent in connecting_positions(tent):
      if orth_tent in positions['0']:
        valid = True
        break
      else:
        valid = False
    if valid == False:
      print("False at tent position", tent)
      return False
  
  # check for all tents not being next to each other
  for tent in positions['T']:
    for pos_tent in connecting_positions(tent, True):
      if pos_tent in positions['T']:
        valid = False
        print(f"Found two tents next to each other at positions {tent} and {pos_tent}")
        return False
      else:
        valid = True

  # Check if water is orthogonally connected
  water_connections = {}
  water_positions = positions['W'].copy()
  for water in positions['W']:
    temp_connections = []
    for orth_water in connecting_positions(water):
      if orth_water in water_positions:
        temp_connections.append(orth_water)
    water_connections[water] = temp_connections
  valid = is_connected(water_connections)

  # Check if each tent has a unique tree
  tree_tent_connections = {}
  for tent in positions['T']:
    tree_tent_connections[tent] = []
    for orth_tree in connecting_positions(tent):
      if orth_tree in positions['R']:
        tree_tent_connections[tent].append(orth_tree)
  valid = tree_and_tent(tree_tent_connections)

  return valid