#!/usr/bin/python

import sys, copy, re, string

def add(a, b): 
    if not(a == None or b == None):
        return Term(str(int(a.pred)+int(b.pred)), [])  
        
def sub(a, b):
    if not(a == None or b == None): 
        return Term(str(int(a.pred)-int(b.pred)), [])
        
def mul(a, b): 
    if not(a == None or b == None):
        return Term(str(int(a.pred)*int(b.pred)), [])
        
def lt(a, b): 
    if not(a == None or b == None):
        return int(a.pred) <  int(b.pred)
    else:
        return 0
        
def mt(a, b):
    if not(a == None or b == None): 
        return int(a.pred) >  int(b.pred)
    else:
        return 0
        
def eq(a, b): 
    if not(a == None or b == None):
        try: return(int(a.pred) == int(b.pred))
        except ValueError, msg: return(str(a.pred) == str(b.pred)) 
        
        
def eq2(a, b): 
    if not(a == None or b == None):
        return str(a.pred) == str(b.pred)

operators = {'+': add, '-':sub, '*':mul, '<':lt, '>':mt, '=':eq, '==':eq2}
    
def isVariable(term):
    return term.args == [] and term.pred[0:1] in string.uppercase

def isConstant(term):
    return term.args == [] and not term.pred[0:1] in string.uppercase

def split (l, sep, All=1):
    "Split l by sep but honoring () and []"
    nest = 0
    lsep = len(sep)
    if l == "": return []
    for i in range(len(l)):
        c = l[i]
        if nest <= 0 and l[i:i+lsep] == sep:
            if All: return [l[:i]]+split(l[i+lsep:], sep)
            else: return [l[:i], l[i+lsep:]]
        if c in ['[', '(']: nest = nest+1
        if c in [']', ')']: nest = nest-1
    return [l]

infixOps = ("*is*", "==", "<", ">", "+", "-", "*", "/", "=")
def splitInfix(s):
    for op in infixOps:
        p = split(s, op, All=0)
        if len(p) > 1: return (op, p)
    return None

def fatal (mesg):
    sys.stdout.write ("Fatal: %s\n" % mesg)
    sys.exit(1)

def parseTerm(s, args=None):
    if type(s) == string:
        s = s.strip()
    if not args:
        parts = splitInfix(s)
    if args:            # Predicate and args seperately
        self.pred = s
        self.args = []
        for arg in args:
            if type(arg) == str:
                temp = self.makeTerm(arg)
                self.args.append(temp)
            else:
                newpred = arg[0]
                newargs = arg[1]
                q = self.makeTerm(arg)
                self.args.append(q)
                
    elif parts:
        self.args = map(self.makeTerm, parts[1])
        self.pred = parts[0]
    elif s[-1] == ']':  # Build list "term"
        flds = split(s[1:-1], ",")
        fld2 = split(s[1:-1], "|")
        if len(fld2) > 1:
            self.args = map(self.makeTerm, fld2)
            self.pred = '.'
        else:
            flds.reverse()
            l = Term('.', [])
            for fld in flds: l = Term('.', [Term(fld), l])
            self.pred = l.pred; self.args = l.args
    elif s[-1] == ')':           # Compile from "pred(a,b,c)" string
        flds = split(s, '(', All=0)
      #  for x in s:
      #   print "^", x, "^"
        if len(flds) != 2: fatal("Syntax error in term: %s" % [s])
        self.args = map(self.makeTerm, split(flds[1][:-1], ','))
        self.pred = flds[0]
    else: 
        self.pred = s         # Simple constant or variable
        self.args = []


    return pred, args
    
def parseRule(s, args=None):   # expect "term:-term,term,..."
    if not args:
        if isinstance(s, Term):
            self.head = s
            self.goals = []
        else:
            s = s.rstrip('.')
            flds = string.split(s, ":-")
            self.head = Term(flds[0])
            self.goals = []
            if len(flds)==2:
                flds = split(flds[1], ",")
                for fld in flds: self.goals.append(Term(fld))
    else:
        if isinstance(s, Term):
            self.head = s
        else:
            self.head = Term(s, None)
        self.goals = []
        for g in args:
            if isinstance(g, Term):
                self.head = args
            else:
                self.goals.append(Term(g, None))

    return head, goals
    

class Term(object):
    """
    A Prolog term cosisting of a predicate and optional arguments.
    """
    
    def __init__ (self, s, args=None):
        if isinstance(s, Term):
            self.pred = s.pred
            self.args = s.args
        elif type(s) == tuple:
            self.pred = s[0]
            self.args = []
            argstemp = s[1]
            for argtemp in argstemp:
                temp = self.makeTerm(argtemp)
                self.args.append(temp)
                
        else:
            if type(s) == string:
                s = s.strip()
            if not args:
                parts = splitInfix(s)
            if args:            # Predicate and args seperately
                self.pred = s
                self.args = []
                for arg in args:
                    if type(arg) == str:
                        temp = self.makeTerm(arg)
                        self.args.append(temp)
                    elif type(arg) != tuple:        # in case of math in capabilities !  XANDER
                        newpred = arg[1]
                        newargs = [arg[0],arg[2]]
                        tuplearg = (newpred,newargs)
                        q = self.makeTerm(tuplearg)
                        self.args.append(q)
                    else:
                        newpred = arg[0]
                        newargs = arg[1]
                        q = self.makeTerm(arg)
                        #print "*****************************     ", newpred, newargs, q
                        self.args.append(q)
                        
            elif parts:
                if (parts[0] == '-') and len(parts[1][0]) == 0:
                    self.pred = s
                    self.args = []
                else:
                    self.args = map(self.makeTerm, parts[1])
                    self.pred = parts[0]
            elif s[-1] == ']':  # Build list "term"
                flds = split(s[1:-1], ",")
                fld2 = split(s[1:-1], "|")
                if len(fld2) > 1:
                    self.args = map(self.makeTerm, fld2)
                    self.pred = '.'
                else:
                    flds.reverse()
                    l = Term('.', [])
                    for fld in flds: l = Term('.', [Term(fld), l])
                    self.pred = l.pred; self.args = l.args
            elif s[-1] == ')':           # Compile from "pred(a,b,c)" string
                flds = split(s, '(', All=0)
              #  for x in s:
              #   print "^", x, "^"
                if len(flds) != 2: fatal("Syntax error in term: %s" % [s])
                self.args = map(self.makeTerm, split(flds[1][:-1], ','))
                self.pred = flds[0]
            else: 
                self.pred = s         # Simple constant or variable
                self.args = []

    def __repr__ (self):
        if self.pred == '.':
            if len(self.args) == 0: return "[]"
            nxt = self.args[1]
            if nxt.pred == '.' and nxt.args == []:
                return "[%s]" % str(self.args[0])
            elif nxt.pred == '.':
                return "[%s,%s]" % (str(self.args[0]), str(self.args[1])[1:-1])
            else:
                return "[%s|%s]" % (str(self.args[0]), str(self.args[1]))   
        elif self.args:
            return "<%s(%s)>" % (self.pred, string.join(map(str, self.args), ","))
        else: return self.pred
    
    def makeTerm(self, s):
        return Term(s)


class Rule(object):
    """
    A Prolog rule that consists of a head (a term) and an optional list of goals (also terms).
    """
    
    def __init__ (self, s, args=None):   # expect "term:-term,term,..."
        if not args:
            if isinstance(s, Term):
                self.head = s
                self.goals = []
            else:
                s = s.rstrip('.')
                flds = string.split(s, ":-")
                self.head = Term(flds[0])
                self.goals = []
                if len(flds)==2:
                    flds = split(flds[1], ",")
                    for fld in flds: self.goals.append(Term(fld))
        else:
            if isinstance(s, Term):
                self.head = s
            else:
                self.head = Term(s, None)
            self.goals = []
            for g in args:
                if isinstance(g, Term):
                    self.head = args
                else:
                    self.goals.append(Term(g, None))

    def __repr__ (self):
        return "<Rule: %s:- %s>" % (self.head, self.goals)
        

class Goal(object):
    """
    A Prolog goal, basically a rule with a parent.
    """
    
    def __init__ (self, rule, parent=None, env={}):
        self.rule = rule
        self.parent = parent
        self.env = copy.deepcopy(env)
        self.inx = 0      # start search with 1st subgoal

    def __repr__ (self):
        return "<Goal:%s:%d:%s>" % (self.rule, self.inx, self.env)


class Prolog(object):
    """
    The Prolog engine.
    """
    
    def __init__(self, rules=[], trace=False, indent=""):
        self.rules = rules
        self.trace = trace
        self.indent = indent
        self.shell = False
    
    def main(self):
        for file in sys.argv[1:]:
            if file == '.': return  # early out. no user interaction
            self.procFile(open(file), '')   # file on the command line
        self.procFile (sys.stdin, '? ')  # let the user have her say
    
    def procFile(self, f, prompt):
#       global rules, trace
        env = []
        while 1:
            if prompt:
                sys.stdout.write(prompt)
                sys.stdout.flush()
            sent = f.readline()
            if sent == "": break
            s = re.sub("#.*", "", sent[:-1]) # clip comments and newline
            s = re.sub(" is ", "*is*", s)   # protect "is" operator
            s = re.sub(" ", "" , s)      # remove spaces
            if s == "": continue
    
            if s[-1] in ['?', '.']: punc=s[-1]; s=s[:-1]
            else                : punc='.'
    
            if   s == 'trace': self.trace = not self.trace
            elif s == 'dump':
                for rule in self.rules: print rule
            elif punc == '?':
                self.search(Term(s), self.rules)
            else            : self.rules.append(Rule(s))
    
    # A Goal is a rule in at a certain point in its computation. 
    # env contains definitions (so far), inx indexes the current term
    # being satisfied, parent is another Goal which spawned this one
    # and which we will unify back to when this Goal is complete.
    #
    
    def unify(self, src, srcEnv, dest, destEnv):
        "update dest env from src. return true if unification succeeds"
#       global trace, indent
        if self.trace: print self.indent, "Unify", src, srcEnv, "to", dest, destEnv
        self.indent = self.indent+"  "
        if src.pred == '_' or dest.pred == '_': return self.sts(1, "Wildcard")
    
        if isVariable(src):
            srcVal = self.eval(src, srcEnv)
            if not srcVal: return self.sts(1, "Src unset")
            else: return self.sts(self.unify(srcVal, srcEnv, dest, destEnv), "Unify to Src Value")
    
        if isVariable(dest):
            destVal = self.eval(dest, destEnv)        # evaluate destination
            if destVal: return self.sts(self.unify(src, srcEnv, destVal, destEnv), "Unify to Dest value")
            else:
                destEnv[dest.pred] = self.eval(src, srcEnv)
                return self.sts(1, "Dest updated 1")    # unifies. destination updated
                
    
        elif src.pred    != dest.pred  : return self.sts(0, "Diff predicates")
        elif len(src.args) != len(dest.args): return self.sts(0, "Diff # args")
        else:                                                                           # Here the unification takes place!
            dde = copy.deepcopy(destEnv)
            for i in range(len(src.args)):
                if not self.unify(src.args[i], srcEnv, dest.args[i], dde):
                    return self.sts(0, "Arg doesn't unify")
            destEnv.update(dde)
            return self.sts(1, "All args unify")
            
    
    def sts(self, ok, why):
#       global trace, indent
        self.indent = self.indent[:-2]
        if self.trace: print self.indent, ["No", "Yes"][ok], why
        return ok
    
    def search(self, term, rules, env={}):
#       global trace
        # pop will take item from end, insert(0,val) will push item onto queue
        #print "searching for", term, "in", rules, "using", env

        goal = Goal(Rule("all(done):-x(y)"))      # Anything- just get a rule object
        goal.env = env  # <==== dit is hem !!!
        goal.rule.goals = [term]                  # target is the single goal
        queue = [goal]                        # Start our search
        results = []
        result = False
        result2 = True
    
        while queue:
            c = queue.pop()                      # Next goal to consider
            if self.trace: print "Deque", c
            if c.inx >= len(c.rule.goals):        # Is this one finished?
                if c.parent == None:                # Yes. Our original goal?
# for printing output when used as interactive shell
#                   if c.env: print  c.env       # Yes. tell user we              # COMMENT BY XANDER
#                   else    : print "Yes"         # have a solution             # COMMENT BY XANDER
    
                    if c.env:
                        result = True                               ##################################   LOOK AT THIS  #################################
                        results.append(c.env) # Yes. tell user we
                    #   if self.shell: print c.env
                    else:
                        result = True        # have a solution
                    #   if self.shell: print "Yes"
                    continue
                parent = copy.deepcopy(c.parent)    # Otherwise resume parent goal
                self.unify (c.rule.head, c.env, parent.rule.goals[parent.inx], parent.env)
                parent.inx = parent.inx+1          # advance to next goal in body
                queue.insert(0, parent)          # let it wait its turn
                if self.trace: print "Requeuing", parent
                continue
    
            # No. more to do with this goal.
            term = c.rule.goals[c.inx]            # What we want to solve
    
            pred = term.pred                        # Special term?
            if pred in ['*is*', 'is', 'cut', 'fail', '<', '==', '=', '>', '-', '+', '*', '/']:
                if pred in ['*is*', 'is']:
                    ques = self.eval(term.args[0], c.env)
                    ans  = self.eval(term.args[1], c.env) 
                    if ques == None:
                        c.env[term.args[0].pred] = ans  # Set variable
                    elif ques.pred != ans.pred:
                        continue                     # Mismatch, fail
                elif pred == 'cut': queue = []     # Zap the competition
                elif pred == 'fail': continue       # Dont succeed
                elif self.eval(term, c.env) is 0:        # Unbound variable found, don't fail yet!  by Xander
                    continue
                elif not self.eval(term, c.env):          # Fail if not true
                     c.env = False
                     result2 = False
                     results = False
                     break
                     
                         
                c.inx = c.inx + 1                   # Succeed. resume self.
                queue.insert(0, c) 
                continue
    
            for rule in rules:                     # Not special. Walk rule database
                if rule.head.pred != term.pred: continue
                if len(rule.head.args) != len(term.args): continue
                child = Goal(rule, c)               # A possible subgoal
                ans = self.unify(term, c.env, rule.head, child.env)
                if ans:                           # if unifies, queue it up
                    queue.insert(0, child)
                    if self.trace: print "Queuing", child
        if result is False and result2 is False:
            return False
        elif len(results) > 0:
            return results
        else:
            return result
    
    def eval(self, term, env):   # eval all variables within a term to constants
        special = operators.get(term.pred)
        if special:
            #print "---  special  ---   ", special(eval(term.args[0],env),eval(term.args[1],env))
            return special(self.eval(term.args[0], env), self.eval(term.args[1], env))
        if isConstant(term):
            return term
        if isVariable(term):
            ans = env.get(term.pred)
            if not ans: return None
            else: return self.eval(ans, env)
        args = []
        for arg in term.args:
                a = self.eval(arg, env)
                if not a: return None
                else: args.append(a)
        return Term(term.pred, args)

if __name__ == "__main__":
    p = Prolog()
    p.shell = True
    p.main()
