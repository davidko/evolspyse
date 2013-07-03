import math

def deg2rad(d):
    return d/180*math.pi

def rad2deg(r):
    return r*180/math.pi

def sign(x):
    if x < 0: return -1
    elif x > 0: return 1
    else: return 0
