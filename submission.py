from kaggle_environments.envs.hungry_geese.hungry_geese import Observation, Configuration, Action, row_col
from random import choice, sample, randint, seed
from operator import eq
last_direction = None
iteration_number = 1
# 11 X 7 grid
# -----------------------------
#    1 2 3 4 5 6 7 8 9 10 11  |
# 1  - - - - N - - - R - -    |
# 2  - - - M - - - - - - -    |
# 3  - - - - - - - - - - -    |
# 4  - - O - X - - - P - -    |
# 5  - - - - - - - - - - -    |
# 6  - Z - - Y - - - - - -    | (5,8)
# 7  - - - - - - - - Q - -    | (6,4)
# -----------------------------

def random_agent(directions):
    seed(None,randint(1,2))
    step = choice(directions)
    seed(1)
    return step

def get_nearest_cells(x,y):
    # returns all cells reachable from the current one
    result = []
    for i in (-1,+1):
        result.append(((x+i+7)%7, y))
        result.append((x, (y+i+11)%11))
    return result

# will not consider blocking
def tell_distance(x1, y1, x2, y2):
    x_dist = min(abs(x2-x1), 7 - abs(x2-x1))
    y_dist = min(abs(y2-y1), 11 - abs(y2-y1))
    return x_dist + y_dist

# will not consider blocking
def get_direction(head, target):
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

# if two directions are opposite return true
def opposite_direct(a,b):
    if a =='NORTH' and b == 'SOUTH' or a =='SOUTH' and b == 'NORTH':
        return True
    if a =='EAST' and b == 'WEST' or a =='WEST' and b == 'EAST':
        return True
    return False

def my_move(food_location, available_steps, other_goose, my_head, last_direction, occupied_cells):
    my_food = []
    traffic_direction = {val[0]:val[1] for val in available_steps.values()}

    for food in food_location:
        my_dist = tell_distance(my_head[0],my_head[1],food[0],food[1])
        flag = True #closest to me
        my_food.append(food) # probable food
        for head in other_goose:
            dist = tell_distance(head[0], head[1], food[0], food[1])
            if dist < my_dist:
                # probability denied
                my_food.remove(food)
            if(dist <= my_dist):
                flag = False
                break
        if not flag:
            continue
        else:
            direct = get_direction(my_head, food)
            if direct in traffic_direction.keys() and not opposite_direct(direct, last_direction) and traffic_direction[direct] != 4:
                # print("found closer than others at {} : heading {}".format(food, direct))
                return direct

    # print("my options {}".format(my_food))
    for food in my_food:
        direct = get_direction(my_head, food)
        if direct in traffic_direction.keys() and not opposite_direct(direct, last_direction) and traffic_direction[direct] != 4:
            # print("going with option {} : heading {}".format(food, direct))
            return direct
    
    # INSTEAD MOVE AWAY FROM COMPETITION
    temp = min(traffic_direction.values()) 
    direct = [key for key in traffic_direction if traffic_direction[key] == temp]
    # print("going for random {}".format(direct))
    return direct[0]

def agent(obs_dict, config_dict):
    observation = Observation(obs_dict)
    configuration = Configuration(config_dict)
    player_index = observation.index
    player_goose = observation.geese[player_index]
    player_head = player_goose[0]
    my_X, my_Y = row_col(player_head, configuration.columns)
    global last_direction
    global iteration_number

    # print("**iteration**: {}".format(iteration_number))
    iteration_number+=1
    # print("my head at {}".format([my_X, my_Y]))
    food_location = []
    available_steps = {}
    other_goose = [] # head of competitor geese
    occupied_cells = []
    possible_positions = get_nearest_cells(my_X, my_Y)
    last_direction_updated = False

    # add all directions
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
        if(direct!= '-'):
            available_steps[(x,y)] = [direct,0]

    for food in observation.food:
        x,y = row_col(food, configuration.columns)
        food_location.append([x,y])
    # print("food locations are {}".format(food_location))

    # let's remove all cells that are not available for me to move from available steps
    # and mark the occupied cells
    for i in range(len(observation.geese)):
        opp_goose = observation.geese[i]
        if len(opp_goose) == 0:
            continue
        for ind in opp_goose:
            x, y = row_col(ind, configuration.columns)
            occupied_cells.append([x,y])
            if (x, y) in available_steps.keys():
                available_steps.pop((x,y)) # this position is already taken
                if(not len(available_steps)): #if available steps is empty kill by random direction
                    print("kill")
                    last_direction = random_agent(["NORTH", "EAST", "SOUTH", "WEST"])
                    last_direction_updated = True
                    break
        if last_direction_updated:
            break
        if i != player_index:
            x, y = row_col(opp_goose[0], configuration.columns)
            other_goose.append([x, y])
            possible_moves = get_nearest_cells(x, y) # head can move anywhere
            for [x, y] in possible_moves:
                if (x,y) in available_steps.keys() and [x,y] in food_location:
                    available_steps.pop((x, y)) #only safe moves
                    food_location.remove([x,y])
                    if not len(available_steps):
                        # print("give me my food else i will have to die")
                        last_direction_updated = True
                        if (x-1 == my_X) or (x==0 and my_X==6):
                            last_direction = 'SOUTH'
                        elif (x+1 == my_X) or (x==6 and my_X==0):
                            last_direction = 'NORTH'
                        elif (y-1 == my_Y) or (y==0 and my_Y==10):
                            last_direction = 'EAST'
                        elif (y+1 == my_Y) or (y==10 and my_Y==0):
                            last_direction = 'WEST'
                        break
        if last_direction_updated:
            break

    #calculate traffic around that direction
    for (x, y) in available_steps.keys():
        all_steps = get_nearest_cells(x, y)
        available_steps[(x,y)][1] = sum(map(eq, all_steps, occupied_cells))
    
    # print("occupied cells are {}".format(occupied_cells))
    # print("available steps are {}".format(available_steps))
    # print("comp heads at {}".format(other_goose))

    # the first step toward the nearest favourable food
    my_head = [my_X, my_Y]
    if not last_direction_updated:
            last_direction = my_move(food_location, available_steps, other_goose, my_head, last_direction, occupied_cells)
            last_direction_updated = True

    return last_direction