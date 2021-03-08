
from kaggle_environments.envs.hungry_geese.hungry_geese import Observation, Configuration, Action, row_col
from heapq import heapify, heappush, heappop
import numpy as np

last_direction = None
iteration_number = 1

def bfs(start_x, start_y, mask, food_coords, flag=0):
    dist_matrix = np.zeros_like(mask)
    vect_matrix = np.full_like(mask, -1)
    
    queue = [(start_x, start_y, 0, None)]
    
    while queue:
        current_x, current_y, current_dist, vect = queue.pop(0)
        vect_matrix[current_x, current_y] = vect
        up_x = current_x + 1 if current_x != 6 else 0
        down_x = current_x - 1 if current_x != 0 else 6
        left_y = current_y - 1 if current_y != 0 else 10
        right_y = current_y + 1 if current_y != 10 else 0
        
        if mask[up_x, current_y] != -1 and not dist_matrix[up_x, current_y]:
            dist_matrix[up_x, current_y] = current_dist + 1
            if vect is None:
                queue.append((up_x, current_y, current_dist + 1, 0))
            else:
                queue.append((up_x, current_y, current_dist + 1, vect))
        if mask[down_x, current_y] != -1 and not dist_matrix[down_x, current_y]:
            dist_matrix[down_x, current_y] = current_dist + 1
            if vect is None:
                queue.append((down_x, current_y, current_dist + 1, 1))
            else:
                queue.append((down_x, current_y, current_dist + 1, vect))
        if mask[current_x, left_y] != -1 and not dist_matrix[current_x, left_y]:
            dist_matrix[current_x, left_y] = current_dist + 1
            if vect is None:
                queue.append((current_x, left_y, current_dist + 1, 2))
            else:
                queue.append((current_x, left_y, current_dist + 1, vect))
        if mask[current_x, right_y] != -1 and not dist_matrix[current_x, right_y]:
            dist_matrix[current_x, right_y] = current_dist + 1
            if vect is None:
                queue.append((current_x, right_y, current_dist + 1, 3))
            else:
                queue.append((current_x, right_y, current_dist + 1, vect))
            
    min_food_id = -1
    min_food_dist = 200000
    for id_, food in enumerate(food_coords):
        if dist_matrix[food[0], food[1]] != 0 and min_food_dist > dist_matrix[food[0], food[1]]:
            min_food_id = id_
            min_food_dist = dist_matrix[food[0], food[1]]
    
    if flag==1:
        return min_food_dist

    if min_food_id == -1:
        x, y = -1, -1
        mn = 0 
        for i in range(dist_matrix.shape[0]):
            for j in range(dist_matrix.shape[1]):
                if dist_matrix[i, j] > mn:
                    x, y = i, j
                    mn = dist_matrix[i, j]
        return vect_matrix[x, y]
    
    food_x, food_y = food_coords[min_food_id]
    return vect_matrix[food_x, food_y]

def straightforward_bfs(mask, last_direction, start_row, start_col, food_coords):
    my_action = bfs(start_row, start_col, mask, food_coords)

    up_x = start_row + 1 if start_row != 6 else 0
    down_x = start_row - 1 if start_row != 0 else 6
    left_y = start_col - 1 if start_col != 0 else 10
    right_y = start_col + 1 if start_col != 10 else 0
    
    step = 'NORTH'
    if my_action == 0:
        step = 'SOUTH'
        if last_direction == 'NORTH':
            if mask[down_x, start_col] != -1:
                step = 'NORTH'
            elif mask[start_row, left_y] != -1:
                step = 'WEST'
            elif mask[start_row, right_y] != -1:
                step = 'EAST'
    if my_action == 1:
        step = 'NORTH'
        if last_direction == 'SOUTH':
            if mask[up_x, start_col] != -1:
                step = 'SOUTH'
            elif mask[start_row, left_y] != -1:
                step = 'WEST'
            elif mask[start_row, right_y] != -1:
                step = 'EAST'
    if my_action == 2:
        step = 'WEST'
        if last_direction == 'EAST':
            if mask[up_x, start_col] != -1:
                step = 'SOUTH'
            elif mask[down_x, start_col] != -1:
                step = 'NORTH'
            elif mask[start_row, right_y] != -1:
                step = 'EAST'
    if my_action == 3:
        step = 'EAST'
        if last_direction == 'WEST':
            if mask[up_x, start_col] != -1:
                step = 'SOUTH'
            elif mask[down_x, start_col] != -1:
                step = 'NORTH'
            elif mask[start_row, left_y] != -1:
                step = 'WEST'
    return step

def get_nearest_cells(x,y):
    """
    returns all adjacent cells
    """
    result = []
    for i in (-1,+1):
        result.append(((x+i+7)%7, y))
        result.append((x, (y+i+11)%11))
    return result

def get_direction(head, target):
    """
    will not consider blocking
    """
    x1=head[0]
    y1=head[1]
    x2=target[0]
    y2=target[1]
    if(x1==x2):
        direct = 'WEST'
        if y1 < y2:
            if y2-y1 < 11-(y2-y1):
                direct = 'EAST'
        else:
            if y1-y2 > 11-(y1-y2):
                direct = 'EAST'
    if(y1==y2):
        direct = 'NORTH'
        if x1 < x2:
            if x2-x1 < 7-(x2-x1):
                direct = 'SOUTH'
        else:
            if x1-x2 > 7-(x1-x2):
                direct = 'SOUTH'
    else:
        direct = 'WEST'
        if y1 < y2:
            if y2-y1 < 11-(y2-y1):
                direct = 'EAST'
        else:
            if y1-y2 > 11-(y1-y2):
                direct = 'EAST'
        if x1 < x2:
            if x2-x1 < 7-(x2-x1):
                direct = 'SOUTH'
        else:
            if x1-x2 > 7-(x1-x2):
                direct = 'SOUTH'
    return direct

def opposite_direct(a,b):
    """
    if two directions are opposite return true
    """
    if a =='NORTH' and b == 'SOUTH' or a =='SOUTH' and b == 'NORTH':
        return True
    if a =='EAST' and b == 'WEST' or a =='WEST' and b == 'EAST':
        return True
    return False

def dfs_hole(cell, occupied, visited, parent):
    visited[cell] = True
    res = True
    val = 1
    adj_cells = get_nearest_cells(cell[0], cell[1])
    adj_cells.remove(parent)
    options = [cell for cell in adj_cells if list(cell) not in occupied and cell not in visited.keys()]
    if not len(options):
        for cell in adj_cells:
            if list(cell) not in occupied:
                return False, val
        return True, val

    for child_cell in options:
        temp1, temp2 = dfs_hole(child_cell, occupied, visited, cell)
        res = res and temp1
        val += temp2

    return res, val

def black_hole(available_steps, danger_area, occupied, my_head):
    """
    returns list of cells whose dfs ends at a cell surrounded by a tail
    """
    black_holes = {}

    for x, y in available_steps.keys():
        visited = {tuple(my_head):True}
        flag, val = dfs_hole((x,y), occupied, visited, tuple(my_head))
        if flag:
            black_holes[(x,y)] = available_steps[(x, y)][0]
        available_steps[(x, y)][1] = val

    for x, y in danger_area.keys():
        visited = {tuple(my_head):True}
        flag, val = dfs_hole((x,y), occupied, visited, tuple(my_head))
        if flag:
            black_holes[(x,y)] = [danger_area[(x,y)][0], val]
        danger_area[(x, y)][1] = val

    return black_holes, available_steps, danger_area

def my_move(food_location, available_steps, other_heads, my_head, last_direction, body_cells, danger_area, mask, other_tails):
    my_food = []

    black_holes, available_steps, danger_area = black_hole(available_steps, danger_area, [*body_cells, *other_heads, *other_tails], my_head)
    print("black hole if i head towards : {}".format(black_holes))

    # available room for me to move in that direction
    direction_room = {val[0]:val[1] for val in available_steps.values()}
    print("room directions {}".format(direction_room))

    max_heap = []
    corresponding_direction = {}
    heapify(max_heap)
    dp_dist = {}
    closestFood = {}

    for head in [*other_heads, my_head]:
        for food in food_location:
            key = tuple((*head, *food))
            if key not in dp_dist.keys():
                dp_dist[key] = bfs(*head, mask, [food], 1)
            distance = dp_dist[key]

            if tuple(head) not in closestFood.keys():
                closestFood[tuple(head)] = [[food], distance]
            elif distance < closestFood[tuple(head)][1]:
                closestFood[tuple(head)] = [[food], distance]
            elif distance == closestFood[tuple(head)][1]:
                closestFood[tuple(head)][0].append(food)

    for x in closestFood.values():
        for food in x[0]:
            if food in closestFood[tuple(my_head)][0] and x[1] < closestFood[tuple(my_head)][1]:
                closestFood[tuple(my_head)][0].remove(food)
        
    for food in food_location:
        key = tuple((*my_head, *food))
        my_distance = dp_dist[key]
        flag = True #closest to me
        my_food.append(food) # probable food
        for head in other_heads:
            key = tuple((*head, *food))
            distance = dp_dist[key]
            print("comp at {} i'm at {} my distance is {} his distance is {}".format(head,my_head,my_distance,distance))
            if distance < my_distance:
                # probability denied
                my_food.remove(food)
            if(distance <= my_distance):
                flag = False
                break
        if not flag:
            continue
        else:
            my_food.remove(food)
            direct = straightforward_bfs(mask, last_direction, *my_head, [food])
            if direct in direction_room.keys():
                heappush(max_heap, -1*direction_room[direct])
                corresponding_direction[direction_room[direct]] = direct

    if len(max_heap):
        print("available max heap and directions {} {}".format(max_heap, corresponding_direction))
    while len(max_heap):
        room = -1*heappop(max_heap)
        direct = corresponding_direction[room]
        if direct not in black_holes.values():
            print("found favourable food towards {}".format(direct))
            return direct

    if len(my_food):
        print("my options {}".format(my_food))
    for food in my_food:
        direct = straightforward_bfs(mask, last_direction, *my_head, [food])
        if direct in direction_room.keys():
            heappush(max_heap, -1*direction_room[direct])
            corresponding_direction[direction_room[direct]] = direct
    if len(max_heap):
        print("available max heap and directions {} {}".format(max_heap, corresponding_direction))
    while len(max_heap):
        room = -1*heappop(max_heap)
        direct = corresponding_direction[room]
        if direct not in black_holes.values():
            print("found favourable food towards {}".format(direct))
            return direct

    if len(closestFood[tuple(my_head)][0]):
        print("my other options {}".format(closestFood[tuple(my_head)][0]))
    for food in closestFood[tuple(my_head)][0]:
        direct = straightforward_bfs(mask, last_direction, *my_head, [food])
        if direct in direction_room.keys():
            heappush(max_heap, -1*direction_room[direct])
            corresponding_direction[direction_room[direct]] = direct
    print("available max heap and directions {} {}".format(max_heap, corresponding_direction))
    while len(max_heap):
        room = -1*heappop(max_heap)
        direct = corresponding_direction[room]
        if direct not in black_holes.values():
            print("found favourable food towards {}".format(direct))
            return direct

    # INSTEAD MOVE TOWARDS LOWEST TRAFFIC AND NO BLACK HOLE    
    temp = []
    last_option1 = []
    for cell in available_steps.keys():
        if cell in black_holes.keys():
            if len(last_option1) == 0 or last_option1[1] < available_steps[cell][1]:
                last_option1 = available_steps[cell]
        else:
            if len(temp) == 0 or temp[1] < available_steps[cell][1]:
                temp = available_steps[cell]
    if len(temp):
        print("moving towards temp 1 {}".format(temp[0]))
        return temp[0]

    temp = []
    last_option2 = []
    for cell in danger_area.keys():
        if cell in black_holes.keys():
            if len(last_option2) == 0 or last_option2[1] < danger_area[cell][1]:
                last_option2 = danger_area[cell]
        else:
            if len(temp) == 0 or temp[1] < danger_area[cell][1]:
                temp = danger_area[cell]
    if len(temp):
        print("moving towards temp 2 {}".format(temp[0]))
        return temp[0]
    
    if len(last_option1):
        print("moving towards last option 1 {}".format(last_option1[0]))
        return last_option1[0]
    if len(last_option2):
        print("moving towards last option 2 {}".format(last_option2[0]))
        return last_option2[0]

def agent(obs_dict, config_dict):
    observation = Observation(obs_dict)
    configuration = Configuration(config_dict)
    player_index = observation.index
    player_goose = observation.geese[player_index]
    player_head = player_goose[0]
    player_tail = player_goose[-1]
    my_X, my_Y = row_col(player_head, configuration.columns)
    my_tail_X, my_tail_Y = row_col(player_tail, configuration.columns)
    mask = np.zeros((configuration.rows, configuration.columns))
    
    global last_direction
    global iteration_number

    print("**iteration**: {}".format(iteration_number))
    print("my head at {} - {}".format([my_X, my_Y], last_direction))
    iteration_number+=1
    
    food_location = []
    available_steps = {}
    other_heads = [] # head of competitor geese
    body_cells = []
    other_tails = []
    last_direction_updated = False

    # add all directions
    possible_positions = get_nearest_cells(my_X, my_Y)
    for x, y in possible_positions:
        direct = '-'
        if((x-1 == my_X) or (x==0 and my_X==6)) and last_direction != 'NORTH':
            direct = 'SOUTH'
        elif((x+1 == my_X) or (x==6 and my_X==0)) and last_direction != 'SOUTH':
            direct = 'NORTH'
        elif((y-1 == my_Y) or (y==0 and my_Y==10)) and last_direction != 'WEST':
            direct = 'EAST'
        elif((y+1 == my_Y) or (y==10 and my_Y==0)) and last_direction != 'EAST':
            direct = 'WEST'
        if direct != '-':
            available_steps[(x,y)] = [direct,0]

    for food in observation.food:
        x,y = row_col(food, configuration.columns)
        mask[x, y] = 2
        food_location.append([x,y])
    print("food locations are {}".format(food_location))
  
    #   where other goose can come
    danger_area = {}
    for i in range(len(observation.geese)):
        opp_goose = observation.geese[i]
        if len(opp_goose) == 0:
            continue
        for ind, goose in enumerate(opp_goose):
            x, y = row_col(goose, configuration.columns)
            mask[x, y] = -1
            # and mark the occupied cells if not head or tail of goose
            if ind != 0 and ind != len(opp_goose) - 1:
                body_cells.append([x,y])
            if ind != 0 and ind == len(opp_goose) - 1:
                other_tails.append([x,y])
            if (x, y) in available_steps.keys():
                # let's remove all cells that are not available from available steps
                available_steps.pop((x,y))
            if (x, y) in danger_area.keys():
                # let's remove all cells that are not available from danger steps
                danger_area.pop((x,y))
            if not len(available_steps) and not len(danger_area): #if steps is empty kill by NORTH direction
                print("kill")
                if player_head!=player_tail and (my_tail_X, my_tail_Y) in possible_positions:
                    last_direction = get_direction((my_X, my_Y), (my_tail_X, my_tail_Y))
                else:
                    last_direction = 'NORTH'
                last_direction_updated = True
                break
        if last_direction_updated:
            break
        if i != player_index:
            x, y = row_col(opp_goose[0], configuration.columns)
            # add competition goose head
            other_heads.append([x, y])
            possible_moves = get_nearest_cells(x, y) # head can move anywhere
            for [x, y] in possible_moves:
                if (x,y) in available_steps.keys() and [x,y] in food_location:
                    danger_area[(x,y)] = available_steps[(x,y)]
                    available_steps.pop((x, y)) #only safe moves
                    food_location.remove([x,y]) #don't consider this food
                elif (x,y) in available_steps.keys() and len(available_steps)+len(danger_area) > 1:
                    danger_area[(x,y)] = available_steps[(x,y)]
                    available_steps.pop((x, y)) #only safe moves
        if last_direction_updated:
            break
    
    print("body cells are {}".format(body_cells))
    print("available steps are {}".format(available_steps))
    print("other heads at {}".format(other_heads))
    print("other tails at {}".format(other_tails))
    print("danger area at {}".format(danger_area))

    my_head = [my_X, my_Y]
    if not last_direction_updated:
            last_direction = my_move(food_location, available_steps, other_heads, my_head, last_direction, body_cells, danger_area, mask, other_tails)
            last_direction_updated = True

    return last_direction
