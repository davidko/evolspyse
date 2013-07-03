"""Spyse semant environment module"""

import time
import threading
import math
import copy
from datetime import datetime
from sets import Set
import spyse.util.vector
import os

class Model(object):
    """Environment model for context-awareness"""
    
    def __init__(self):
        self.__items = {}
        self.__lock=threading.Lock()
        self.__observers = []
        
    def write(self, key, value):
        self.__lock.acquire()
        value['timestamp'] = time.time()
        self.__items[key] = value
        for o in self.__observers:
            o.notify(key, value)
        self.__lock.release()

    def read(self, key):
        self.__lock.acquire()
        val = self.__items.get(key, None)
        val_copy = copy.deepcopy(val)
        self.__lock.release()
        return val_copy

    def take(self, key):
        self.__lock.acquire()
        val = self.__items.get(key, None)
        val_copy = copy.deepcopy(val)
        if val is not None:
            del self.__items[key]
        self.__lock.release()
        return val_copy

    def keys(self):
        return self.__items.keys()

    def values(self):
        return self.__items.values()

    def items(self):
        return self.__items.items()

    def register_observer(self, observer):
        self.__observers.append(observer)

    def unregister_observer(self, observer):
        try:
            self.__observers.remove(observer)
        except:
            pass


class Controller(object):
    def __init__(self, model):
        self._model = model
        self.start_time=time.time()
        self.setup()
        
    def setup(self):
        pass

    # return a list of all key,value pairs of which value[label]==labelvalue
    def find_items(self,label,labelvalue):
        return [(key, val) for (key, val) in self._model.items() if val[label]==labelvalue]
    
    def time(self):
        return time.time()-self.start_time
    
    def write(self, key, item):
        self._model.write(key, item)
            
    def read(self, key):
        return self._model.read(key)
            
    def take(self, key):
        return self._model.take(key)

    def entities(self):
        return self._model.keys()

    def register_observer(self, observer):
        self._model.register_observer(observer)

    def unregister_observer(self, observer):
        try:
            self._model.unregister_observer(observer)
        except:
            pass


class Controller2D(Controller):
    """Controller for 2-dimensional models and items."""

    def place(self, key, **kwargs):
        self.write(key, kwargs)

    def drop(self, key):
        self.take(key)

    def move(self, key, location):
        """Move entity to an absolute position."""
        e = self.read(key)
        if e is None:
            return
        else:
            e['location'] = location
            self.write(key, e)

    def turn(self, key, a):
        """turn by a degrees in plane: y is south, x is east, alpha = 0 south, clock-wise"""

        e = self.read(key)
        e['rotation'] = e['rotation'] + a # clockwise
        self.write(key, e)
        
    def forward(self, key):
        #print 'forward'
        e = self.read(key)
        e.spot = e.spot + e.velo
#        dx = d * cos(e.h/180.0*pi)
#        dy = d * sin(e.h/180.0*pi)
#        e.x = e.x + dx
#        e.y = e.y + dy
        self.write(key, e)

    def backward(self, key, d):
        e = self.read(key)
        e.spot = e.spot + e.velo
#        dx = d * cos(e.h/180.0*pi)
#        dy = d * sin(e.h/180.0*pi)
#        e.x = e.x - dx
#        e.y = e.y - dy
        self.write(key, e)

    def left(self, key, a):
        self.turn(key, -a)

#        e = self.read(key)
#        e.h = (e.h - h) % 360

#        dx = d * cos(e.h/180.0*pi)
#        dy = d * sin(e.h/180.0*pi)
#        e.x = e.x - dx
#        e.y = e.y + dy
        self.write(key, e)

    def right(self, key):
        e = self.read(key)
        if e.velo.y != 0:
            alpha = sin(e.velo.x/e.velo.y)
        else:
            alpha = 0
        alpha = (alpha + 90) % 360
        e.velo.x = e.v * sin(alpha)
        e.velo.y = e.v * cos(alpha)
        self.write(key, e)

#        e = self.read(key)
#        e.h = (e.h + h) % 360

#        dx = d * cos(e.h/180.0*pi)
#        dy = d * sin(e.h/180.0*pi)
#        e.x = e.x + dx
#        e.y = e.y - dy
        self.write(key, e)

    def up(self, key, d):
        pass

    def down(self, key, d):
        pass

    def north(self, key, d):
        e = self.read(key)
        e.y = e.y + d
        self.write(key, e)

    def east(self, key, d):
        e = self.read(key)
        e.x = e.x + d
        self.write(key, e)

    def south(self, key, d):
        e = self.read(key)
        e.y = e.y - d
        self.write(key, e)

    def west(self, key, d):
        e = self.read(key)
        e.x = e.x - d
        self.write(key, e)

    def speed(self, key, v):
        e = self.read(key)
        e.v = v
        self.write(key, e)

    def faster(self, key, dv):
        e = self.read(key)
        e.v = e.v + dv
        self.write(key, e)

    def slower(self, key, dv):
        e = self.read(key)
        e.v = max(e.v - dv, 0)
        self.write(key, e)

    def stop(self, key):
        e = self.read(key)
        e.v = 0
        self.write(key, e)

##    def neighbours(self, key, type=None):
##        # Who is within distance d from agent key?
##
##        candidates = {}
###        for k, i in self.indices.iteritems():
###            print k, i.key
##        e = self.read(key)
##        i_x = self.indices['x']
##        i_y = self.indices['y']
##        i_t = self.indices['type']
##        x_min = i_x.classify(e.x - e.d)
##        x_max = i_x.classify(e.x + e.d)
##        y_min = i_y.classify(e.y - e.d)
##        y_max = i_y.classify(e.y + e.d)
##
##        x_set = Set()
##        x_classes = i_x.classes()
##        for xc in x_classes:
##            if xc in range(x_min, x_max+1):
##                for v in i_x.values[xc]:
##                    x_set.add(v)
##
##        y_set = Set()
##        y_classes = i_y.classes()
##        for yc in y_classes:
##            if yc in range(y_min, y_max+1):
##                for v in i_y.values[yc]:
##                    y_set.add(v)
##
##        if type is None:
##            t_set = i_t.values()
##        else:
##            t_set = i_t.values[type]
##
##        set = x_set & y_set & t_set
##        #print set
##        set.remove(key)
##
##        # check distance for all candidates
##        # remove candidates too far off
##        false_candidates = Set()
##        for candidate in set:
##            c = self.read(candidate)
##            #print c.key
##            dx = e.x-c.x
##            dy = e.y-c.y
##            dist = sqrt(dx*dx + dy*dy)
##            #print dist
##            if dist > e.d:
##                false_candidates.add(candidate)
##
##        return list(set - false_candidates)

    def __inside(self, circle, item, label):
        try:
            if item['label'] is not label:
                return False
            else:
                x, y, d = circle
                xi, yi = item['location']
                dx = xi-x
                dy = yi-y
                return (dx*dx + dy*dy < d*d)
        except:
            return False
    
    def neighbours(self, key, label=None):
        # Who is within distance d from agent key?
        
        try:
            d = 50    #TODO: use view distance of item
            item = self._model.read(key)
            x, y = item['location']
            circle = (x, y, d)
            values = self._model.values()
            
            # remove value of own key
            i = values.index(item)
            del values[i]
        except:
            return []
        
        return [i for i in values if self.__inside(circle, i, label)]
        
    def inview(self, key, type=None):
        # neighbours in heading direction

        #print datetime.today(), key, 'inview', type
        candidates = {}
#        for k, i in self.indices.iteritems():
#            print k, i.key
        e = self.read(key)
        i_x = self.indices['x']
        i_y = self.indices['y']
        i_t = self.indices['type']

        view_left = copy.deepcopy(e.face)
        view_left.r = e.d
        view_left.phi = view_left.phi + e.a/360.0*math.pi
        view_middle = copy.deepcopy(e.face)
        view_middle.r = e.d
        view_right = copy.deepcopy(e.face)
        view_right.r = e.d
        view_right.phi = view_right.phi - e.a/360.0*math.pi

#        print key
#        print 'spot ', e.spot
#        print 'velo ', e.velo
#        print 'left ', view_left
#        print 'right', view_right

        x_min = i_x.classify(min(e.spot.x, e.spot.x+view_left.x, e.spot.x+view_middle.x, e.spot.x+view_right.x))
        x_max = i_x.classify(max(e.spot.x, e.spot.x+view_left.x, e.spot.x+view_middle.x, e.spot.x+view_right.x))
        y_min = i_y.classify(min(e.spot.y, e.spot.y+view_left.y, e.spot.x+view_middle.y, e.spot.y+view_right.y))
        y_max = i_y.classify(max(e.spot.y, e.spot.y+view_left.y, e.spot.x+view_middle.y, e.spot.y+view_right.y))

#================================================================================
#        if e.a < 90:
#            x_min = i_x.classify(e.x)
#            x_max = i_x.classify(e.x + e.d * cos((90-e.h-e.a/2)/180.0*pi))
#            y_min = i_y.classify(e.y)
#            y_max = i_y.classify(e.y + e.d * cos((e.h-e.a/2)/180.0*pi))
#        elif e.h < 180:
#            x_min = i_x.classify(e.x)
#            x_max = i_x.classify(e.x + e.d)
#            y_min = i_y.classify(e.y)
#            y_max = i_y.classify(e.y + e.d)
#        elif e.h < 270:
#            x_min = i_x.classify(e.x)
#            x_max = i_x.classify(e.x + e.d)
#            y_min = i_y.classify(e.y)
#            y_max = i_y.classify(e.y + e.d)
#        else:
#            x_min = i_x.classify(e.x)
#            x_max = i_x.classify(e.x + e.d)
#            y_min = i_y.classify(e.y)
#            y_max = i_y.classify(e.y + e.d)
#================================================================================

        x_set = Set()
        x_classes = i_x.classes()
        for xc in x_classes:
            if xc in range(x_min, x_max+1):
                for v in i_x.values[xc]:
                    x_set.add(v)

        y_set = Set()
        y_classes = i_y.classes()
        for yc in y_classes:
            if yc in range(y_min, y_max+1):
                for v in i_y.values[yc]:
                    y_set.add(v)

        t_set = Set()
        if type is not None:
            t = i_t.values[type]
        else:
            t = i_t.items()
        for tt in t:
            t_set.add(tt)

        set = x_set & y_set & t_set

#        if key == 'SlowCar':
#            print 'x_min', x_min
#            print 'x_max', x_max
#            print 'y_min', y_min
#            print 'y_max', y_max
#            
#            print 'i_x', i_x.values
#            print 'i_y', i_y.values
#            print 'i_t', i_t.values
#            
#            print 'i_x.values', i_x.values
#            print 'i_y.values', i_y.values
#            print 'i_t.values', i_t.values
#    
#            print 'x_set', x_set
#            print 'y_set', y_set
#            print 't_set', t_set
#            print 'set', set

        set.remove(key)

        # check distance and angle for all candidates
        # remove candidates too far off or out of angle
        false_candidates = Set()
        for candidate in set:
            c = self.read(candidate)
            v = vector.Vector([c.x-e.x, c.y-e.y, c.z-e.z])
            distance = vector.norm(v)
            angle = v.phi
            #angle = math.fabs(v.phi - e.spot.phi)

#            print 'distance', distance
#            print 'e.d', e.d
#            print 'angle', angle
#            print 'e.a', e.a
#            print 'e.a/360*math.pi', e.a/360*math.pi

            if distance > e.d or angle > e.a/360*math.pi:
                #print 'removing', candidate
                false_candidates.add(candidate)

        #print 'set - false_candidates', set - false_candidates

        return list(set - false_candidates)

    def present(self, x, y, d):
        # who is within distance d from (x, y)?
        pass

    def FindObjects(self, type):
        self.objects = {}
        for entity in self.entities():
            e = self.read(entity)
            if e['label'] == type: self.objects[entity] = e
        return self.objects


#@singleton
class Environment(threading.Thread):
    def __init__(self, condition, **kwargs):
        #super(self.__class__, self).__init__()
        super(Environment, self).__init__()
        
        self.condition = condition    # a function that defines how long to run, should return Boolean
        
        for a, v in kwargs.items():
            setattr(self, a, v)
        
        self.updateProcs = []
        self.set_model()
        self.set_controller()
        self.setup()
        
    # override this to set up an environment
    def setup(self):
        pass
        
    # override this to select a model
    def set_model(self):
        self.model = None
        
    # override this to select a controller
    def set_controller(self):
        self.controller = None
        
    def run(self):
        while self.condition():
            for p in self.updateProcs: p()
            time.sleep(0.05)


class Environment2D(Environment):
    def __init__(self, condition, **kwargs):
        super(Environment2D, self).__init__(condition, **kwargs)

    def set_model(self):
        self.model = Model()

    def set_controller(self):
        self.controller = Controller2D(self.model)
