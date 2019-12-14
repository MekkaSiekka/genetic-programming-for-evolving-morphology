import matplotlib.pyplot as plt
import numpy as np
import os
# Variable: how many groups you have run for one experiment
num = 3
from sklearn.utils import shuffle
from collections import defaultdict

NUM_PER_GEN = 0
def read_file_to_np(dir_name):
    files = os.listdir(dir_name)
    all_x = np.zeros((0,1))
    all_y = np.array((0,1))
    for i in range(0,len(files)):
        txt_name = dir_name+'/'+files[i];
        #read-in the txt file as a list of pairs
        with open(txt_name) as f:
            content = f.readlines()
            content = [x.strip() for x in content] 

        x_array = []
        y_array = []

        #add x y seperately into python arrays. Each index of x/y array corresponds to a point
        for str_pair in content:
            x=float(str_pair.split()[0])
            y=float(str_pair.split()[1])
            x_array.append(x)
            y_array.append(y)

        x_array = np.array(x_array)
        y_array = np.array(y_array)
        x_array = x_array.reshape(1,x_array.shape[0])
        y_array = y_array.reshape(1,y_array.shape[0])

        if i == 0:
            all_x = x_array
            all_y = y_array
        else:
            all_x = np.concatenate((all_x,x_array),axis = 0)
            all_y = np.concatenate((all_y,y_array),axis = 0)
        print(all_x.shape)
    #plt.plot(all_x[1], all_y[1], '-')
    return all_x,all_y


def get_error(all_x,all_y):
    print("all_y")
    y_var = np.var(all_y,axis=0)
    idx_arr = np.arange(1,y_var.shape[0]+1).reshape(y_var.shape[0])
    y_error = y_var / np.sqrt(idx_arr)
    return y_error



def read_dots(file_name):
        with open(file_name) as f:
            content = f.readlines()
            content = [x.strip() for x in content] 

        x_array = []
        y_array = []

        #add x y seperately into python arrays. Each index of x/y array corresponds to a point
        for str_pair in content:
            x=float(str_pair.split()[0])
            y=float(str_pair.split()[1])
            x_array.append(x)
            y_array.append(y)

        x_array = np.array(x_array)
        y_array = np.array(y_array)
        x_array = x_array.reshape(1,x_array.shape[0])
        y_array = y_array.reshape(1,y_array.shape[0])

        return x_array,y_array

#given a file name, read related data
def read_all(file_name):
    with open(file_name) as f:
        content = f.readlines()
        content = [x.strip().split() for x in content] 
    #print(content)
    x_array = []
    y_array = []
    diversity_x = []
    diversity_y = []
    fitness_x = []
    converge_x= []
    fitness_y = []
    converge_y= []
    pos = 0
    dot_x =[]
    dot_y =[]
    num = int(content[pos][0])
    pos = pos+1
    for i in range(0,num):
        #pair = content[pos].split()
        converge_x.append( int(content[pos][0]) )
        converge_y.append( float(content[pos][1]) )
        pos = pos+1

    #print(converge_x)
   
    num = int(content[pos][0])
    pos = pos+1
    for i in range(0,num):
        #pair = content[pos].split()
        fitness_x.append(int(content[pos][0]))
        fitness_y.append(float(content[pos][1]))
        pos = pos+1
    #print(fitness_x)

    num = int(content[pos][0])
    pos = pos+1
    for i in range(0,num):
        #pair = content[pos].split()
        diversity_x.append( int(content[pos][0])   )
        diversity_y.append(  float(content[pos][1])   )
        pos = pos+1
    #print(diversity_x)

    num = int(content[pos][0])
    pos = pos+1
    #print("num",num)
    for i in range(0,num):
        x = float(content[pos][0])
        #dot_x.append(x)
        pos = pos+1

        num2 = float(content[pos][0])
        #print("num2",num2)
        pos=pos+1
        #step_dots = []
        for j in range(0,int(num2)):
            NUM_PER_GEN = num2
            dot_x.append(x)
            dot_y.append(content[pos][0])
            pos= pos+1
    # print(dot_x[499:510])
    # print(dot_y[499:510])
    # for i in range(0,len(dot_x)):
    #     print(dot_x[i],dot_y[i])

    dot_x = np.array(dot_x)
    dot_y = np.array(dot_y)

    dot_x = dot_x.reshape(dot_x.shape[0]).astype(float)
    dot_y = dot_y.reshape(dot_y.shape[0]).astype(float)
    # a, b = shuffle(dot_x, dot_y, random_state=0)
    # print(a.shape)
    # plt.ylim(0,0.0025)
    # plt.scatter(a[0:5000],b[0:5000],s=5)
    # plt.show()
    #return (fitness_x,fitness_y,converge_x,converge_y)
    return (diversity_x,
        diversity_y,
        fitness_x ,
        converge_x,
        fitness_y ,
        converge_y,
        dot_x,
        dot_y)
    #add x y seperately into python arrys. Each index of x/y array corresponds to a point



#read_all("GP1155315267.txt")

files = os.listdir()


types = ["RD","HC","EA"]
#types = ["EA","HC","RD","GD"]
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

for t in types:
    f_name = [x for x in files if x[0:2]==t]
    all_fitness_x = []
    all_fitness_y = []
    for name in f_name:
        (diversity_x,
        diversity_y,
        fitness_x ,
        converge_x,
        fitness_y ,
        converge_y,
        dot_x,
        dot_y )= read_all(name)

        all_fitness_x.append(fitness_x)
        all_fitness_y.append(fitness_y)
    print("all_fitness_x",all_fitness_x)
    all_fitness_x = np.array(all_fitness_x).astype(float)
    all_fitness_y = np.array(all_fitness_y).astype(float)
    avg_x = np.average(all_fitness_x,axis = 0)
    avg_y = np.average(all_fitness_y,axis = 0)
    ax1.plot(avg_x,avg_y,label=f_name[0][0:2])
    y_error =  get_error(all_fitness_x,all_fitness_y)
    ax1.fill_between(avg_x, avg_y-y_error*20, avg_y+y_error*20,alpha=0.5)
    #plt.errorbar(all_fitness_x[0],all_fitness_y[0],yerr= y_error,alpha=0.3)
plt.xlim(0,10000)
plt.ylim(0.00,1)

ax1.set_xlabel('Evaluations')
ax1.set_ylabel('Fitness: Speed m/s')
ax2.set_ylabel('Fitness: # Body length/Cycle')
ax2.set_ylim(0.06*2.5,0.15*2.5)
plt.title('Speed V.S Number of Individual Evaluated(Error Bar x20)')
ax1.legend()
plt.show()



types = ["RD","HC","EA"]
#types = ["EA","HC","RD","GD"]
for t in types:
    f_name = [x for x in files if x[0:2]==t]
    all_fitness_x = []
    all_fitness_y = []
    for name in f_name:
        (diversity_x,
        diversity_y,
        fitness_x ,
        converge_x,
        fitness_y ,
        converge_y,
        dot_x,
        dot_y )= read_all(name)

        all_fitness_x.append(fitness_x)
        all_fitness_y.append(fitness_y)
    print("all_fitness_x",all_fitness_x)
    all_fitness_x = np.array(all_fitness_x).astype(float)
    all_fitness_y = np.array(all_fitness_y).astype(float)
    avg_x = np.average(all_fitness_x,axis = 0)
    avg_y = np.average(all_fitness_y,axis = 0)
    plt.plot(avg_x,avg_y,label=f_name[0][0:2])
    y_error =  get_error(all_fitness_x,all_fitness_y)
    plt.fill_between(avg_x, avg_y-y_error*20, avg_y+y_error*20,alpha=0.5)
    #plt.errorbar(all_fitness_x[0],all_fitness_y[0],yerr= y_error,alpha=0.3)
plt.xlim(0,10000)
plt.ylim(0.06,0.15)

plt.xlabel('Evaluations')
plt.ylabel('Fitness: Speed m/s')
plt.title('Speed V.S Number of Individual Evaluated(Error Bar x20)')
plt.legend()
plt.show()






# types = ["HC","EA"]
# for t in types:
#     f_name = [x for x in files if x[0:2]==t]
#     all_fitness_x = []
#     all_fitness_y = []
#     for name in f_name:
#         print(name)
#         (diversity_x,
#         diversity_y,
#         fitness_x ,
#         converge_x,
#         fitness_y ,
#         converge_y,
#         dot_x,
#         dot_y )= read_all(name)

#         all_fitness_x.append(converge_x)
#         all_fitness_y.append(converge_y)
#         # print(converge_y)
#         print(converge_x)
#         print(converge_y)
#     print("all_fitness_x",all_fitness_x)
#     all_fitness_x = np.array(all_fitness_x).astype(float)
#     all_fitness_y = np.array(all_fitness_y).astype(float)
#     avg_x = np.average(all_fitness_x,axis = 0)
#     avg_y = np.average(all_fitness_y,axis = 0)
#     plt.plot(avg_x,avg_y,label=f_name[0][0:2])
#     y_error =  get_error(all_fitness_x,all_fitness_y)
#     plt.fill_between(avg_x, avg_y-y_error, avg_y+y_error,alpha=0.5)
#     #plt.errorbar(all_fitness_x[0],all_fitness_y[0],yerr= y_error,alpha=0.3)

# plt.xlabel('Evaluations')
# plt.ylabel('Fraction of population reached optimum')
# plt.title('Performance Of Robot Evolution')
# plt.legend()
# plt.show()


types = ["RD","HC","EA"]
for t in types:
    f_name = [x for x in files if x[0:2]==t]
    all_fitness_x = []
    all_fitness_y = []
    for name in f_name:
        print(name)
        (diversity_x,
        diversity_y,
        fitness_x ,
        converge_x,
        fitness_y ,
        converge_y,
        dot_x,
        dot_y )= read_all(name)
        
        d= {}
        for i in dot_x:
            if i==1 :
                NUM_PER_GEN +=1
            d[i] = 0
        for i in range(len(dot_x)):
            if dot_y[i]>= 0.3:
                d[int(dot_x[i])] +=1/NUM_PER_GEN

        xx = [float(x) for x in d.keys()]
        yy = [float(x) for x in d.values()]
        print("xx",xx)
        print("yy",yy)
        all_fitness_x.append(xx)
        all_fitness_y.append(yy)
        # print(converge_y)


    all_fitness_x = np.array(all_fitness_x).astype(float)
    all_fitness_y = np.array(all_fitness_y).astype(float)
    avg_x = np.average(all_fitness_x,axis = 0)
    avg_y = np.average(all_fitness_y,axis = 0)
    plt.plot(avg_x,avg_y,label=f_name[0][0:2])
    y_error =  get_error(all_fitness_x,all_fitness_y)
    plt.fill_between(avg_x, avg_y-y_error, avg_y+y_error,alpha=0.5)
    #plt.errorbar(all_fitness_x[0],all_fitness_y[0],yerr= y_error,alpha=0.3)

plt.xlim(0,1000)
plt.xlabel('Generation')
plt.ylabel('Fraction of population reached optimum')
plt.title('Convergence plot of  Robot Evolution')
plt.legend()
plt.show()



# plt.plot(d.keys(),d.values())
# plt.xlabel('Evaluations')
# plt.ylabel('Fraction of population reached threshold')
# plt.title('Convergence Plot')
# plt.legend()
# plt.show()
# plt.show()


plt.scatter(dot_x,dot_y,s=10)
plt.xlabel('Generation')
plt.ylabel('Fitness')
plt.title('Dot Plot for EA')
plt.show();

plt.scatter(diversity_x,diversity_y)
plt.xlabel('Generation')
plt.ylabel('Diversity Parameter')
plt.title('Diversity Plot for EA')
plt.show();


# x,y = read_dots('gp.txt')
# plt.scatter(x,y,s=10,label='Genetic Programming Fitting')
# x,y = read_dots('data.txt')
# plt.scatter(x,y,s=10,label='Ground Truth',alpha = 0.3)
# plt.xlabel('x')
# plt.ylabel('y')
# plt.title('GP result v.s ground truth')
# plt.legend()
# plt.show()
# plt.show()

# x,y = read_dots('hc.txt')
# plt.scatter(x,y,s=0.3,label='Hill Climber Fitting')
# x,y = read_dots('data.txt')
# plt.scatter(x,y,s=10,label='Ground Truth',alpha = 0.3)
# plt.xlabel('x')
# plt.ylabel('y')
# plt.title('HC result v.s ground truth')
# plt.legend()
# plt.show()

exit()
