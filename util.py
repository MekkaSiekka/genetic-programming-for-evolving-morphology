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

def energy_plot(cycle):
    T = []
    E_G = []
    E_S = []
    E_K = []
    E_P = []
    E = []
    cur_time = 0
    draw_world()
    s = System()
    start = time.time()
    for t in range(0,cycle):
        #rate(FPS)
        for tt in range(0,10):
            s.step(cur_time)
            cur_time = cur_time + DT
            #print(s.ms[0].a)
        Egrav,Espring,Ekina = s.energy()
        #print(s.ms[0].v)
        #print(Egrav+Espring+Ekina)
        s.draw()
        T.append(DT*100*t)
        E_G.append(Egrav)
        E_S.append(Espring)
        E_K.append(Ekina)
        E_P.append(Egrav + Espring)
        E.append(Egrav + Espring + Ekina)
    print("speed", s.EVAL/(time.time()-start))
    #print(T)
    #print(E_G)
    #print(len(T),len(E_G))
    plt.scatter(T,E_G,s=0.3,label = "Gravitational Potential Energy")
    plt.scatter(T,E_S,s=0.3,label = "Spring Potential Energy")
    plt.scatter(T,E_P,s=0.3,label = "Total Potential Energy")
    plt.scatter(T,E_K,s=0.3,label = "Kinatic Energy")
    plt.scatter(T,E,s=0.3, label = "Total Energy")
    plt.xlabel('Time (s)')
    plt.ylabel('Energy, (J)')
    plt.title('Energy Plot of System')
    plt.legend()
    plt.show()

def draw_world():
    side = 5
    thk = 0.001
    scene.width = 1920
    scene.height = 1080
    # wallR = box (pos=vector( side, 0, 0), size=vector(thk, s2, s3),  color = color.red)
    # wallL = box (pos=vector(-side, 0, 0), size=vector(thk, s2, s3),  color = color.red)
    #wallB = box (pos=vector(0, 0, 0), size=vector(side, side, thk),  texture={'file':textures.stones, 'bumpmap':bumpmaps.stones} )
    wallB = box (pos=vector(0, 0, 0), size=vector(side, side, thk),  texture='https://i.imgur.com/riHzBb8.gif' )
    # wallT = box (pos=vector(0,  side, 0), size=vector(s3, thk, s3),  color = color.blue)
    # wallBK = box(pos=vector(0, 0, -side), size=vector(s2, s2, thk), color = color.gray(0.7))


# for i in range(0,len(self.ms)):
        #     m = self.ms[i]
        #     F = vector(0,0,0)
        #     #sum up spring force
        #     for s in self.ss:
        #         self.EVAL = self.EVAL + 1;
        #         if not (s.idx1 == i or s.idx2 == i) : 
        #             continue 
        #         if BREATH:
        #             print('bb')
        #             s.l0 = s.l *( 1+ s.B*sin(s.w*time + s.C)) 
        #         if (s.idx1 == i): 
        #             end_idx = s.idx1
        #             start_idx = s.idx2
        #         else:
        #             end_idx = s.idx2
        #             start_idx = s.idx1

        #         pos_end = self.ms[end_idx].pos
        #         pos_start = self.ms[start_idx].pos
        #         dirc = pos_end-pos_start
        #         unit_dir =  norm(dirc)        
        #         delta_l = dirc - s.l0*unit_dir
        #         #print(delta_l)
        #         F_spring = -s.k * delta_l 
        #         F  = F + F_spring
 
        #     F = F + m.mass * g
        #     F_exter = vector(0,0,0)
        #     if m.pos.z <0:
        #         F_exter = F_exter + vector(0,0,-KC*m.pos.z)
        #     F = F + F_exter
        #     if m.pos.z <0 and F_exter.z <0:
        #         F.x = F.y = 0

        #     FS[i] = F


# points = (0.0,0.1)
        # tmp = 0
        # for x in points:
        #     for y in points:
        #         for z in points: 
        #             m = Mass()
        #             m.pos = vector(x,y,z)
        #             self.ms.append(m)
        #             if DRAW:
        #                 ball = sphere (color = color.green, radius = 0.01, pos = m.pos,remain=1, visible=False)
        #                 self.balls.append(ball)
        #             tmp = tmp +1 

        # for i in range(0,len(self.ms)):
        #     for j in range(i,len(self.ms)):
        #         if i==j:
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
        #  self.translate(vector(-0.05,-0.05,0.2))
        #locs = {(0,0,0),(0,1,0),(0,-1,0),(0,2,0),(0,-2,0),(1,0,0),(0,0,1)}