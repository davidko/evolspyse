from spyse.asw.environment import Environment2D, Controller2D
from sys import maxint
import time
import math
import wx
import struct


TYPES = { # type: (red, green, blue)
         'city':     (255,   0,   0), 
         'grass':    (  0, 255,   0), 
         'sea':      (  0,   0, 255), 
         'sand':     (255, 255, 255), 
         'airport':  (127, 127, 127), 
         'road':     (  0,   0,   0)
        }


class DI_Environment(Environment2D):

    def setup(self):
        self.xChart=1000.0; self.yChart=800.0
        #self.make_cells()
        self.make_roads()
        self.make_sensors()
        self.updateProcs.append(self.moveRobots)
        #self.updateProcs.append(self.update_cells)
        self.updateProcs.append(self.update_sensors)
        
    def set_controller(self):
        self.controller = DI_Controller(self.model)
    # model for updating robot positions in environment
    def moveRobots(self):
#        print "move_robots"
        for key, value in self.controller.find_items('label', 'Robot'):            
            v = value['speed']
            a = value['rotation']*(math.pi/180)
            x_old, y_old = value['location']
#            print x_old, y_old
            if v is not None and v>0:
                dt = time.time()-value['timestamp']
                x = x_old+math.cos(a)*v*dt
                y = y_old+math.sin(a)*v*dt
                self.controller.move(key, location=(x, y))

    def update_cells(self):
        pass

    def update_sensors(self):
        pass

    def bitmap2world(self, (xb, yb)):
        return (xw, yw)
        
    def colour2type(self, r, g, b):
        d = []
        for t, c in TYPES.iteritems():
            dx = r-c[0]; dy = g-c[1]; dz = b-c[2]
            d.append((math.sqrt(dx*dx + dy*dy + dz*dz), t))
        return min(d)[1]

    def make_cells(self):
        img = wx.Image("spyse/demo/DangerIsland/images/borkum_plain_1200x900_2.png", wx.BITMAP_TYPE_PNG)
        self.imgwidth = img.GetWidth()
        self.imgheight = img.GetHeight()
        nbytes = self.imgwidth*self.imgheight*3
        data = struct.unpack(str(nbytes)+'B', img.GetData())
        
        ## hexagonal cells
        self.cell_radius = rad = 3.0
        dia = rad * math.cos(30.0*math.pi/180.0)
        dd = 2*dia

        nr=0
        xi = 0; x = 0
        while x < self.imgwidth:
            yi = 0
            y = 0
            while y < self.imgheight:
                if yi%2 == 0:
                    x = xi*dd
                else:
                    x = xi*dd+dia
                i = (int(y)*self.imgwidth+int(x))*3
                r, g, b = data[i:i+3]
                t = self.colour2type(r, g, b)
                xw=(float(x)*self.xChart)/self.imgwidth; yw=self.yChart-(float(y)*self.yChart)/self.imgheight
                self.controller.place("cell"+str(nr), label="cell", location=(xw, yw), type=t, radius=self.cell_radius)
                yi = yi+1; y = yi*(1.5*rad)
                nr+=1
            xi = xi+1
    
    def make_roads(self):
#        f=open('spyse/demo/DangerIsland/roads.txt')
#        for i, line in enumerate(f):
#            x1, y1, x2, y2 = line.split()
#            name='RoadSegment_' + str(i)
#            beginloc=(int(float(x1)), int(float(y1)))
#            endloc=(int(float(x2)), int(float(y2)))
#            #print name, beginloc, endloc
#            self.controller.place(name, label="road", name=name, begin=beginloc, end=endloc)
#        f.close()
        f=open('spyse/demo/DangerIsland/roads.txt')
        nodes = {}
        edges = {}
        for i, line in enumerate(f):
            name, x, y = line.split()
            if name.startswith('Node'):
                nodes[name] = (int(float(x)), int(float((y))))
            elif name.startswith('Edge'):
                edges[name] = (x, y)
        f.close()
        self.controller.place("Roadmap", label="roadmap", nodes=nodes, edges=edges)

    def make_sensors(self):
        sensors = [ # (name, (x, y), state [colour], direction [road))
                   ("Sensor_1", (522,  99), (  0, 255,   0), 'Edge_00'),
                   ("Sensor_2", (375, 285), (  0, 255,   0), 'Edge_62'),
                   ("Sensor_3", (284, 362), (  0, 255,   0), 'Edge_36'),
                   ("Sensor_4", (325, 462), (255, 255,   0), 'Edge_42'),
                   ("Sensor_5", (585, 368), (255, 255,   0), 'Edge_61'),
                   ("Sensor_6", (705, 394), (  0, 255,   0), 'Edge_77'),
                   ("Sensor_7", (480, 505), (255,   0,   0), None)
                   ]
        for sensor in sensors:
            self.controller.place(sensor[0], label="sensor", name=sensor[0], location=sensor[1], state=sensor[2], direction=sensor[3])


class DI_Controller(Controller2D):
    """"""
    
    def __on_segment(self, point, delta, start, end):
        """"""
        
        xp, yp = point
        x0, y0 = start
        x1, y1 = end
        dx, dy = x1 - x0, y1 - y0
        # y = ax +/- b = dy/dx +/- delta
        a = float(dy)/float(dx)
        x, y = xp - x0, yp - y0
        
        if dx <= 0: xmin = dx-delta; xmax = delta
        else:       xmin = -delta; xmax = dx+delta
        
        if dy <= 0: ymin = dy-delta; ymax = delta
        else:       ymin = -delta; ymax = dy+delta
        
        if (xmin < x < xmax) and (ymin < y < ymax) and (abs(a*x-y) < delta):
            return True
        else:
            return False
    
    def on_road(self, key):
        """"""
        
        #TODO: create Roadmap class with appropriate methods
        self.roadmap = self.read('Roadmap')
        road_nodes = self.roadmap['nodes']
        road_edges = self.roadmap['edges']
        
        try:
            delta = 15    #TODO: use view distance of item
            item = self._model.read(key)
            point = item['location']
            roads = [road for road in road_edges.values() if self.__on_segment(point, delta, road_nodes[road[0]], road_nodes[road[1]])]
            return roads
        except:
            return []
        
    def distance(self, key, point):
        """"""
        
        if point is None:
            return maxint # no maxfloat found
        else:
            try:
                item = self._model.read(key)
                x0, y0 = item['location']
                x1, y1 = point
                dx, dy = x1-x0, y1-y0
                return math.sqrt(dx*dx + dy*dy)
            except:
                return maxint
