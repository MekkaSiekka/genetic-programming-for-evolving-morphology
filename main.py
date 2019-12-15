import logging
import threading
import time
import numpy as np  
from vpython import *
import sys 
import time
import copy
import threading
import multiprocessing

import matplotlib.pyplot as plt
import random
import math
from util import *

NUM_TRHEAD = 8
M = 0.1
K = 5000;
KC = 100000;
g = vector(0,0,-9.81)
DT = 0.0005
FPS = 20
TIME = 5
OMEGA = 10
BREATH = True
EVAL = 0
DRAW  = True
NUM_SYS = 5
MUs = 0.1
MUk = 0.8
DAMP = 0.9999
T = 0
SIDE = 0.1



def dist(a,b):
    c = a-b
    return np.sqrt(c.x*c.x + c.y*c.y+c.z*c.z)

class Mass(object):
    def __init__(self):
        self.mass = M
        self.pos = vector(0,0,0)
        self.v = vector(0,0,0)
        self.a = vector(0,0,0)


class Spring(object):
    def __init__(self):
        self.k = 1
        self.l = 0.1
        self.l0 = self.l
        self.idx1 = 1
        self.idx2 = 1
        self.A = 0.1
        self.B = 0.1
        self.w = OMEGA
        self.C = 0

class System(object):
    def __init__(self,dir_name):
        self.ss = []
        self.ms = [] 
        self.Fs = []
        self.balls = [] #used for drawing
        self.cylinders= [] #used for drawing
        self.EVAL = 0
        self.frame = 0
        self.triangles = []
        self.triangle_idxs = []
        # loc_set = set()
        # permitted_spring= set()
        # for loc in locs:
        #     points = (0,1)
        #     m_in_cube = []
        #     for x in points:
        #         for y in points:
        #             for z in points: 
        #                 vec = vector(x,y,z)*SIDE
        #                 trans = vector(loc[0],loc[1],loc[2])*SIDE
        #                 vec = vec + trans
        #                 loc_set.add((vec.x,vec.y,vec.z))
        #                 print(vec.x,vec.y,vec.z)
        #                 m_in_cube.append(vec)
        #     #work on springs
        #     for l1 in m_in_cube:
        #         for l2 in m_in_cube:
        #             if not (l1.x == l2.x and l1.y == l2.y and l1.z == l2.z):
        #                 tup1 = (l1.x ,l1.y ,l1.z, l2.x ,l2.y ,l2.z)
        #                 tup2 = (l2.x ,l2.y ,l2.z, l1.x ,l1.y ,l1.z)
        #                 if not (tup1 in permitted_spring  and tup2 in permitted_spring):
        #                     permitted_spring.add((l1.x ,l1.y ,l1.z, l2.x ,l2.y ,l2.z))

        # for loc in loc_set:
        #     m = Mass()
        #     m.pos = vector(loc[0],loc[1],loc[2])

        #     self.ms.append(m)
        #     if DRAW:
        #         ball = sphere (color = color.green, radius = 0.01, pos = m.pos,remain=1, visible=False)
        #         self.balls.append(ball)

        # for i in range(0,len(self.ms)):
        #     for j in range(i,len(self.ms)):
        #         if i==j:
        #             continue
        #         # if not close(dist(self.ms[i].pos,self.ms[j].pos)):
        #         #     continue
        #         l1 = self.ms[i].pos
        #         l2 = self.ms[j].pos
        #         tup = (l1.x ,l1.y ,l1.z, l2.x ,l2.y ,l2.z)
        #         if not tup in permitted_spring:
        #             continue
        #         s = Spring()
        #         s.k = K 
        #         s.l = dist(self.ms[i].pos,self.ms[j].pos)
        #         s.idx1 = i
        #         s.idx2 = j
        #         self.ss.append(s)
        #         vec2 = self.ms[i].pos
        #         vec1 = self.ms[j].pos
        #         if DRAW:
        #             c = cylinder(pos=vec2,  axis=vec1-vec2, radius=0.002,remain = 1,visible=False)
        #             self.cylinders.append(c)

        file_name = dir_name+"/"+"model.txt"
        with open(file_name) as f:
            content = f.readlines()
            content = [x.strip().split() for x in content] 

        pos = 0
        num_m =  int(content[0][0])
        num_s =  int(content[1][0])
        num_rect = int(content[2][0])
        print(num_rect)
        pos +=3
        for i in range(0,num_m):
            c = [float(x) for x in content[pos] ]
            loc = vector(c[0],c[1],c[2])
            pos = pos+1
            m = Mass()
            m.pos = loc
            self.ms.append(m)
            if DRAW:
                ball = sphere (color = color.green, radius = 0.01, pos = m.pos,remain=1, visible=False)
                self.balls.append(ball)
        for i in range(0,num_s):
            idxs = [int(x) for x in content[pos] ]
            pos = pos+1

            s = Spring()
            s.l = dist(self.ms[idxs[0]].pos,self.ms[idxs[1]].pos)
            s.idx1 = idxs[0]
            s.idx2 = idxs[1]
            self.ss.append(s)
            vec2 = self.ms[idxs[0]].pos
            vec1 = self.ms[idxs[0]].pos
            if DRAW:
                c = cylinder(pos=vec2,  axis=vec1-vec2, radius=0.002,remain = 1,visible=False)
                self.cylinders.append(c)
        for i in range(0,num_rect):
            idxs = [int(x) for x in content[pos]]
            pos = pos+1
            a = vertex( pos=self.ms[idxs[0]].pos,color= vec(0,102/255,204/255))
            b = vertex( pos=self.ms[idxs[1]].pos,color= vec(0,128/255,1))
            c = vertex( pos=self.ms[idxs[2]].pos,color= vec(153/255,1,1))
            # random.seed(0)
            # a = vertex( pos=self.ms[idxs[0]].pos,color= vec(random.uniform(0, 1),102/255,204/255))
            # b = vertex( pos=self.ms[idxs[1]].pos,color= vec(0,random.uniform(0, 1),1))
            # c = vertex( pos=self.ms[idxs[2]].pos,color= vec(153/255,1,random.uniform(0, 1)))
            T = triangle( v0=a, v1=b, v2=c )
            self.triangle_idxs.append(idxs)
            self.triangles.append(T)
        print(content[pos-1])
        # --------------------------reading frame by frame ------------------------------------- 
        self.status = []
        file_name = dir_name+"/"+"status.txt"
        with open(file_name) as f:
            content = f.readlines()
            content = [x.strip().split() for x in content] 
        
        pos = 0
        for i in range(0,int(len(content)/num_m)):
            step = []
            for  j in range(num_m):
                c = [float(x) for x in content[pos] ]
                loc = vector(c[0],c[1],c[2])
                step.append(loc)
                pos+=1
            #print(step)
            self.status.append(step)

        # print("read")
        # for i in range(num_m*num_m*num_m):
        #     print(i)
        #     a = vertex( pos=vec(0,0,0), color= vec(1,0,0))
        #     b = vertex( pos=vec(0,0,0),color= vec(0,1,0) )
        #     c = vertex( pos=vec(0,0,0),color= vec(0,0,1) )
        #     T = triangle( v0=a, v1=b, v2=c )
        #     self.triangles.append(T)





        # def rotate(self,angle, axis):
        #     for i in range(0,len(self.ms)):
        #         self.ms[i].pos=rotate(self.ms[i].pos,angle,axis)

        # def translate(self, dirc):
        #     for i in range(0,len(self.ms)):
        #         self.ms[i].pos= self.ms[i].pos + dirc
    
    
    def step(self,time = 0):
        return 


    def draw(self):
        ms,ss = self.ms, self.ss
        for i in range(0,len(self.balls)):
            self.balls[i].pos = ms[i].pos
            self.balls[i].visible = False
        for i in range(0,len(self.cylinders)):
            s = ss[i]
            vec1 = ms[s.idx1].pos
            vec2 = ms[s.idx2].pos
            #rod = cylinder(pos=vec2,  axis=vec1-vec2, radius=0.005,remain = 1)
            self.cylinders[i].pos = vec2
            self.cylinders[i].axis = vec1-vec2
            self.cylinders[i].visible = True
            strain = abs(mag(vec1-vec2)-s.l0)/s.l0
            #print(strain)
            #self.cylinders[i].color = vector(min((mag(vec1-vec2)-s.l0)/s.l0,1) , 1, 1)
    

    def draw_frame(self):
        scene.width = 1920
        scene.height = 1080
        step = self.status[self.frame]
        ms,ss = self.ms, self.ss
        for i in range(0,len(self.balls)):
            self.balls[i].pos = ms[i].pos = self.status[self.frame][i]
            self.balls[i].visible = False


        for i in range(0,len(self.cylinders)):
            s = ss[i]
            vec1 = ms[s.idx1].pos
            vec2 = ms[s.idx2].pos
            #rod = cylinder(pos=vec2,  axis=vec1-vec2, radius=0.005,remain = 1)
            self.cylinders[i].pos = vec2
            self.cylinders[i].axis = vec1-vec2
            self.cylinders[i].visible = False
            strain = abs(mag(vec1-vec2)-s.l0)/s.l0
        
        for i in range(0,len(self.triangles)):
            idxs= self.triangle_idxs[i]
            self.triangles[i].v0.pos = ms[idxs[0]].pos
            self.triangles[i].v1.pos = ms[idxs[1]].pos
            self.triangles[i].v2.pos = ms[idxs[2]].pos
        #print("drawing")
        idx = 0
        num_m = len(ms)
        # for i in range(num_m):
        #     for j in range(num_m):
        #         for k in range(num_m):
        #             print(i,j,k)
        #             self.triangles[idx].v0.pos = ms[i].pos
        #             self.triangles[idx].v1.pos = ms[j].pos
        #             self.triangles[idx].v2.pos = ms[k].pos
        #             self.triangles[idx].visible = True;
        #             idx = idx +1

        self.frame += 1

if __name__ == "__main__":
    if DRAW:
        a=1
        draw_world()
    s = System("./")
    # a = vertex( pos=vec(0,0,0) , color= vec(1,0,0))
    # b = vertex( pos=vec(0,0,0),color= vec(0,1,0) )
    # c = vertex( pos=vec(0,0,0),color= vec(0,0,1) )
    # T = triangle( v0=a, v1=b, v2=c )
    # T.visible = False
    #s.draw()
    #exit()
    i = 0
    scene.width = 1920
    scene.height = 1080
    while True:
        s.draw_frame()
        # s2.draw_frame()
        # s3.draw_frame()
