import thread
import threading
import time
from Queue import Queue

class ThreadPool(object):
    """Thread pool contains worker threads that can process agent behaviours"""
    
    def __init__(self, size):
        self.q = Queue()
        self.workers = []
        
        for i in range(size):
            w = Worker(self)
            self.workers.append(w)
            w.start()
            
    def die(self):
        for w in self.workers:
            w.die()
    
    def reschedule(self,agent):
        self.q.put(agent)
    
    def get_next(self):
        try:
            return self.q.get(False)
        except: return None

        
class Worker(threading.Thread):
    """Worker can take one agent and process its behaviour"""
    
    def __init__(self, pool):
        self.pool = pool
        self.running = False
        super(Worker, self).__init__()
        
    def die(self):
        self.running = False
    
    def run(self):
        self.running = True
        while self.running:   
            a = self.pool.get_next()
            if a is not None:
                start = time.clock()
                res = a.run_once()
                while res != 1 and a.state == 1 and (time.clock()-start) < 0.01:
                    res = a.run_once()
                
                if res != 1 and a.state == 1:
                    self.pool.reschedule(a)
            
            #time.sleep(0)
            time.sleep(0.001)

                
