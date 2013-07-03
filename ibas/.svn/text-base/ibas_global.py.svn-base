class IBASGlobal(object):
    
    @classmethod
    def print_message(cls, message, level):
        if IBASGlobal.verbose_level >= level:
            print message
    
    def __init__(self):
        cls = self.__class__
        cls.verbose_level = 0