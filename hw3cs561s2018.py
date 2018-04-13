import copy
from enum import Enum
import time
start_time = time.time()
import heapq

priority = [["up_walk",0],["down_walk",0],["left_walk",0],["right_walk",0],["up_run",0],["down_run",0],["left_run",0],["right_run",0],]
print_moves = {"up_walk":"Walk Up","left_walk":"Walk Left","right_walk":"Walk Right","down_walk":"Walk Down","up_run":"Run Up","left_run":"Run Left","right_run":"Run Right","down_run":"Run Down"}

directions = {
    "up_walk" : [(1,0),(0,-1),(0,1),(1,0),(0,-1),(0,1)],         #up,left,right
    "left_walk" : [(0,-1),(-1,0),(1,0),(0,-1),(-1,0),(1,0)],      #left,down,up
    "right_walk" : [(0,1),(1,0),(-1,0),(0,1),(1,0),(-1,0)],      #right,up,down
    "down_walk" : [(-1,0),(0,-1),(0,1),(-1,0),(0,-1),(0,1)],      #down,left,right
    "up_run" : [(2,0),(0,-2),(0,2),(1,0),(0,-1),(0,1)],
    "left_run" : [(0,-2),(-2,0),(2,0),(0,-1),(-1,0),(1,0)],
    "right_run" : [(0,2),(2,0),(-2,0),(0,1),(1,0),(-1,0)],
    "down_run" : [(-2,0),(0,-2),(0,2),(-1,0),(0,-1),(0,1)],
}

neighbours = [(1,0),(-1,0),(0,1),(0,-1),(2,0),(-2,0),(0,2),(0,-2)]
P_QUEUE = []  # priority queue of states (used for prioritized sweeping)
STATE2PRIORITY = {}  # map from a state to its priority

class Grid:
    def __init__(self, rows, cols, wall_no, wall_pos, t_no, t_pos_reward, p_walk, p_run, r_walk, r_run, discount, grid):
        self.rows = rows
        self.cols = cols
        self.wall_no = wall_no
        self.wall_pos = copy.deepcopy(wall_pos)
        self.t_no = t_no
        self.t_pos_reward = copy.deepcopy(t_pos_reward)
        self.p_walk = p_walk
        self.p_run = p_run
        self.r_walk = r_walk
        self.r_run = r_run
        self.discount = discount
        self.grid = grid
    

#reads input file and does necessary formatting
def read_input_file():
    global priority    
    input_file = open("input.txt")
    ip = input_file.read().splitlines()

    #get grid size i.e. rows and columns of the grid world
    grid_size = ip[0].split(",")
    rows = int(grid_size[0])
    cols = int(grid_size[1])

    #get wall cell numbers and position
    wall_no = int(ip[1])
    wall_pos = []
    for i in range(2,(wall_no + 2)):
        t =ip[i].split(",")
        temp_wall = []
        temp_wall.append(int(t[0])-1)
        temp_wall.append(int(t[1])-1)
        wall_pos.append(temp_wall)

    #get terminal state number, position and rewards
    t_no = int(ip[2+wall_no])
    t_pos_reward = {}
    for i in range(wall_no + 3, wall_no + 3 + t_no):
        t = ip[i].split(",")
        temp_t = {}
        #print str(int(t[0])-1) + "_" + str(int(t[1])-1)
        temp_t[str(int(t[0])-1) + "_" + str(int(t[1])-1)] = (float(t[2]))
        t_pos_reward.update(temp_t)
    
    #read transition model, rewards, and discount factor
    p = ip[wall_no + 3 + t_no].split(",")
    p_walk = float(p[0])
    p_run = float(p[1])

    r = ip[wall_no + 3 + t_no + 1].split(",")
    r_walk = float(r[0])
    r_run = float(r[1])

    discount = float(ip[wall_no + 3 + t_no + 2])

    input_file.close()    

    #put all the read values in the grid world object
    temp_obj = Grid(rows, cols, wall_no, wall_pos, t_no, t_pos_reward, p_walk, p_run, r_walk, r_run, discount, {})

    for i in range(0,4):
        priority[i][1] = r_walk
    for i in range(4,8):
        priority[i][1] = r_run  

    return temp_obj

def check_values_in_object(obj):
    print "Grid rows: ",obj.rows
    print "Grid cols: ",obj.cols
    print "No. of walls: ",obj.wall_no
    print "Wall positions: ",obj.wall_pos
    print "Terminal states: ",obj.t_no
    print "Terminal position and rewards: ",obj.t_pos_reward
    print "p_walk: ",obj.p_walk
    print "p_run: ",obj.p_run
    print "r_walk: ",obj.r_walk
    print "r_run: ",obj.r_run
    print "Discount: ",obj.discount  
    print "Grid: \n",obj.grid

def generate_inital_trasitions(obj):
    global directions

    for i in range(0, obj.rows):
        for j in range(0, obj.cols):
            k = str(i) + "_" + str(j)
            if obj.grid.has_key(k):
                for direction in directions:
                    if direction[-1] == 'n':
                        #print direction, directions[direction],directions[direction][0][0]
                        
                        action_run(i,j,obj,k,direction)
                    else:
                        #print direction, directions[direction],directions[direction][0][0]
                        action_walk(i,j,obj,k,direction)
                    #print type(obj.grid[k][direction])
                

            else:   #if state is not in the grid
                continue
    



def action_walk(i, j, obj, k, direction): #list from the dict, x is 1 (walk) or 2 (run)
    global directions
#UP
    temp_tup = {}
    z_key = str(i+directions[direction][0][0]) + "_" + str(j+directions[direction][0][1]) 
    if obj.grid.has_key(z_key):
            temp_tup[z_key] = obj.p_walk
    else:
            temp_tup[k] = obj.p_walk

    if obj.grid[k][direction].has_key(temp_tup.keys()[0]):
        obj.grid[k][direction][temp_tup.keys()[0]] += temp_tup.values()[0]
    else:
        obj.grid[k][direction].update(temp_tup)

#LEFT
    temp_tup = {}
    z_key = str(i+directions[direction][1][0]) + "_" + str(j+directions[direction][1][1])
    if obj.grid.has_key(z_key):
            temp_tup[z_key] = (0.5 * (1 - obj.p_walk))
    else:
            temp_tup[k] = (0.5 * (1 - obj.p_walk))#obj.p_walk

    if obj.grid[k][direction].has_key(temp_tup.keys()[0]):
        obj.grid[k][direction][temp_tup.keys()[0]] += temp_tup.values()[0]
    else:
        obj.grid[k][direction].update(temp_tup)

#RIGHT
    temp_tup = {}
    z_key = str(i+directions[direction][2][0]) + "_" + str(j+directions[direction][2][1])
    if obj.grid.has_key(z_key):
            temp_tup[z_key] = (0.5 * (1 - obj.p_walk))
    else:
            temp_tup[k] = (0.5 * (1 - obj.p_walk)) #obj.p_walk

    if obj.grid[k][direction].has_key(temp_tup.keys()[0]):
        obj.grid[k][direction][temp_tup.keys()[0]] += temp_tup.values()[0]
    else:
        obj.grid[k][direction].update(temp_tup)





def action_run(i, j, obj, k, direction): #list from the dict, x is 1 (walk) or 2 (run)
    global directions
#UP
    temp_tup = {}
    z_key = str(i+directions[direction][0][0]) + "_" + str(j+directions[direction][0][1]) 
    if obj.grid.has_key(z_key) and obj.grid.has_key(str(i+directions[direction][3][0]) + "_" + str(j+directions[direction][3][1])):
            temp_tup[z_key] = obj.p_run
    else:
            temp_tup[k] = obj.p_run

    if obj.grid[k][direction].has_key(temp_tup.keys()[0]):
        obj.grid[k][direction][temp_tup.keys()[0]] += temp_tup.values()[0]
    else:
        obj.grid[k][direction].update(temp_tup)

#LEFT
    temp_tup = {}
    z_key = str(i+directions[direction][1][0]) + "_" + str(j+directions[direction][1][1])
    if obj.grid.has_key(z_key) and obj.grid.has_key(str(i+directions[direction][4][0]) + "_" + str(j+directions[direction][4][1])):
            temp_tup[z_key] = (0.5 * (1 - obj.p_run))
    else:
            temp_tup[k] = (0.5 * (1 - obj.p_run))#obj.p_run

    if obj.grid[k][direction].has_key(temp_tup.keys()[0]):
        obj.grid[k][direction][temp_tup.keys()[0]] += temp_tup.values()[0]
    else:
        obj.grid[k][direction].update(temp_tup)

#RIGHT
    temp_tup = {}
    z_key = str(i+directions[direction][2][0]) + "_" + str(j+directions[direction][2][1])
    if obj.grid.has_key(z_key) and obj.grid.has_key(str(i+directions[direction][5][0]) + "_" + str(j+directions[direction][5][1])):
            temp_tup[z_key] = (0.5 * (1 - obj.p_run))

    else:
            temp_tup[k] = (0.5 * (1 - obj.p_run)) #obj.p_run

    if obj.grid[k][direction].has_key(temp_tup.keys()[0]):
        obj.grid[k][direction][temp_tup.keys()[0]] += temp_tup.values()[0]
    else:
        obj.grid[k][direction].update(temp_tup)






def generate_grid(obj):
    global directions
    #Generate keys for the grid first
    for i in range(0, obj.rows):
        for j in range(0, obj.cols):
            k = str(i) + "_" + str(j)
            obj.grid[k] = {"up_walk":{},"left_walk":{},"right_walk":{},"down_walk":{},"up_run":{},"left_run":{},"right_run":{},"down_run":{}}

    #remove states having walls from the grid
    for i in range(0, obj.wall_no):
        k = str(obj.wall_pos[i][0]) + "_" + str(obj.wall_pos[i][1])
        obj.grid.pop(k,None)

    generate_inital_trasitions(obj) 

    #remove terminal states
    for terminal in obj.t_pos_reward.keys():
        obj.grid[terminal] = {"up_walk":{},"left_walk":{},"right_walk":{},"down_walk":{},"up_run":{},"left_run":{},"right_run":{},"down_run":{}}
        #print obj.grid[terminal]
    #add corresponding probabilities to each move


    #for x in obj.grid.keys():
       # print x,obj.grid[x],"\n"
   

def calculate_max(state, current_position, U2, discount, terminal_states):
    max_value = float("-inf")
    global priority

    #if it is a terminal state, add only reward associated with it
    if current_position in terminal_states.keys():
        return terminal_states[current_position], "Exit" 

    for i in range(0,8):
        sum = 0
        for key in state[priority[i][0]].keys():            
            sum +=  (state[priority[i][0]][key] * (priority[i][1] + discount * U2[key]))            
        if max_value < sum:
            max_value = sum
            max_value_step = priority[i][0]

 

    return max_value, max_value_step


def value_iteration(obj):
    V={}
    nV={}

    
    assert len(P_QUEUE) == len(STATE2PRIORITY) == 0
    V = {state: 0 for state in obj.grid.keys()}
    nV = {state: 0 for state in obj.grid.keys()}


    # first iteration, we don't have anything in our priority queue, add states that will change in the next sweep:
    for state in obj.grid.keys():
        #nV[state], dev_null = calculate_max(obj.grid[state], state, nV, obj.discount, obj.t_pos_reward)
        v = nV[state]
        #TERMINAL STATE
        if state in obj.t_pos_reward.keys():
            nV[state] = obj.t_pos_reward[state] 
        else:
            utility_for_orientation = []
            for i in range(0,8):
                sum = 0
                for key in obj.grid[state][priority[i][0]].keys():            
                    sum +=  (obj.grid[state][priority[i][0]][key] * (priority[i][1] + obj.discount * nV[key])) 
                utility_for_orientation.append(sum)
            nV[state] = max(utility_for_orientation)        
        delta = abs(nV[state] - v)

        if delta > 0:
            heapq.heappush(P_QUEUE, (-delta, state))  # add s with priority -delta (most probable = lower value).
            STATE2PRIORITY[state] = -delta  # keep track of its priority.
        

    # Iterate over states in the priority queue:
    iteration = 1  # iteration index
    while len(P_QUEUE) > 0:
        _, s = heapq.heappop(P_QUEUE)  # pop most probable state.
        del STATE2PRIORITY[s]  # forget its priority.

        # do one Bellman Backup of current state:
        v = V[s]  # old state-value
        #V[s], moves[s] = calculate_max(obj.grid[s], s, V, obj.discount, obj.t_pos_reward)
        #TERMINAL STATE
        if s in obj.t_pos_reward.keys():
            V[s] = obj.t_pos_reward[s] 
        else:
            utility_for_orientation = []
            for i in range(0,8):
                sum = 0
                for key in obj.grid[s][priority[i][0]].keys():            
                    sum +=  (obj.grid[s][priority[i][0]][key] * (priority[i][1] + obj.discount * V[key])) 
                utility_for_orientation.append(sum)
            V[state] = max(utility_for_orientation)
        delta = abs(v-V[s])

        
        #Find neighbours
        k = s.split("_")
        neighbour_states = {}
        for i in range(0,8):
            a={}
            a_key = str(int(k[0])+neighbours[i][0]) + "_" + str(int(k[1])+neighbours[i][1])
            if obj.grid.has_key(a_key):
                a[a_key] = 0
                neighbour_states.update(a)
        #print neighbour_states
        
        # add neighbors to the priority queue:
        for s1 in neighbour_states:
            max_value = 0
            max_value_move = ""
            for i in range(0,8):
                sum = 0
                for key in obj.grid[s1][priority[i][0]].keys():
                    sum +=  (obj.grid[s1][priority[i][0]][key] * delta)
                                
                if max_value < sum:
                    max_value = sum
            new_priority = -max_value
            #print -max_value
            #new_priority = - max([delta * P[s1, a, s] for a in obj.grid[s])  # how much s1 is influenced by the current change.
            if new_priority < 0:
                # most probable = min value between current and new priority.
                if s1 in STATE2PRIORITY and STATE2PRIORITY[s1] > new_priority:  # update element in priority queue
                    old_priority = STATE2PRIORITY[s1]
                    index = P_QUEUE.index((old_priority, s1))  # current index in the priority queue.
                    P_QUEUE[index] = (new_priority, s1)  # update current priority.
                    STATE2PRIORITY[s1] = new_priority  # keep track of the update.
                elif s1 not in STATE2PRIORITY:  # add new state to priority queue
                    heapq.heappush(P_QUEUE, (new_priority, s1))  # push to priority queue.
                    STATE2PRIORITY[s1] = new_priority  # keep track of its priority.'''
        print "Queue Length: ", len(P_QUEUE)
        print "Iteration: ",iteration
        iteration += 1

    return V

def best_policy(obj,U):
    global priority
    moves = {}

    for state in obj.grid.keys():
        #state = '0_19'
        max_val_move = ""
        max_val = -float("inf")
        for i in range(0,8):
            sum = 0
            #print obj.grid[state][priority[i][0]].keys()
            for key in obj.grid[state][priority[i][0]].keys(): 
                #print obj.grid[state][priority[i][0]][key]           
                sum +=  (obj.grid[state][priority[i][0]][key] * (priority[i][1] + obj.discount * U[key]))    
                        ##probability                   Reward          gamma       next move -> 3
            #print i,priority[i][0],sum
            if max_val < sum:
                max_val = sum
                max_val_move = priority[i][0]

        #print state,max_val_move,sum
        #exit()
        #print max_val
        #print max_val_move
        temp_dict = {}
        temp_dict[state] = max_val_move
        moves.update(temp_dict)

    return moves

def main():
    obj = read_input_file()
    #check_values_in_object(obj)
    generate_grid(obj)
    print "!! GRID DONE !!"  

    final_utility = value_iteration(obj)
    print "!! Value Iteration Done !!"
    moves = best_policy(obj,final_utility)
    print "!! best policy Done !!"
    
    wall_pos = {}
    for x in obj.wall_pos:
        k = str(x[0]) + "_" + str(x[1])
        wall_pos[k] = 0
    '''print moves
    print wall_pos
    print len(obj.grid)
    print len(moves)
    print len(wall_pos)
    print len(obj.t_pos_reward)'''


    op = open("output.txt","w")
    output_record = []
    for row in range(obj.rows):
        output_row = []
        for column in range(obj.cols):
            state = str(row) + "_" + str(column)
            #print state
            if state in wall_pos.keys():
                #print state, "None"
                output_row.append("None")
            elif state in obj.t_pos_reward.keys():
                #print state, "Exit"
                output_row.append("Exit")
            else:
                #print state, print_moves[moves[state]]
                output_row.append(print_moves[moves[state]])
        output_record.append(",".join(output_row))
    
    final_output_record = reversed(output_record)
    op.write("\n".join(final_output_record))
    op.close()
    print("--- %s seconds ---" % (time.time() - start_time))

#call to main function
if __name__ == '__main__':
    main()