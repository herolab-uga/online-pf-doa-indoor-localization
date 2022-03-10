import math
import numpy as np
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from matplotlib import pyplot as pb
import random
from datetime import datetime
import time

# distance Calculation
def dist(x, y, pos):
    return math.sqrt((pos[0]-x)**2 + (pos[1]-y)**2)

# Simulation Environment variable Initialization
areaSize=(30, 30)
node_positions = (areaSize[0]+6,areaSize[1]+6)
node_pos=[(-node_positions[0],node_positions[1]),(node_positions[0],node_positions[1]),(node_positions[0],-node_positions[1]),(-node_positions[0],-node_positions[1])] # for 4 nodes
# node_pos=[(-node_positions[0],-node_positions[1]),(-node_positions[0],node_positions[1]),(node_positions[0],-node_positions[1])] # fro 3 nodes
initial_pos=(0,0) 
possible_value = list(range(-20, 20))
num_particles = 200
NOISE_LEVEL=1
RESOLUTION=5
Delta_X = 72
Delta_Y = 72
STEP_SIZE=1/RESOLUTION

# RSSI signal generation at pos(x,y) using path-loos model
def gen_wifi(freq=2.4, power=20, trans_gain=0, recv_gain=0, size=areaSize, pos=(5,5), shadow_dev=2, n=3,noise=NOISE_LEVEL):
    if pos is None:
        pos = (random.randrange(size[0]), random.randrange(size[1]))

    random.seed(datetime.now())
    rss0 = power + trans_gain + recv_gain + 20 * math.log10(3 / (4 * math.pi * freq * 10))
    rss0=rss0-noise*random.random()
    normal_dist = np.random.normal(0, shadow_dev, size=[size[0]+1, size[1]+1])
    rss = []

    random.seed(datetime.now())

    for x in range(0,3):
        distance = dist(node_pos[x][0], node_pos[x][1], pos)
        val =rss0 - 10 * n * math.log10(distance) + normal_dist[int(pos[0])][int(pos[1])]
        rss.append(val-noise*random.random())

    return rss


# Robot path trajectory generation

## To visualize Simulation, uncomment the plt code

# plt.ion()
# plt.title("Robot Trajectory")
# plt.ylim(-areaSize[1],areaSize[1])
# plt.xlim(-areaSize[0],areaSize[0])
# plt.plot( node_pos[0],node_pos[1], 'ro', markersize=5, clip_on=False, zorder=100)
# plt.plot( node_pos[2],node_pos[3], 'ro', markersize=5, clip_on=False, zorder=100)
# rss_pos=[(node_pos[0][0]+3,node_pos[0][1]-1),(node_pos[1][0]-25,node_pos[1][1]-1),(node_pos[2][0]-25,node_pos[2][1]-1),(node_pos[3][0]+3,node_pos[3][1]-1)]
text=[]
overall_rss=[]
original_tragectory=[]
Previous_pos = initial_pos

# for i in range(0,4):
#     text.append(plt.text(rss_pos[i][0],rss_pos[i][1], 'RSS'+str(i), fontsize=10))

def move(pos):
    x,y=pos[0],pos[1]
    original_tragectory.append((x,y))
    # plt.plot([Previous_pos[0],x],[Previous_pos[1],y],'g-',linewidth=2,clip_on=False)
    rss = gen_wifi(pos=(x,y))
    overall_rss.append(rss)
    # for i in range(0,4):
    #     text[i].set_text('RSS'+str(i+1)+'='+str(round(rss[i], 2)))
    # plt.draw()
    # plt.pause(0.0001)
x=0
for y in np.arange(0,areaSize[1],STEP_SIZE):
    move((x,y))
    Previous_pos = (x,y)
y=areaSize[1]
for x in np.arange(0,areaSize[0],STEP_SIZE):
    move((x,y))
    Previous_pos = (x,y)
x=areaSize[0]
for y in np.arange(areaSize[1],-areaSize[1],-STEP_SIZE):
    move((x,y))
    Previous_pos = (x,y)
y=-areaSize[1]
for x in np.arange(areaSize[0],-areaSize[0],-STEP_SIZE):
    move((x,y))
    Previous_pos = (x,y)
x=-areaSize[0]
for y in np.arange(-areaSize[0],areaSize[0],STEP_SIZE):
    move((x,y))
    Previous_pos = (x,y)
y=areaSize[1]
for x in np.arange(-areaSize[0],0,STEP_SIZE):
    move((x,y))
    Previous_pos = (x,y)

# plt.show(block=False)
# plt.savefig('PF_tragectory_boundry.png')
# plt.pause(3)
# plt.clf()
# plt.close()


# plt.ion()
# plt.ylim(-areaSize[1],areaSize[1])
# plt.xlim(-areaSize[0],areaSize[0])

random.seed(datetime.now())
previous_errors =[]
distance_error =[]
particles = []
Previous_pos = initial_pos
start_time = time.time()

for x in np.arange(-areaSize[0],areaSize[0],STEP_SIZE*2):
    for y in np.arange(-areaSize[1],areaSize[1],STEP_SIZE*2):
        particles.append((x,y))

# plt.title("Predicted Robot Positions")
for i in range(0,len(original_tragectory)):
    positions =[]
    errors=[]
    weights =[]
    rands = []
    range_probs = []
    error=0
    for particle in particles:
        x,y=particle[0],particle[1]
        actual_rss = gen_wifi(pos=(x,y),noise=0)
        error = np.sum(np.subtract(actual_rss,overall_rss[i]))
        positions.append((x,y))
        errors.append(error)


    min_error = min(errors)
    min_index = errors.index(min_error)
    pos=positions[min_index]
    print(pos)
    previous_errors.append(errors[min_index])
    distance_error.append(dist(pos[0],pos[1],original_tragectory[i]))

# plt.show(block=False)
# plt.savefig('PF_predicted_trajectory_boundry.png')
print("--- Computation Time: %s seconds ---" % (time.time() - start_time))
distcumulativeEror=np.sum(distance_error)/10
distmeanError=np.average(distance_error)/10
distStandardDeviationError=np.std(distance_error)/10
print("DIST_ERROR:   Cumulative Error: " + str(distcumulativeEror)+"\tMean  Error: "+str(distmeanError)+"\tStandard Deviation: "+str(distStandardDeviationError))
resultFile = open("error_boundry_Markov_full(6by6).csv", "a")  # append mode
resultFile.write(str(distcumulativeEror)+","+str(distmeanError)+","+str(distStandardDeviationError)+"\n")


resultFile.close()
# plt.pause(3)
# plt.clf()
# plt.close()

