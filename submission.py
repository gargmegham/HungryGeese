from kaggle_environments.envs.hungry_geese.hungry_geese import Observation, Configuration, Action, row_col
from random import choice, sample, randint, seed
# 11 X 7 grid
# -----------------------------
#    1 2 3 4 5 6 7 8 9 10 11  |
# 1  - - - - - - - - - - -    |
# 2  - - - - - - - - - - -    |
# 3  - - - - - - - - - - -    |
# 4  - - - - - - - - - - -    |
# 5  - - - - - - - - - - -    |
# 6  - - - - - - - - - - -    |
# 7  - - - - X - - - - - -    |
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

def direction(X, Y, x, y):
    if x > X:
        return 'SOUTH'         
    if y > Y:
        return 'EAST'
    if x < X:
        return 'NORTH'                
    if y < Y:
        return 'WEST'

def find_favourable_move(food_location, available_steps, comp_head, my_head):
    print("my head at {}".format(my_head))
    my_food = []
    for food in food_location:
        my_dist = abs(my_head[0] - food[0]) + abs(my_head[1] - food[1])
        flag = True #closest
        my_food.append(food)
        for comp in comp_head:
            dist = abs(comp[0] - food[0]) + abs(comp[1] - food[1])
            if dist < my_dist:
                my_food.remove(food)
            if(dist <= my_dist):
                flag = False
                break
        if not flag:
            continue
        else:
            direct = direction(my_head[0], my_head[1], food[0], food[1])
            if direct in available_steps.values():
                print("found closer at {} : heading {}".format(food, direct))
                return direct
    print("closest {}".format(my_food))
    for food in my_food:
        direct = direction(my_head[0], my_head[1], food[0], food[1])
        if direct in available_steps.values():
            return direct
    
    direct = random_agent(list(available_steps.values()))
    print("going for random {}".format(direct))
    return direct

def agent(obs_dict, config_dict):
    observation = Observation(obs_dict)
    configuration = Configuration(config_dict)
    player_index = observation.index
    player_goose = observation.geese[player_index]
    player_head = player_goose[0]
    X, Y = row_col(player_head, configuration.columns)

    food_location = []
    available_steps = {}

    for x, y in get_nearest_cells(X, Y):
        direct = '-'
        if(x-1 == X) or (x==0 and X==6):
            direct = 'SOUTH'
        if(x+1 == X) or (x==6 and X==0):
            direct = 'NORTH'
        if(y-1 == Y) or (y==0 and Y==10):
            direct = 'EAST'
        if(y+1 == Y) or (y==10 and Y==0):
            direct = 'WEST'
        available_steps[(x,y)] = direct
    print("available_steps are {}".format(available_steps))        

    comp_head = [] # head of other geese

    # add food
    for food in observation.food:
        x,y = row_col(food, configuration.columns)
        food_location.append([x,y])
    print("food locations are {}".format(food_location))
    
    # let's add all cells that are available
    for i in range(len(observation.geese)):
        opp_goose = observation.geese[i]
        if len(opp_goose) == 0:
            continue
        occupied = []
        for ind in opp_goose:
            x,y = row_col(ind, configuration.columns)
            occupied.append([x,y])
            if (x,y) in available_steps.keys():
                available_steps.pop((x,y)) # this position is already taken
                if(not len(available_steps)):
                    print("kill")
                    return 'SOUTH'
        
        if i != player_index:
            x, y = row_col(opp_goose[0], configuration.columns)
            comp_head.append([x,y])
            possible_moves = get_nearest_cells(x,y) # head can move anywhere
            for [x,y] in possible_moves:
                if (x,y) in available_steps.keys() and [x,y] in food_location:
                    if(len(available_steps) == 1):
                        print("give me my food")
                        return direction(X, Y, x, y)
                    available_steps.pop((x,y)) #only safe moves

    print("occupied cells are {}".format(occupied))
    print("available steps are {}".format(available_steps))
    print("comp heads at {}".format(comp_head))
    # the first step toward the nearest favourable food
    my_head = [X,Y]
    return find_favourable_move(food_location, available_steps, comp_head, my_head)