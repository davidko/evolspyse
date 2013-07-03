"""Spyse semant environment module"""

# TODO: remove  all sub-Models
# TODO: only volume and sphere controllers are needed (plane = volume/z=0): volume = [x, y, z], sphere = [rho, theta, d]
# TODO: different entities ??? or controllers ???


import time
import thread
import math
import copy
from datetime import datetime
from sets import Set
import Pyro4.core
import Pyro4.naming

from spyse.core.platform.constants import Dist
from spyse.util import vector

dist=None
daemon=None
pyroloc=None
nameserver=None

class Entity(object):
    # x-coordinate
    def __get_x(self): return self.spot.x
    def __set_x(self, x): self.spot.x = x
    def __del_x(self): print '__del_x NOT SUPPORTED'  #__del_ self.spot.x
    x = property(__get_x, __set_x, __del_x, "x-coordinate")

    # y-coordinate
    def __get_y(self): return self.spot.y
    def __set_y(self, y): self.spot.y = y
    def __del_y(self): print '__del_y NOT SUPPORTED'  #__del_ self.spot.y
    y = property(__get_y, __set_y, __del_y, "y-coordinate")

    # z-coordinate
    def __get_z(self): return self.spot.z
    def __set_z(self, z): self.spot.z = z
    def __del_z(self): print '__del_z NOT SUPPORTED'  #__del_ self.spot.z
    z = property(__get_z, __set_z, __del_z, "z-coordinate")

    # speed
    def __get_v(self): return vector.norm(self.velo)
    def __set_v(self, v):
        #print 'NOT YET IMPLEMENTED' #self.velo = value
        if self.v == 0:
            self.velo = self.face * v
        elif v == 0:
            self.velo = vector.Vector([0.0, 0.0, 0.0])
        else:
            self.velo = self.velo * (v / self.v)
        #print 'speed', self.velo
    def __del_v(self): print '__del_v NOT SUPPORTED'  #__del_ self.velo
    v = property(__get_v, __set_v, __del_v, "speed")

    # heading (2D only), degrees clockwise, 0 at north
#    def __get_h(self): return asin(self.velo.x/self.velo.y)
#    def __set_h(self, value): pass #self.velo = value
#    def __del_h(self): pass #__del_ self.velo
#    h = property(__get_h, __set_h, __del_h, "heading")

    # view depth
    def __get_d(self): return self.view[0]
    def __set_d(self, d): self.view[0] = d
    def __del_d(self): print '__del_d NOT SUPPORTED'  #__del_ self.view[0]
    d = property(__get_d, __set_d, __del_d, "view depth")

    # view angle
    def __get_a(self): return self.view[1]
    def __set_a(self, a): self.view[1] = a
    def __del_a(self): print '__del_a NOT SUPPORTED'  #__del_ self.view[1]
    a = property(__get_a, __set_a, __del_a, "view angle")

    def __init__(self, name, type, spot=[0.0, 0.0, 0.0], form='box', size=[0.0, 0.0, 0.0], velo=[0.0, 0.0, 0.0], face=[1.0, 0.0, 0.0], view=(10.0, 90.0), cond=None):
        self.name = name                      # name
        self.type = type                      # type
        self.time = time.time()               # timestamp
#        self.root = root                      # the modifier (agent), how to get this reliably?
        self.spot = vector.Vector(spot)       # location vector
        #if form is not None:  # reduce size of entity object
        self.form = form                      # type of shape
        self.size = vector.Vector(size)       # area covered by entity (bounding box)
        self.velo = vector.Vector(velo)       # velocity/orientation vector
        self.face = vector.Vector(face)       # orientation that entity faces
        self.view = view                      # visible area: depth, angle
        self.cond = cond                      # condition/state of the entity
        self.id = None                        # id of the distmodel the entity is in


class Index(object):
    def __init__(self, name):
        self.name = name
        self.values = {}

    def classify(self, value):
        return value

    def classes(self):
        return self.values.keys()

    def entities(self):
        entities = []
        for ee in self.values.itervalues():
            for e in ee:
                entities.append(e)
        return entities

    def add(self, name, value):
        class_value = self.classify(value)
        if class_value not in self.values:
            self.values[class_value] = []
        self.values[class_value].append(name)

    def remove(self, name, value):
        class_value = self.classify(value)
        try:
            self.values[class_value].remove(name)
            if self.values[class_value] == []:
                #print 'removing class', class_value
                del self.values[class_value]
        except:
            pass

    def update(self, name, old_value, new_value):
        if old_value is not None:
            self.remove(name, old_value)
        self.add(name, new_value)

##                    if old_value is not None:
##                        i.values[i.classify(old_value)].remove(old_entity.name)
##                    if new_value not in i.values:
##                        i.values[i.classify(new_value)] = []
##                    i.values[i.classify(new_value)].append(entity.name)


class IntegerIndex(Index):
    def __init__(self, name, min, max, res):
        super(IntegerIndex, self).__init__(name)
        self.__slot = int((max - min + 1)/res)
        #print name, 'slot', self.__slot

    def classify(self, value):
        #print 'class of', value, 'is', int(value / self.__slot) * self.__slot-1
        return int(value / self.__slot) * self.__slot-1


class StringIndex(Index):
    def __init__(self, name):
        super(StringIndex, self).__init__(name)
        self.__slot = None

    def classify(self, value):
        return value


class Model(object):

    # TODO: make thread-safe
    # make Model a thread and use Queue (does this work for reading *and* writing?)
#class Model(threading.Thread):

    SERVER_PYRONAME = 'model-server'
    PYRONAME = 'env-model'

    def __init__(self):
        # tuple space, http://c2.com/cgi/wiki?TupleSpace
        # JavaSpaces API used here, http://wwws.sun.com/software/jini/specs/jini1.2html/jsTOC.html
        # maybe use PyLinda? http://www-users.cs.york.ac.uk/~aw/pylinda/

        # stigmergic level
        #self.__cosmos = cosmos

        # semantic level
        self.__entities = {}
        self.__others = []
        
        self.__lock = thread.allocate_lock()
        
        self.write = self.write_basic
        self.read = self.read_basic
        self.read_if = self.read_if_basic
        self.take = self.take_basic
        self.take_if = self.take_if_basic
        self.entities = self.entities_basic

        if dist == Dist.CENTRAL_SERVER:
            daemon.connect(self, Model.SERVER_PYRONAME)
        elif dist == Dist.CENTRAL_CLIENT:
            self.__model_server = Pyro4.core.getProxyForURI('PYRONAME://' + Model.SERVER_PYRONAME)
            self.write = self.write_client
            self.read = self.read_client
            self.read_if = self.read_if_client
            self.take = self.take_client
            self.take_if = self.take_if_client
            self.entities = self.entities_client
        elif dist == Dist.BCAST_UPDATE:
            self.write = self.write_update
            self.take = self.take_update
            self.take_if = self.take_if_update
            daemon.connect(self, pyroloc + '/' + Model.PYRONAME)
            self.__others = self.__find_others()
            self.__lock.acquire()
            if len(self.__others) > 0:
                self.__entities = self.__others[0].get_entities()
                for model in self.__others:
                    model.add_other(self.getProxy())
            self.__lock.release()
 
    def add_other(self, model):
        self.__others.append(model)
        
    def __find_others(self):
        """Find all other viewer instances"""
        others = []
        objs = nameserver.list(":spyse")
        for obj in objs:
            if obj[1] == 1 and obj[0].find('/' + Model.PYRONAME) != -1:
                prox = nameserver.resolve(obj[0]).getProxy()
                if prox.objectID != self.objectGUID:
                    others.append(prox)
        return others               

    # stigmergic level
#    
#    def set_tile(self, x, y, z, name, value):  # Ignore z for now
#        tile = self.cosmos[x][y]
#        tile['t']= time.time()
#        
#        
#    def get_tile(x, y, z):    # ignore z for now
#        return self.cosmos[x][y]

    # semantic level

    def write(self, name, value, localonly=None):
        pass
    
    def write_basic(self, name, value, localonly=None):
        value.t = time.time()
        self.__entities[name] = value
                
    def write_client(self, name, value, localonly=None):
        self.__model_server.write(name, value)
                
    def write_update(self, name, value, localonly=False):
        self.write_basic(name,value)
        if localonly:
            return
        if not self.__lock.acquire(False):
            return
        for model in self.__others:
            model.write(name, value, True)
        self.__lock.release()

    def read(self, name):
        pass
            
    def read_basic(self, name):
        e = self.__entities[name]
        return copy.deepcopy(e)
        
    def read_client(self, name):
        return self.__model_server.read(name)

    def read_if(self, name):
        pass
            
    def read_if_basic(self, name):
        e = self.__entities.get(name, None)
        return copy.deepcopy(e)
    
    def read_if_client(self, name):
        return self.__model_server.read_if(name)

    def take(self, name, localonly=None):
        pass
        
    def take_basic(self, name, localonly=None):
        val = copy.deepcopy(self.__[name])
        e = copy.deepcopy(val)
        del self.__entities[name]
        return e
        
    def take_client(self, name, localonly=None):
        return self.__model_server.take(name)
    
    def take_update(self, name, localonly=False):
        e = self.take_basic(name)
        if localonly:
            return e
        self.__lock.acquire()
        for model in self.__others:
            model.take(name, localonly=True)
        self.__lock.release()
        return e

    def take_if(self, name, localonly=None):
        pass
    
    def take_if_basic(self, name, localonly=None):
        val = self.__entities.get(name, None)
        e = copy.deepcopy(val)
        if val is not None:
            del self.__entities[name]
        print 'dropping',name
        return e
    
    def take_if_client(self, name, localonly=None):
        return self.__model_server.take_if(name)
    
    def take_if_update(self, name, localonly=False):
        e = self.take_if_basic(name)
        if localonly:
            return e
        self.__lock.acquire()
        for model in self.__others:
            model.take_if(name, localonly=True)
        self.__lock.release()
        return e

    def entities(self):
        pass
            
    def entities_basic(self):
        return self.__entities.values()
        
    def entities_client(self):
        return self.__model_server.entities()

#FIXME: remove get_entities() ???
    def get_entities(self):
        return self.__entities


class View():
    def __init__(self, model, controller):
        self.__model = model
        self.controller = controller    

    def entities(self):
        return self.__model.entities()

    def write(self, name, entity):       
        self.controller.write(name, entity)

    def read(self, name):              
        return self.controller.read(name)


class Controller(object):
    def __init__(self, model):
        
        self.__model = model
        self.indices = {}          

        #if dist == Dist.CENTRAL_SERVER:
        #    daemon.connect(self,'controller-server')
        #elif dist == Dist.CENTRAL_CLIENT:
        #    self.__model_server = Pyro4.core.getProxyForURI("PYRONAME://controller-server")

    def add_index(self, index):
        #if dist == Dist.CENTRAL_CLIENT:
        #    copy.copy(self.__model_server).add_index(index)
        #else:
            self.indices[index.name] = index

    def update_all_indices(self):
            pass

    def update_indices(self, entity):
        if dist == Dist.CENTRAL_CLIENT:
            copy.copy(self.__model_server).update_indices(entity)
            return

        old_entity = self.__model.read_if(entity.name)
        for k, i in self.indices.iteritems():
            old_value = getattr(old_entity, k, None)
            new_value = getattr(entity, k, None)
#            print 'old', getattr(old_entity, k, None)
#            print 'new', getattr(entity, k, None)
#            print 'update', entity.name, k, i.values, old_value, new_value
            if (new_value is not None) and (old_value != new_value):
                i.update(entity.name, old_value, new_value)

#    def update_indices(self, entity):
#            old_entity = self.__model.read_if(entity.name)
#            
#            # define classes for each index, assignment of values to classes
#            
#            for k, i in self.indices.iteritems():
#                print 'old', getattr(old_entity, k, None)
#                print 'new', getattr(entity, k, None)
#                old_value = getattr(old_entity, k, None)
#                new_value = getattr(entity, k, None)
#                print 'update', entity.name, k, i, old_value, new_value
#                if (new_value is not None) and (old_value != new_value):
#                    if old_value is not None:
#                        i[old_value].remove(old_entity.name)
#                    if new_value not in i:
#                        i[new_value] = []
#                    i[new_value].append(entity.name)
#            print self.indices
#            # check for current value of all attributes
#            # if new value different remove pointer (name) to current value and add new one

    def write(self, name, entity):
        #self.update_indices(entity)
        self.__model.write(name, entity)
            
    def read(self, name):
        return self.__model.read_if(name)
        
    def set_color(self, name, color):
        e = self.read(name)
        e.color = color
        self.write(name, e)          

class PlaneModel(Model):
    def __init__(self, x_min, x_max, y_min, y_max):
        super(PlaneModel, self).__init__()
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

        #def h(x): return map(v, range(min_y, max_y))
        #cosmos = map(h, range(min_x, max_x))
        # c2 = [[y for y in range(0, 20)] for x in range(0, 20)]

        # def d(x, y): return {'val': x*y}
#        cosmos = [[value(x,y) for y in range(min_y, max_y)] for x in range(min_x, max_x)]


class PlaneView(View):
    pass


class PlaneController(Controller):
    def __init__(self, model):
        super(PlaneController, self).__init__(model)
        self.add_index(IntegerIndex('x', -50, 50, 50))
        self.add_index(IntegerIndex('y', -50, 50, 50))
        self.add_index(StringIndex('type'))    
        
    def place_ent(self, entity):
        self.write(entity.name, entity)

    def place(self, name, type, spot=[0.0, 0.0, 0.0], form='box', size=[0.0, 0.0, 0.0], velo=[0.0, 0.0, 0.0], view=(10.0, 90.0), cond=None):
        e = Entity(name, type, spot=vector.Vector(spot), form=form, size=vector.Vector(size), velo=vector.Vector(velo), view=view, cond=cond)
        e.color='red'
        print 'place', e.name, e.type
        self.write(name, e)

    def drop(self, name):
        self._Controller__model.take_if(name)
        print "Agent", name, "removed."

    def move(self, name, x=None, y=None, z=None):
        e = self.read(name)
        if e is None: return
        if x is not None:
            e.x = x
            #setattr(e, 'x', x)
        if y is not None:
            e.y = y
        if z is not None:
            e.z = z
        self.write(name, e)

    def turn(self, name, a):
        """turn by a degrees in plane: y is north, x is east, aplha = 0 north, clock-wise"""
        e = self.read(name)

#        alpha = math.sin(e.velo.x/e.velo.y)
#        alpha = (alpha + a) % 360
#        e.velo.x = e.v * math.sin(alpha)
#        e.velo.y = e.v * math.cos(alpha)
#        e.h = (e.h + h) % 360

        alpha = (a % 360)/180*math.pi
#        print 'alpha', alpha
#        print 'face.phi, velo.phi', e.face.phi, e.velo.phi
#        print 'face.theta, velo.theta', e.face.theta, e.velo.theta
        e.face.phi = e.face.phi + alpha
        e.velo.phi = e.velo.phi + alpha
#        print 'face, velo', e.face, e.velo
#        print 'face.phi, velo.phi', e.face.phi, e.velo.phi
#        print 'face.theta, velo.theta', e.face.theta, e.velo.theta

        self.write(name, e)

    def forward(self, name):
        #print 'forward'
        e = self.read(name)
        e.spot = e.spot + e.velo
#        dx = d * cos(e.h/180.0*pi)
#        dy = d * sin(e.h/180.0*pi)
#        e.x = e.x + dx
#        e.y = e.y + dy
        self.write(name, e)

    def backward(self, name, d):
        e = self.read(name)
        e.spot = e.spot + e.velo
#        dx = d * cos(e.h/180.0*pi)
#        dy = d * sin(e.h/180.0*pi)
#        e.x = e.x - dx
#        e.y = e.y - dy
        self.write(name, e)

    def left(self, name, a):
        self.turn(name, -a)

#        e = self.read(name)
#        e.h = (e.h - h) % 360

#        dx = d * cos(e.h/180.0*pi)
#        dy = d * sin(e.h/180.0*pi)
#        e.x = e.x - dx
#        e.y = e.y + dy
        self.write(name, e)

    def right(self, name):
        e = self.read(name)
        if e.velo.y != 0:
            alpha = sin(e.velo.x/e.velo.y)
        else:
            alpha = 0
        alpha = (alpha + 90) % 360
        e.velo.x = e.v * sin(alpha)
        e.velo.y = e.v * cos(alpha)
        self.write(name, e)

#        e = self.read(name)
#        e.h = (e.h + h) % 360

#        dx = d * cos(e.h/180.0*pi)
#        dy = d * sin(e.h/180.0*pi)
#        e.x = e.x + dx
#        e.y = e.y - dy
        self.write(name, e)

    def up(self, name, d):
        pass

    def down(self, name, d):
        pass

    def north(self, name, d):
        e = self.read(name)
        e.y = e.y + d
        self.write(name, e)

    def east(self, name, d):
        e = self.read(name)
        e.x = e.x + d
        self.write(name, e)

    def south(self, name, d):
        e = self.read(name)
        e.y = e.y - d
        self.write(name, e)

    def west(self, name, d):
        e = self.read(name)
        e.x = e.x - d
        self.write(name, e)

    def speed(self, name, v):
        e = self.read(name)
        e.v = v
        self.write(name, e)

    def faster(self, name, dv):
        e = self.read(name)
        e.v = e.v + dv
        self.write(name, e)

    def slower(self, name, dv):
        e = self.read(name)
        e.v = max(e.v - dv, 0)
        self.write(name, e)

    def stop(self, name):
        e = self.read(name)
        e.v = 0
        self.write(name, e)

    def neighbours(self, name, type=None):
        # Who is within distance d from agent name?

        candidates = {}
#        for k, i in self.indices.iteritems():
#            print k, i.name
        e = self.read(name)
        i_x = self.indices['x']
        i_y = self.indices['y']
        i_t = self.indices['type']
        x_min = i_x.classify(e.x - e.d)
        x_max = i_x.classify(e.x + e.d)
        y_min = i_y.classify(e.y - e.d)
        y_max = i_y.classify(e.y + e.d)

        x_set = Set()
        x_classes = i_x.classes()
        for xc in x_classes:
            if xc in range(x_min, x_max + 1):
                for v in i_x.values[xc]:
                    x_set.add(v)

        y_set = Set()
        y_classes = i_y.classes()
        for yc in y_classes:
            if yc in range(y_min, y_max + 1):
                for v in i_y.values[yc]:
                    y_set.add(v)

        if type is None:
            t_set = i_t.values()
        else:
            t_set = i_t.values[type]

        set = x_set & y_set & t_set
        #print set
        set.remove(name)

        # check distance for all candidates
        # remove candidates too far off
        false_candidates = Set()
        for candidate in set:
            c = self.read(candidate)
            #print c.name
            dx = e.x-c.x
            dy = e.y-c.y
            dist = sqrt(dx*dx + dy*dy)
            #print dist
            if dist > e.d:
                false_candidates.add(candidate)

        return list(set - false_candidates)


##    def neighbours(self, name, d):
##        # who is within distance d from agent name?
##        # only look in one direction?
##
##        items = self.__model.items()
##        me = self.read(name)
##        n = []
##        #print items
##        for key, item in items:
##            if key != name:
##                dx = item.x-me.x
##                dy = item.y-me.y
##                dist = sqrt(dx*dx + dy*dy)
##                print key, dist
##                if dist <= d:
##                    n.append(key)
##                return n

    def inview(self, name, type=None):
        # neighbours in heading direction

        #print datetime.today(), name, 'inview', type
        candidates = {}
#        for k, i in self.indices.iteritems():
#            print k, i.name
        e = self.read(name)
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

#        print name
#        print 'spot ', e.spot
#        print 'velo ', e.velo
#        print 'left ', view_left
#        print 'right', view_right

        x_min = i_x.classify(min(e.spot.x, e.spot.x + view_left.x, e.spot.x + view_middle.x, e.spot.x + view_right.x))
        x_max = i_x.classify(max(e.spot.x, e.spot.x + view_left.x, e.spot.x + view_middle.x, e.spot.x + view_right.x))
        y_min = i_y.classify(min(e.spot.y, e.spot.y + view_left.y, e.spot.x + view_middle.y, e.spot.y + view_right.y))
        y_max = i_y.classify(max(e.spot.y, e.spot.y + view_left.y, e.spot.x + view_middle.y, e.spot.y + view_right.y))

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
            if xc in range(x_min, x_max + 1):
                for v in i_x.values[xc]:
                    x_set.add(v)

        y_set = Set()
        y_classes = i_y.classes()
        for yc in y_classes:
            if yc in range(y_min, y_max + 1):
                for v in i_y.values[yc]:
                    y_set.add(v)

        t_set = Set()
        if type is not None:
            t = i_t.values[type]
        else:
            t = i_t.entities()
        for tt in t:
            t_set.add(tt)

        set = x_set & y_set & t_set

#        if name == 'SlowCar':
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

        set.remove(name)

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


#from spyse.core.behaviours import Behaviour
#class EnvironmentReceiverBehaviour(Behaviour):
#    pass

class DistView(View):
    def in_model(self, spot):
        return self._View__model.in_model(spot)

class DistController(PlaneController):
    def in_model(self, spot):
        return self._Controller__model.in_model(spot)
    
    def place(self, name, type, spot=[0.0, 0.0, 0.0], form='box', size=[0.0, 0.0, 0.0], velo=[0.0, 0.0, 0.0], view=(10.0, 90.0), cond=None):
        e = Entity(name, type, spot=vector.Vector(spot), form=form, size=vector.Vector(size), velo=vector.Vector(velo), view=view, cond=cond)
        e.color='red'
        e.hid = self._Controller__model.id # set HomeID
        e.cid = self._Controller__model.id # set CurrentID
        print 'place', e.name, e.type
        self.write(name, e)
        
class DistModel(Model):
    #id = None
    
    def __init__(self, x_min, x_max, y_min, y_max):
        super(DistModel, self).__init__()
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.bounds = (self.x_min,self.x_max,self.y_min,self.y_max)
        self.__others = {}
        self.__lock = thread.allocate_lock()
        self.id = 'model-' + str(hash(self)) + str(time.time())
        print 'MODELID',self.id
        
        daemon.connect(self, pyroloc + '/' + Model.PYRONAME)
        others = self._Model__find_others()
        for other in others:
            id = other.get_id()
            self.__others[id] =(other.get_bounds(), other, thread.allocate_lock(), id)
            other.add_other(self.id, self.bounds,self.getProxy())
        
    def get_id(self):
        return self.id
            
    def add_other(self, id, bounds, proxy):
        self.__others[id] = (bounds, proxy, thread.allocate_lock(), id)
    
    def get_bounds(self):
        return self.bounds
    
    def in_model(self, spot):
        if self.in_bounds(spot, self.bounds):
            return True
        else:
            for other in self.__others.values():
                if self.in_bounds(spot,other[0]):
                    return True
        return False
    
    def in_bounds(self, spot, bounds):
        if spot.x >= bounds[0] and spot.x <= bounds[1] and \
            spot.y >= bounds[2] and spot.y <= bounds[3]:
            return True
        else:
            return False

    def write_basic(self, name, value):
        if value.cid == self.id:
            # Entity is here
            if self.in_bounds(value.spot, self.bounds): # and stays here
                self._Model__entities[name] = value
                return
            for other in self.__others.values():
                if self.in_bounds(value.spot, other[0]): # goes to other
                    if other[2].acquire(False):
                        if value.hid == value.cid: # moves from home to other
                            value.cid = other[3]
                            other[1].write(name,value)
                            self._Model__entities[name] = other
                        elif other[3] == value.hid: # moves from other to home
                            value.cid = value.hid
                            other[1].write(name,value)                            
                            self._Model__entities[name] = None
                        elif self.__others.has_key(value.hid) and self.__others[value.hid][2].acquire(False):
                            # moves from other to other (report this to home)
                            value.cid = other[3]
                            other[1].write(name,value)                            
                            self.__others[value.hid][1].hop_entity(name,other[3])
                            self._Model__entities[name] = None
                            self.__others[value.hid][2].release()
                        other[2].release()
        elif self.__others[value.cid][2].acquire(False):
            # Entity isn't here thus remote invocation
            self.__others[value.cid][1].write(name,value)
            self.__others[value.cid][2].release()
            
    def read_basic(self, name):
        e = self._Model__entities[name]
        if isinstance(e, Entity):
            return copy.deepcopy(e)
        else:
            if e[2].acquire(False):
                res = e[1].read(name)
                e[2].release()
                return res
        
        print 'Entity',name,'not found.'
        return None

    def read_if_basic(self, name):
        e = self._Model__entities.get(name, None)
        if isinstance(e, Entity):
            return copy.deepcopy(e)
        elif e is not None:
            if e[2].acquire(False):
                res = e[1].read_if(name)
                e[2].release()
                return res
        
        print 'Entity',name,'not found.'
        return None
    
    def hop_entity(self, name, id):
        self._Model__entities[name] = self.__others[id]


class Environment(object):

    # singleton: allow only one environment instance
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/113657
    def __init__(self):
        self.model = None
        self.view = None
        self.controller = None


class PlaneEnvironment(Environment):
    def __init__(self, x_min=0, x_max=100, y_min=0, y_max=100):
        self.model = PlaneModel(x_min, x_max, y_min, y_max)
        self.controller = PlaneController(self.model)
        self.view = PlaneView(self.model, self.controller)

class DistEnvironment(Environment):
    def __init__(self, x_min=0, x_max=100, y_min=0, y_max=100):
        self.model = DistModel(x_min, x_max, y_min, y_max)
        self.controller = DistController(self.model)
        self.view = DistView(self.model, self.controller)
    
    def in_model(self,spot):
        return self.model.in_model(spot)
