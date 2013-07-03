class Node(object):
    def __init__(self):
        self.nid = ""
        self.names = []        # names are stored in tuples as <value, languageNID>
        self.statements = []
        self.attributes = []
        
    def get_name(self, language):
        for tup in self.names:
            if str(tup[1]) == str(language):
                return tup[0]
        try:
            return self.names[0][0]
        except:
            return 'Unknown-name'
    
    def __repr__(self):
        return "Node"
        
class Statement(object):
    def __init__(self):
        self.subject = ""
        self.predicate = ""
        self.object = ""
        self.attributes = []
        
    def __repr__(self):
        return "Statement"

class Attribute(object):
    def __init__(self):
        self.type = ""
        self.value = ""
        self.attributes = []
    
    def __repr__(self):
        return "Attribute"
        