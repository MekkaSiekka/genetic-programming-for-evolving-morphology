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
BREATH = False
EVAL = 0
DRAW  = True
NUM_SYS = 5
MUs = 0.1
MUk = 0.8
DAMP = 1
T = 0
SIDE = 0.1
locs = {(0,0,0),(1,0,0),(-1,0,0)}
def dist(a,b):
    c = a-b
    return np.sqrt(c.x*c.x + c.y*c.y+c.z*c.z)

def force_thread(FS,ms,ss,idx1,idx2,time):
        #print("in mass",ms[0].mass)
        for i in range(idx1,idx2):
            m = ms[i]
            F = vector(0,0,0)
            #sum up spring force
            for s in ss:
                if not (s.idx1 == i or s.idx2 == i) : 
                    continue 
                if BREATH:
                    s.l0 = s.l *( 1+ s.B*sin(s.w*time + s.C)) 
                if (s.idx1 == i): 
                    end_idx = s.idx1
                    start_idx = s.idx2
                else:
                    end_idx = s.idx2
                    start_idx = s.idx1

                pos_end = ms[end_idx].pos
                pos_start = ms[start_idx].pos
                dirc = pos_end-pos_start
                unit_dir =  norm(dirc)        
                delta_l = dirc - s.l0*unit_dir
                #print(delta_l)
                F_spring = -s.k * delta_l 
                F  = F + F_spring
 
            F = F + m.mass * g
            F_exter = vector(0,0,0)
            if m.pos.z <0:
                F_exter = F_exter + vector(0,0,-KC*m.pos.z)
            F = F + F_exter
            if m.pos.z <0 and F_exter.z <0:
                F.x = F.y = 0
                # FH = math.sqrt(F.x*F.x + F.y*F.y)

                # if FH < -F_exter.z*MUs:
                #     F.x = F.y = 0
                # if FH > -F_exter.z*MUs:
                #     F.x = F.x - F.x/abs(F.x)*MUk*F_exter.z
                #     F.y = F.y - F.y/abs(F.y)*MUk*F_exter.z

            #FS.append(F)
            FS[i] = F

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
    def __init__(self):
        self.ss = []
        self.ms = [] 
        self.Fs = []
        self.balls = [] #used for drawing
        self.cylinders= [] #used for drawing
        self.EVAL = 0
        
 
        loc_set = set()
        permitted_spring= set()
        for loc in locs:
            points = (0,1)
            m_in_cube = []
            for x in points:
                for y in points:
                    for z in points: 
                        vec = vector(x,y,z)*SIDE
                        trans = vector(loc[0],loc[1],loc[2])*SIDE
                        vec = vec + trans
                        loc_set.add((vec.x,vec.y,vec.z))
                        print(vec.x,vec.y,vec.z)
                        m_in_cube.append(vec)
            #work on springs
            for l1 in m_in_cube:
                for l2 in m_in_cube:
                    if not (l1.x == l2.x and l1.y == l2.y and l1.z == l2.z):
                        tup1 = (l1.x ,l1.y ,l1.z, l2.x ,l2.y ,l2.z)
                        tup2 = (l2.x ,l2.y ,l2.z, l1.x ,l1.y ,l1.z)
                        if not (tup1 in permitted_spring  and tup2 in permitted_spring):
                            permitted_spring.add((l1.x ,l1.y ,l1.z, l2.x ,l2.y ,l2.z))

        for loc in loc_set:
            m = Mass()
            m.pos = vector(loc[0],loc[1],loc[2])

            self.ms.append(m)
            if DRAW:
                ball = sphere (color = color.green, radius = 0.01, pos = m.pos,remain=1, visible=False)
                self.balls.append(ball)



        def close(num):
            if abs(num-1*SIDE) <=0.00001:
                return True
            if abs(num-math.sqrt(2)*SIDE) <=0.00001:
                return True
            if abs(num-math.sqrt(3)*SIDE) <=0.00001:
                return True
            return False

        for i in range(0,len(self.ms)):
            for j in range(i,len(self.ms)):
                if i==j:
                    continue
                # if not close(dist(self.ms[i].pos,self.ms[j].pos)):
                #     continue
                l1 = self.ms[i].pos
                l2 = self.ms[j].pos
                tup = (l1.x ,l1.y ,l1.z, l2.x ,l2.y ,l2.z)
                if not tup in permitted_spring:
                    continue
                s = Spring()
                s.k = K 
                s.l = dist(self.ms[i].pos,self.ms[j].pos)
                s.idx1 = i
                s.idx2 = j
                self.ss.append(s)
                vec2 = self.ms[i].pos
                vec1 = self.ms[j].pos
                if DRAW:
                    c = cylinder(pos=vec2,  axis=vec1-vec2, radius=0.002,remain = 1,visible=False)
                    self.cylinders.append(c)
    
    def rotate(self,angle, axis):
        for i in range(0,len(self.ms)):
            self.ms[i].pos=rotate(self.ms[i].pos,angle,axis)

    def translate(self, dirc):
        for i in range(0,len(self.ms)):
            self.ms[i].pos= self.ms[i].pos + dirc
    
    
    def step(self,time = 0):
        #print(self.ms[0].pos)
        num_m = len(self.ms)
        #print(num_m)
        FS = [None]*num_m
        num_m_per_thread = int(num_m/NUM_TRHEAD)+1
        threads = list()
        for idx in range(NUM_TRHEAD):
            #print (idx*num_m_per_thread,min((idx+1)*num_m_per_thread,num_m))
            x = threading.Thread(target=force_thread, 
                args=(FS,self.ms,
                        self.ss,
                        idx*num_m_per_thread,
                        min((idx+1)*num_m_per_thread,num_m),
                        time,)
                )
            threads.append(x)
            x.start()

        for index, thread in enumerate(threads):
            thread.join()

        

        for i in range(0,len(self.ms)): 
            F = FS[i]
            m = self.ms[i]
            #print(m.pos)
            m.a = F/m.mass
            m.v = m.v + m.a*DT
            m.v = m.v*DAMP
            m.pos = m.pos + m.v*DT
            self.ms[i] = m


    def base_case(self):
        self.ss = []
        self.ms = [] 
        self.Fs = []
        self.balls = [] #used for drawing
        self.cylinders= [] #used for drawing
        
        m = Mass()
        m.pos = vector(0,0,0.1)
        ball = sphere (color = color.green, radius = 0.01, pos = m.pos,remain=1)
        self.balls.append(ball)
        self.ms.append(m)

        m= Mass()
        m.pos = vector(0,0,0.2)
        ball = sphere (color = color.red, radius = 0.01, pos = m.pos,remain=1)
        self.balls.append(ball)
        self.ms.append(m)

        for i in range(0,len(self.ms)):
            for j in range(i,len(self.ms)):
                if i==j:
                    continue
                s = Spring()
                s.k = K 
                s.l0 = dist(self.ms[i].pos,self.ms[j].pos)
                s.idx1 = i
                s.idx2 = j
                self.ss.append(s)
                vec2 = self.ms[i].pos
                vec1 = self.ms[j].pos

                c = cylinder(pos=vec2,  axis=vec1-vec2, radius=0.005,remain = 1)
                self.cylinders.append(c)
        print("num of springs",len(self.ss))


    def simulate(self):
        T = 2
        t = 0
        while t<T:
            self.step(t)
        

    def draw(self):
        ms,ss = self.ms, self.ss
        for i in range(0,len(self.balls)):
            self.balls[i].pos = ms[i].pos
            self.balls[i].visible = True
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
    
    def energy(self):
        Egrav = 0.0
        Espring =0.0
        Ekina = 0.0
        #gravite
        for i in range(0,len(self.ms)):
            Egrav = Egrav + (-self.ms[i].mass* g.z * self.ms[i].pos.z)
            Ekina = Ekina + 0.5*self.ms[i].mass*mag(self.ms[i].v)*mag(self.ms[i].v)
        #spring
        for s in self.ss:
            vec1 = self.ms[s.idx1].pos
            vec2 = self.ms[s.idx2].pos
            l = mag(vec1-vec2)
            delta_l = l - s.l0 
            Espring = Espring + 0.5*s.k*delta_l*delta_l

        return Egrav,Espring,Ekina
        #kinatic    

def thread_func(s):
    lock = threading.Lock()
    while True:
    #for i in range(0,5):
    #rate(FPS)
        for tt in range(0,5):
            s.step()
                #print(s.ms[0].a)

        if DRAW:
            lock.acquire()
            try:
                s.draw()
            finally:
                lock.release()

def multi_thread_run(SL):
    for s in SL :
        t = threading.Thread(target = thread_func, args=(s,))    
        t.start()

def single_run(SL):
    t = 0.0
    while True:
    #for i in range(0,5):
    #rate(FPS)
        for tt in range(0,5):
            for s in SL:
                s.step(t)
                t += DT

        if DRAW:
            for s in SL:
                s.draw()
        


#energy_plot(2000)
print("kk")
SL = []
print("start")
for i in range(0,NUM_SYS):
    s = System()
    #.base_case()
    dirc = np.random.rand(3,1) -0.5
    dirc = vector(dirc[0],dirc[1],dirc[2])
    dirc.z = 0.01
    #dirc = vector(0,0,0.001)
    angle = np.random.rand((1))[0] * 3.14
    s.translate(dirc)
    #s.rotate(angle,dirc)
    #s.rotate(angle,vector(0,1,1))
    #s.translate(dirc)
    #s.translate(vector(0,0,-0.2))
    vv = 1
    #add spin
    # s.ms[1].v = vector(0,vv,0)
    # s.ms[5].v = vector(0,vv,0)
    # s.ms[0].v = vector(0,0,vv)
    # s.ms[4].v = vector(0,0,vv)
    # s.ms[2].v = vector(0,-vv,0)
    # s.ms[6].v = vector(0,-vv,0)
    # s.ms[3].v = vector(0,0,-vv)
    # s.ms[7].v = vector(0,0,-vv)
    SL.append(s)

if DRAW:
    draw_world()

#multi_thread_run(SL)
single_run(SL)

exit()

frame = 0
print(len(SL))
#exit()




