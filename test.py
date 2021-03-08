from submission import straightforward_bfs, bfs
from heapq import heapify, heappush, heappop
import numpy as np

dist = []
max_heap = []
corresponding_direction = {}
heapify(max_heap)

for food in food_location:
    my_distance = bfs(*my_head, mask, [food], 1)
    flag = True #closest to me
    my_food.append(food) # probable food
    for head in other_heads:
        distance = bfs(*head, mask, [food], 1)
        print("comp at {} i'm at {} my distace is {} his distance is {}".format(head,my_head,my_distance,distance))
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