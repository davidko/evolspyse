"""3APL reasoning behaviour"""

from copy import copy, deepcopy
from pyparsing import Literal, Combine, Optional, Word, Group, Forward, OneOrMore, ZeroOrMore, alphas, delimitedList, nums, oneOf

import spyse.prolog.prolog as prolog

from spyse.core.behaviours.behaviours import Behaviour
from spyse.aaapl.aaaplutils import supertest


class Condition(object):
    """Represents and tests simple conditions.
       If a 3APL condition should be removed, truth is False
       and is represented by the 'NOT' predicate.
       Testing is done against a base with facts (standard the
       beliefbase of an agent) using self.aaapl.prolog.search
       The result is the truth-value (success-value) of the test
       and the given bindings, called unification.
    """

    def __init__(self, aaapl, term, true=True):
        self.aaapl = aaapl
        self._term = term
        self._truth = true

    def __repr__ (self):
        if self._truth:
            return '[' + str(self._term) + ']'
        else:
            return '[' + 'NOT ' + str(self._term) + ']'

    def test(self, base, envi):
        """Atomic test using prolog"""
        if self._truth:
            if str(self._term) == str(prolog.Term('TRUE')):
                result = [{}]
                return (self._truth, result)
            else:
                result = self.aaapl.prolog.search(self._term, base, envi)
                return (self._truth, result)
        else:
            result = self.aaapl.prolog.search(self._term, base, envi)
            if type(result) == bool and not result:
                self._truth = False
                result = True
                return (self._truth, result)
            else:
                result = False
                return (self._truth, result)


class AndCondition(object):
    """Obsolete, since ANDconditions are subclass of CompositeConditions,
       we can use only one class!!
    """
    pass


class CompositeCondition(object):
    """Checks and represents composite conditions by digesting them
       into left and right parts.  Composite conditions are equal to
       AND conditions, replacing 'AND' by a ','.  In this procedure the
       left branch of the condition is checked first.  Iff unification
       is still possible, the right part is also checked.
    """
    def __init__(self, aaapl, left, right, true=True):
        self.aaapl = aaapl
        self._left_cond = left
        self._right_cond = right
        self._truth = true

    def __repr__ (self):
        return '['+ str(self._left_cond) + ' AND ' + str(self._right_cond) +']'

    # NEXT PART IS COPIED FROM AND-CONDITION:
    def test(self, base, envi):
        """Test both parts of the condition"""

        left_result = self._left_cond.test(base, envi)
        if left_result:
            if type(left_result[1]) == list:
                envi.update(left_result[1][0])
            elif left_result[1]:
                if self.aaapl.debug: 
                    print self._left_cond, 
                    "  LEFT  --> RELATION FOUND, RESULT WAS TRUE !!"
            else:
                #if (not(has_value(envi, None)) and len(envi) > 0):
                if self.aaapl.debug:
                    print self._left_cond, left_result
                    print "  LEFT  --> RELATION FOUND, BUT THE RESULT WAS  FALSE!! \t UNIFICATION FAILED"
                return (self._truth, False)

        else:
            print "unification failed" 

        right_result = self._right_cond.test(base, envi)
        if right_result:
            if type(right_result[1]) == list:
                envi.update(right_result[1][0])
                return (self._truth, [envi])
            elif right_result[1]:
                if self.aaapl.debug: 
                    print self._right_cond, 
                    "  RIGHT  --> RELATION FOUND, RESULT WAS TRUE !!"
                return (self._truth, [envi])
            else:
             #   if (not(has_value(envi, None)) and len(envi) > 0):
                if self.aaapl.debug: 
                    print self._right_cond, right_result, 
                    print "  RIGHT  --> RELATION FOUND, BUT THE RESULT WAS  FALSE!! \t UNIFICATION FAILED"
                #envi = {}        # NOTE   LOOK AT THIS !!! Very Important !!!!  XANDER
                return (self._truth, False)
        else:
            print "unification failed" 


class OrCondition(CompositeCondition):
    """Checks and represents OR conditions by digesting them into
       left and right parts.  Or conditions yield True (and possible
       unification) if left and right branch or both are unifiable.
       It returns 0, 1 or 2 dictionaries with possible unifactions.
    """
    def __repr__ (self):
        return '[' + str(self._left_cond) + ' OR ' + str(self._right_cond) + ']'

    def test(self, base, envi):
        """Test both parts of the condition"""
        left_result = self._left_cond.test(base, envi)
        right_result = self._right_cond.test(base, envi)

        if ((type(left_result[1]) == list) and (type(right_result[1]) == list)):
            self._truth = self._left_cond._truth and self._right_cond._truth
            return (self._truth, [left_result[1][0], right_result[1][0]])
        else:
            if (type(left_result[1]) == list):
                return left_result
            if (type(right_result[1]) == list):
                return right_result


class Operation(object):
    """Represents the operation part of a capability.
       An operation has an operator and optional arguments as operands
    """

    def __init__(self, operator, operands):
        self._operator = operator
        self._operands = operands

    def __repr__ (self):
        return self._operator + str(self._operands)


class Capability(object):
    """Capabilities consist of three parts, the precondition, operator and postcondition.
        The pre condition makes sure all needed variables are bounded (unified) for use in the post condition.
        The post condition upodates he beliefbase of an agent by adding and removing facts.
        Functions are defined for getting these parts of the capability.
        An extra post2 condition is created because updating the postcondition replaces variables with values,
        rendering the postcondition useless for a second use.
        This way the postcondition worked on is always a copy (deepcopy) of the original (post2).
    """

    def __init__(self, pre, operator, post, post2):
        self.pre = pre
        self.operator = operator
        self.post = post
        self.post2 = post2

    def set_post(self, newpost):
        """Set new postcondition"""
        self.post = newpost    

    def set_post2(self):
        """Set new post2condition"""
        self.post = copy(self.post2)

    def get_pre(self):
        """Get precondition"""
        return self.pre           

    def get_operator(self):             
        """Get operator"""
        return self.operator             

    def get_post(self):
        """Get postcondition"""
        return self.post         

    def get_post2(self):
        """Get post2condition"""
        return self.post2        


class Capabilitybase(list):
    """Adds capabilities to the agent's capabilitybase"""

    def add(self, capability):
        """Add a capability to the capabilitybase"""
        self.append(capability)


class Belief(object):
    """A belief"""
    pass


class Beliefbase(list):
    """Adds beliefs to the agent's beliefbase.
       Also has a function to get a wanted belief from the beliefbase 
       or to set a certain new belief in the beliefbase from outside AAAPL
    """

    def add(self, belief):
        """Add a belief to the beliefbase"""
        self.append(belief)

    def getbelief(self, beliefyouwant):
        """Get a belief from the beliefbase"""
        for belief in self.datastore['beliefbase']:
            if str(belief.pred) == str(beliefyouwant):
                return belief.args

    def setbeliefs(self, pred, args):
        """Set a belief"""
        self.datastore['beliefbase'].add(prolog.Rule(prolog.Term(pred, args)))


class Planbase(list):
    """Creates a planbase for the agent.
       If a rule is selected for execution in the deliberation cycle,
       it is added to the plan of an agent.  The entire operation is
       done during (and therefore in) the deliberation cycle.
    """

    def add(self, plan):
        """Add a plan to the planbase"""
        if self.aaapl.debug: 
            print 'het plan is: ', plan              
        self.append(plan)
        # move the following into deliberation cycle
        if isinstance(plan, prolog.Rule):
            if self.aaapl.debug: 
                print 'het plan is: ', plan          
            self.append(plan)
        elif isinstance(plan, ComplexGoal):
            if self.aaapl.debug: 
                print 'het plan is: ', plan          
            self.append(plan)


class Goal(object):
    """A Goal"""
    def __init__(self, goal):
        self.goal = goal

    def execute(self):
        """Is done in planbase and subgoal defenitions"""
        # Override in specific goals
        pass


class AtomicGoal(Goal):
    """This is where the real action takes place.
       If an Atomic goal is selected for execution,the following process is started:
       1- Find corresponding capability
       2- Check if the capability is feasible
       3- Unify the operator / operands w.r.t. the already existing unification
       4- Unify and check the pre condition of the capability
       5- Unify post condition of capability
       6- Update beliefbase by adding and/or removing facts
    """

    def __init__(self, aaapl, pred, args):
        self.aaapl = aaapl
        self.pred = pred
        self.args = args

    def execute(self):
        """Atomic execution starts here"""

        counter = 0
        print "\n==================================================================="
        print "==                   Starting Atomic Execution                   =="
        print "===================================================================\n"
        print "executing Atomic predicate:\t", self.pred, self.args, self.aaapl.uni, "\n"

     # **********      FIND CAPABILITY IN CAPABILITYBASE OR IT'S A RULE         ********** #
        firstchar = str(self.pred)[0]
        if firstchar.islower():
            for rule in self.aaapl.rulebase:
                if str(rule.get_head().pred) == str(self.pred):
                    if self.aaapl.debug:
                        head = rule.get_head()  
                    break
            print "---->   ", head, head.pred, head.args
            if len(self.args) > 0:
            #############################################################################

                self.aaapl.headunification = {}
                countheadval = 0
                while countheadval < len(self.args):
                    arg  = str(self.args[countheadval])
                    arg2 = str(head.args[countheadval])

                    if type(arg) != str:
                        termeval = self.aaapl.prolog.eval(arg, self.aaapl.uni)
                        if self.aaapl.debug: 
                            print "\n\nTerm gevonden! Moet eerst berekend worden!   ", arg, "    ---->   ", termeval, "\n\n"
                        arg = str(termeval) 

                    if arg[0].islower() or arg[0].isdigit() or (arg[0] == "-" and arg[1:].isdigit()):
                        self.aaapl.headunification[arg2] = prolog.Term(arg)
                        countheadval = countheadval + 1
                    elif arg in self.aaapl.uni:
                        headval = self.aaapl.uni[arg]
                        self.aaapl.headunification[arg2] = headval
                        countheadval = countheadval + 1
                counter = 0
                if (countheadval == len(self.args)) or (countheadval > len(self.args)):               
                    if self.aaapl.debug: 
                        print "Unification replacement:\t", self.args, "-->", head.args
                    if self.aaapl.debug: 
                        print "Unification:\t\t\t", self.aaapl.uni
                    print "Head unification:\t\t", self.aaapl.headunification, "\n"
                    self.aaapl.uni = self.aaapl.headunification


            #############################################################################


            if self.aaapl.debug: 
                print "het is een rule !!!"

            def checkfeas2(rule):
                """Check feasibility of rule when encountered in body"""
                guard = rule.get_guard()
                head = rule.get_head()
                body = rule.get_body()
                self.aaapl.guarduni = None

                if self.aaapl.debug: 
                    print "***  ", head.pred, head.args
                if len(head.args) == 0:
                    self.aaapl.uni = {}

                if self.aaapl.debug: 
                    print "guard\t", guard, type(guard)
                if self.aaapl.debug: 
                    print "uni\t", self.aaapl.uni
                result = supertest(self, self.aaapl.beliefbase, guard, self.aaapl.uni)     
                if result and (type(result[1]) == list):
                    self.aaapl.guarduni = result
                    self.aaapl.uni = result[1][0] 
                    body.execute()
                elif result and result[1]:
                    body.execute()
                else:
                    if self.aaapl.debug: 
                        print "Rule ", head, "is not feasable"
                    return self.aaapl.uni

            checkfeas2(rule)

        elif firstchar.isupper() :

            if str(self.pred) == "SKIP":
                if self.aaapl.debug: 
                    print "SKIP goal found. So we do nothing !!!!"
                skipfound = 1
            else: skipfound = 0


            capbasecount = 0
            capfound = 0
            capuni = 0
            preuni = 0
            postdigest = 0
           # postrep = 0
            postupdate = 0

            while capbasecount < len(self.aaapl.capabilitybase):
                capelem = self.aaapl.capabilitybase[capbasecount].get_operator()
                capelemop = capelem._operator
                #capelemopr = capelem._operands
                if (str(capelemop) != str(self.pred)):
                    capbasecount = capbasecount + 1
                else:
                    capfound = 1
                    break

       # **********      UNIFY SELECTED CAPABILITY / UPDATE DICTIONAIRY        ********** #
            if capfound == 1:
                self.aaapl.capunification = {}
                countcapval = 0
                while countcapval < len(self.args):
                    arg  = self.args[countcapval]
                    arg2 = capelem._operands[countcapval]

                    if type(arg) != str:
                        termeval = self.aaapl.prolog.eval(arg, self.aaapl.uni)
                        if self.aaapl.debug: 
                            print "\n\nTerm gevonden! Moet eerst berekend worden!   ", arg, "    ---->   ", termeval, "\n\n"
                        arg = str(termeval) 

                    if arg[0].islower() or arg[0].isdigit() or (arg[0] == "-" and arg[1:].isdigit()):
                        self.aaapl.capunification[arg2] = prolog.Term(arg)
                        countcapval = countcapval + 1
                    elif arg in self.aaapl.uni:
                        capval = self.aaapl.uni[arg]
                        self.aaapl.capunification[arg2] = capval
                        countcapval = countcapval + 1
                    else:
                        if self.aaapl.debug: 
                            print "\nUnification failed....... Lets see if we have encountered OR in guards"
                        counter = counter + 1
                        if (type(self.aaapl.guarduni[1]) == list) and (counter < len(self.aaapl.guarduni[1])):
                            self.aaapl.uni = self.aaapl.guarduni[1][counter]
                            if self.aaapl.debug: 
                                print "new dic for unification:  ", self.aaapl.uni, "\n"
                            self.execute()
                            break
                        else:
                            print "\nNo OR found ! Execution failed and stopped!\n"
                            break 
                if (countcapval == len(self.args)) or (countcapval > len(self.args)):               
                    print "Found capability:\t\t", capelem
                    if self.aaapl.debug: 
                        print "Unification replacement:\t", self.args, "-->", capelem._operands
                    if self.aaapl.debug: 
                        print "Unification:\t\t\t", self.aaapl.uni
                    print "Capability unification:\t\t", self.aaapl.capunification, "\n" 
                    capuni = 1

      # **********      UNIFY PRE CONDITION OF CAPABILITY        ********** #
            if capuni == 1:
                cpre  = self.aaapl.capabilitybase[capbasecount].get_pre()   
                if self.aaapl.debug: 
                    print "Pre: \t\t\t\t", cpre
                self.aaapl.uni2 = self.aaapl.uni
                self.aaapl.uni = {}
                if (str(cpre) == None) or (str(cpre) == "[TRUE]") or (str(cpre) == "[true]") or (str(cpre) == "None"):
                    #tpre = (True, [{}])
                    preuni = 1
                    self.aaapl.uni = self.aaapl.capunification
                else:
                    res = supertest(self, self.aaapl.beliefbase, cpre, self.aaapl.capunification)
                    if res and (type(res[1]) == list):
                        self.aaapl.cpreuni = res
                        self.aaapl.uni = res[1][0]
                        #self.aaapl.uni.update(self.aaapl.capunification)
                        if self.aaapl.debug: 
                            print "\nPRE unification SUCCESFULL:\t", self.aaapl.uni, "\n"
                        preuni = 1 
                    else:
                        print "\n--> *(3)*  Unable to unify PRE of capability! Check your code !!!!\n"

       # **********      DIGEST POSTCONDITION TO LIST OF TERMS        ********** #
            if preuni == 1:
                cpost_original = self.aaapl.capabilitybase[capbasecount].get_post2()
                cpost = self.aaapl.capabilitybase[capbasecount].get_post()
                if (str(cpost) == None) or (str(cpost) == "[TRUE]") or (str(cpost) == "[true]") or (str(cpost) == "None"):
                    if self.aaapl.debug: 
                        print "\n\nPOST of Capability is empty! Therefore execution is finished!!\n\n"
                    skipfound = 1
                else:
                    if self.aaapl.debug: 
                        print "POST: \t\t\t\t", cpost
                    termlist = []

                    def digest(condition):
                        """Make list of atomic conditions from a complex condition"""
                        if type(condition) == Condition:
                            termlist.append(condition)
                        else:
                            digest(condition._left_cond)
                            digest(condition._right_cond)

                    originalpre  = self.aaapl.capabilitybase[capbasecount].get_pre()
                    originalop   = self.aaapl.capabilitybase[capbasecount].get_operator()
                    self.aaapl.capabilitybase.remove(self.aaapl.capabilitybase[capbasecount])
                    self.aaapl.datastore['capabilitybase'] = self.aaapl.capabilitybase

                    digest(cpost)
                    if self.aaapl.debug: 
                        print "TERMLIST: \t\t\t", termlist, "\n"
                    postdigest = 1  

        # **********         REPLACE POST VARIABLES WITH VALUES AND UPDATE BELIEFS        ********** #

            if postdigest == 1:
                walktl = 0
                while walktl < len(termlist):
                    facthead = termlist[walktl]._term
                    facttruth = termlist[walktl]._truth
                    factpred = facthead.pred
                    argstemp = []
                    for argument in facthead.args:
                        argstemp.append(deepcopy(argument))
                    factargs2 = facthead.args


                    reparg = 0
                    while reparg < len(factargs2):
                        singlearg = factargs2[reparg]
                        argstr = str(copy(singlearg))

                        if argstr in self.aaapl.uni:
                            factargs2[reparg] = self.aaapl.uni[argstr]      
                            reparg = reparg + 1
                        elif argstr[0].islower() or argstr[0].isdigit() or (argstr[0] == "-" and argstr[1:].isdigit()):
                            if self.aaapl.debug: 
                                print "Integer or atomic value found.... no binding needed!"
                            reparg = reparg + 1
                        elif argstr[0] == "<":
                            termeval = self.aaapl.prolog.eval(singlearg, self.aaapl.uni)
                            if self.aaapl.debug: 
                                print "\nCapability heeft een term!!   ", singlearg, "    ---->   ", termeval, "\n"
                            factargs2[reparg] = termeval

                            reparg = reparg + 1
                        else:
                            print "Ununified argument in POST of capability! PROGRAMMER ERROR !!!!"
                            break
                    if self.aaapl.debug: 
                        print "FACT:", "\t\t\t\t", facthead, facttruth 

                    if facttruth:
                        new_belief = prolog.Rule(copy(facthead))
                        self.aaapl.beliefbase.add(new_belief)
                        print "BELIEF ADDED:\t\t\t",  new_belief, "\n"
                    else:
                        bbase = 0
                        while bbase < len(self.aaapl.beliefbase):
                            belief = self.aaapl.beliefbase[bbase]#.get_head()
                            beliefhead = belief.head
                            beliefpred = beliefhead.pred
                            beliefargs = beliefhead.args
                            if (beliefpred == factpred):
                                if (str(beliefargs) == str(factargs2)):
                                    self.aaapl.beliefbase.remove(belief)
                                    print "BELIEF REMOVED:\t\t\t", beliefhead, "\n"
                                else:
                                    pass
                            bbase = bbase + 1
                    facthead.args = argstemp
                    walktl = walktl + 1
                postupdate = 1

            if capuni == 1:
                self.aaapl.uni = self.aaapl.uni2

            if postupdate == 1:

                self.aaapl.capabilitybase.add(Capability(originalpre, originalop, cpost_original, cpost_original))
                self.aaapl.datastore['capabilitybase'] = self.aaapl.capabilitybase

            if skipfound == 1 or postupdate == 1:

                print "==================================================================="
                print "==                 UPDATING FINISHED SUCCESFULLY                 =="       
                print "===================================================================\n\n\n"
            else:
                print "UPDATING OR EXECUTION FAILED....."

            raw_input("\n\n\t\t*** Xander says:   Please hit enter to continue  ***   \n\n")  # PAUSE statement


class ComplexGoal(Goal):
    """a complexgoal"""
    pass


class PredicateGoal(Goal):
    """a predicategoal"""
    pass


class SequenceGoal(ComplexGoal):
    """Sequence goals are sequences of atomic or other goals.
       When encountered, all atomic subgoals are placed in the agent's
       planbase.  Because we need to ensure that the order of the sequence
       is preserved, we will need to insert the sequence at the start op
       the planbase in the case other plans are present.  Also, we need
       to replace the variables with the unified values before we lose them.
    """

    def __init__(self, goal, aaapl):
        self.aaapl = aaapl
        self.goal = goal

    def execute(self):
        """What to do with a sequence of goals"""
        if self.aaapl.debug:    
            print "SequenceGoal"
        tempplan = []
        for subgoal in self.goal:
            tempgoal = copy(subgoal)
            tempplan.append(tempgoal)
        if len(self.aaapl.planbase) > 0:
            tempplan.extend(self.aaapl.planbase)
            self.aaapl.planbase = tempplan
        else:
            self.aaapl.planbase = tempplan 


class IfGoal(ComplexGoal):           
    """If goals are part of a rule which will be executed conditionally"""

    def __init__(self, precond, thenstm, elsecond, aaapl):
        self.aaapl = aaapl
        self.precond = precond
        self.thenstm = thenstm
        self.elsecond = elsecond

    def execute(self):
        """Check the IF statement.
           If unification is succesfull, we can start putting the body
           of the IF statement in the planbase.  If not, check whether
           there is an ELSE statement.  If there is one, we plan it,
           otherwise the whole execution fails and stops
        """

        if self.aaapl.debug: 
            print "\nIfGoal !!!!\n"
        precond  = self.precond
        body = self.thenstm
        if self.aaapl.debug: 
            print "precond:\t\t", precond
        res = supertest(self, self.aaapl.beliefbase, precond, self.aaapl.uni)
        if res and (type(res[1]) == list) :
            if self.aaapl.debug: 
                print "precond Unification:\t", res[1][0], "\n"
            self.aaapl.planbase.insert(0, body)
        else:
            print "precond Unification:\tUNIFICATION FAILED !!!!", self.elsecond
            if self.elsecond != None:
                body = self.elsecond
                self.aaapl.planbase.insert(0, body)
            else:
                print "Unification IF statement failed, no ELSE statement was given, execution stopped"


class WhileGoal(ComplexGoal):
    """While goals are part of a rule which will be executed conditionally"""

    def __init__(self, precond, whilest, aaapl):
        self.aaapl = aaapl
        self.precond = precond
        self.whilest = whilest

    def execute(self):
        """Check the WHILE statement.
           If unification is succesfull, we can start putting the body
           in the planbase.  the proces fails otherwise.  Because the
           unification changes during WHILE execution, we need to update
           it every step.  The while goals is addedto the planbase as
           long as its condition holds.
        """

        if self.aaapl.debug: 
            print "\nWHILEGoal !!!!\n"
        precond  = self.precond
        body = self.whilest
        if self.aaapl.debug: 
            print "precond:\t\t", precond
        whiletempuni = self.aaapl.uni
        # self.aaapl.uni = {}            # NOTE   LOOK AT THIS !!! Very Important !!!!  XANDER
        res = supertest(self, self.aaapl.beliefbase, precond, self.aaapl.uni)
        if res and (type(res[1]) == list):
            whiletempuni.update(res[1][0])
            temp2 = whiletempuni
            self.aaapl.uni = temp2
            if self.aaapl.debug: 
                print "precond Unification:\t", self.aaapl.uni, "\n"  #res[1][0]
            self.aaapl.planbase.insert(0, body)
            self.aaapl.planbase.insert(1, self)
        else:
            print "precond Unification:\t UNIFICATION FAILED !!!!"
            self.aaapl.uni = whiletempuni


class Goalbase(list):
    """Makes it possible to add and/or replace goals"""

    def add(self, goal):
        """Add goal"""

        self.append(goal)

    def replace(self, old_goal, new_goal):
        """Replace goal"""
        pass


class Rule(object):
    """A rule consists of a head, guard.
       The head can be called from within a rule body or can be matched
       against the goalbase.  Before the body (a collection of one or
       more goals) of the rule is executed the guard is tested.  If the
       testresult is True (and thus a valid unification is found) the
       body is executed using this unification.  All parts of the rule
       can be set or asked for (get).
    """

    def __init__(self, head, guard, body):
        self.set_head(head)
        self.set_guard(guard)
        self.set_body(body)

    def set_head(self, term):
        """Set head of rule"""
        self.head = term

    def get_head(self):
        """Get head of rule"""
        return self.head

    def set_guard(self, guard):
        """Set guard of rule"""
        self.guard = guard

    def get_guard(self):
        """Det guard of rule"""
        return self.guard

    def set_body(self, body):
        """Set body of rule"""
        self.body = body

    def get_body(self):
        """Get body of rule"""
        return self.body


class Rulebase(list):
    """Adds rules to rulebase"""

    def add(self, rule):
        """Append the rule to the base"""

        self.append(rule)


LEFT = '('
RIGHT = ')'
NOT = 'NOT'
AND = 'AND'
OR = 'OR'

class Parser(object):
    """Functionality needed for parsing 3APL.
       It consists of a parser (converting 3APL parts to parse-elements) 
       and functions to convert these elements to prolog terms.
    """

    def __init__(self, aaapl):
        self.aaapl = aaapl

    def __pe2term(self, parse_elem):
        """Transform a ParseElement into a Prolog Term"""

        if parse_elem.getName() in ("atom", "AtomicGoal", "operation", "opr"):
            res = list(parse_elem)                   
        else:
            res = list(parse_elem[0])

        def removebrackets(res):
            """Remove brackets"""
            try:
                res.remove('(')
                res.remove(')')
                res.remove('.')
            except ValueError:
                pass         

        removebrackets(res)       

        relations = ["+", "-", "/", "*", "<", ">", "="]
        testrel = [rel in res for rel in relations]

        if 'is' in res:
            tempterm = self.__pe2term(res[2])
            newargs = []
            newargs.insert(0, res[1])
            newargs.insert(1, tempterm)
            return res[0], newargs


        if True in testrel: 
            if type(res[0]) == str:
                term1 = res[0]
            else:
                term1 = self.__pe2term(res[0])
            if type(res[2]) == str:
                term2 = res[2]    
            else:
                term2 = self.__pe2term(res[2])

            newt = []
            newt.insert(0, term1)
            newt.insert(1, term2) 
            return res[1], newt   
        try:
            res.remove('(')
            res.remove(')')
            res.remove('.')
        except ValueError:
            pass
        return res[0], res[1:]

    def debugaction(self, label):
        """the current action"""

        def theaction():
            """the current action"""
            return theaction

    def __pe2cond(self, parse_elem, truth=True):
        """Transform a ParseElement into a Condition"""
        try:
            name = parse_elem.getName()
        except:
            name = type(parse_elem)

        if name is 'wfflist':
            pass 
            if len(parse_elem) is 1:
                return self.__pe2cond(parse_elem[0], truth)
            else:
                return CompositeCondition(self.aaapl, self.__pe2cond(parse_elem[0]), self.__pe2cond(parse_elem[1:]), truth)
        elif name in [list, 'wff']:
            if name is 'wff':
                pass 
                parse_elem = list(parse_elem)
            else:
                pass 
            if len(parse_elem) is 1:
                return self.__pe2cond(parse_elem[0], truth)
            elif OR in parse_elem:
                i = parse_elem.index(OR)
                return OrCondition(self.aaapl, self.__pe2cond(parse_elem[:i]), self.__pe2cond(parse_elem[i+1:]), truth)
            elif AND in parse_elem:                                                                  
                i = parse_elem.index(AND)
                return CompositeCondition(self.aaapl, self.__pe2cond(parse_elem[:i]), self.__pe2cond(parse_elem[i+1:]), truth)
            else:
                return CompositeCondition(self.aaapl, self.__pe2cond(parse_elem[0]), self.__pe2cond(parse_elem[1:]), truth)
        elif name is 'wffTerm':
            pass 
            return self.__pe2cond(parse_elem[0], truth)
        elif name is 'wffNegation':
            pass 
            return self.__pe2cond(parse_elem[1], False)
        elif name is 'wffCompound':
            pass 
            return self.__pe2cond(parse_elem[0], truth)
        elif name is 'str':
            pass 
        elif name is 'atom':
            res = self.__pe2term(parse_elem)              
            return Condition(self.aaapl, prolog.Term(res[0], res[1]), truth)
        else:
            return None

    def __pe2op(self, parse_elem):
        """transform a ParseElement into an Operation"""
        op_elem = list(parse_elem)
        try:
            op_elem.remove('(')
            op_elem.remove(')')
        except ValueError:
            pass
        return op_elem[0], op_elem[1:]

    def addCapabilities(self):
        """Add capabilities to the capabilitybase"""

        def theaction(strg, loc, tokens):
            """current action"""

            print "\n*** CAPABILITIES:", len(tokens)
            for capability in tokens:
                pre = self.__pe2cond(capability[0][1]) # process { cond } without {}
                opr_elem = self.__pe2op(capability[1])
                opr = Operation(opr_elem[0], opr_elem[1])
                post = self.__pe2cond(capability[2][1])
                post2 = self.__pe2cond(capability[2][1]) 
                self.aaapl.capabilitybase.add(Capability(pre, opr, post, post2))

                print 'Capability'
                print '\tpre \t', pre
                print '\top  \t', opr
                print '\tpost\t', post, '\n'
        return theaction 

    def addBeliefs(self):
        """Add beliefs to the beliefbase"""
        def theaction(strg, loc, tokens):       #   ------> need also support :- -style rules ???
            """current action"""
            print "\n*** BELIEFS:", len(tokens)
            for belief in tokens:
                res = self.__pe2term(belief)
                self.aaapl.beliefbase.add(prolog.Rule(prolog.Term(res[0], res[1])))
            for i in self.aaapl.beliefbase: 
                print '\t', i
        return theaction

    def addSequenceGoal(self):
        """Add sequencegoals to goalbase"""
        def theaction(strg, loc, tokens):
            """current action"""
            res = list(tokens)
            print "SequenceGoal:", ''.join(res)
            self.temp_goals.add(res)
        return theaction

    def addComplexGoal(self):
        """Add complexgoals to goalbase"""
        def theaction(strg, loc, tokens):
            """current action"""
            res = list(tokens)
            print "ComplexGoal:", ''.joint(res)
            self.temp_goals.add(res)
        return theaction

    def addGoals(self):
        """Add simplegoals to goalbase"""
        def theaction(strg, loc, tokens):
            """current action"""
            print "\n*** GOALS:", len(tokens)
            if 'BEGIN' in list(tokens[0]):
                tokens = tokens[0]
            for goal in tokens:
               #print "********", goal.getName()
                if goal in ['BEGIN', ';', 'END']:
                    pass
                else:
                    res = self.__pe2term(goal)
                    self.aaapl.goalbase.add(prolog.Rule(prolog.Term(res[0], res[1]), None))
            for i in self.aaapl.goalbase: 
                print '\t', i
        return theaction

    def __splitOrGuards(self, grd, g_or=None):
        """Splits guard with OR predicate in two branches"""
        if g_or is None: 
            g_or = []
        OR = 'OR'
        if OR in grd:
            pos = grd.index(OR)
            g_or.append(self.__splitAndGuards(grd[:pos]))
            self.splitOrGuards(grd[pos+1:], g_or)
        else:
            g_or.append(self.__splitAndGuards(grd))
        return g_or

    def __splitAndGuards(self, grd, g_and=None):
        """Splits guard with AND predicate in two branches"""
        if g_and is None: 
            g_and = []
        AND = 'AND'
        if AND in grd:
            pos = grd.index(AND)
            res = self.__pe2term(grd[:pos])
            g_and.append(prolog.Term(res[0], res[1]))
            self.__splitAndGuards(grd[pos+1:], g_and)
        else:
#          print "NO"
            res = self.__pe2term(grd)
            g_and.append(prolog.Term(res[0], res[1]))
        return g_and

    def __make_rule_body(self, parse_elem):
        """Seperate the goals in the body of a rule w.r.t. their type"""
        pen = parse_elem.getName()

        if pen is 'PredicateGoal':
            res = self.__pe2term(parse_elem)
            return PredicateGoal(prolog.Term(res[0], res[1]))

        elif pen is 'AtomicGoal':
            pe2 = []
            for i in parse_elem:
                if type(i) != str:
                    i = prolog.Term(self.__pe2term(i))
                    pe2.append(i)
                else:
                    pe2.append(i)   

            gbody = list(pe2)

            try:
                gbody.remove('(')
                gbody.remove(')')
            except ValueError:
                pass
            pred, args = gbody[0], gbody[1:]
            return AtomicGoal(self.aaapl, pred, args)

        elif pen is 'SequenceGoal':
            plist = list(parse_elem)
            plist.remove('BEGIN')
            sep = plist.count(';')
            for i in range(sep):
                plist.remove(';')
            plist.remove('END')
            body = []
            for gbody in plist:
                body.append(self.__make_rule_body(gbody))
            return SequenceGoal(body, self.aaapl)

        elif pen is 'ComplexGoal':
            plist = list(parse_elem)
            if 'BEGIN' in plist:
                seqfound = 1
            else:
                seqfound = 0

            if seqfound == 1:
                plist.remove('BEGIN')
                sep = plist.count(';')
                for i in range(sep):
                    plist.remove(';')
                plist.remove('END')
                body = []
                for gbody in plist:
                    body.append(self.__make_rule_body(gbody))
                return SequenceGoal(body, self.aaapl)
            else:
                if str(plist[0].getName()) == "WhileGoal":
                    pre  = self.__pe2cond(plist[0][1])
                    whilebody = self.__make_rule_body(plist[0][3])
                    return WhileGoal(pre, whilebody, self.aaapl)
                if str(plist[0].getName()) == "IfGoal":
                    pre  = self.__pe2cond(plist[0][1])
                    ifbody = self.__make_rule_body(plist[0][3]) 
                    # check if there is an ELSE statement, this means it body consists of 6 parts
                    if len(plist[0]) == 6:
                        elsebody = self.__make_rule_body(plist[0][5])
                        return IfGoal(pre, ifbody, elsebody, self.aaapl)
                    else:
                        return IfGoal(pre, ifbody, None, self.aaapl)

        elif pen is 'IfGoal':
            plist = list(parse_elem)
            pre  = self.__pe2cond(plist[0][1])
            ifbody = self.__make_rule_body(plist[0][3]) 
            # check if there is an ELSE statement, this means it body consists of 6 parts
            if len(plist[0]) == 6:
                elsebody = self.__make_rule_body(plist[0][5])
                return IfGoal(pre, ifbody, elsebody, self.aaapl)
            else:
                return IfGoal(pre, ifbody, None, self.aaapl)

        elif pen is 'WhileGoal':
            plist = list(parse_elem)
            pre  = self.__pe2cond(plist[0][1])
            whilebody = self.__make_rule_body(plist[0][3])
            return WhileGoal(pre, whilebody, self.aaapl)

    def addRules(self):
        """Add rules to the rulebase"""

        def theaction(strg, loc, tokens):
            """current action"""
            print "\n*** RULES:", len(tokens)

            for rule in tokens:
                res = self.__pe2term(rule[0])
                head = prolog.Term(res[0], res[1])
                guard = self.__pe2cond(list(rule[2]))
                bodyelem = rule[4]
                body = self.__make_rule_body(bodyelem)

                self.aaapl.rulebase.add(Rule(head, guard, body))

                print 'Rule'
                print '\thead \t', head
                print '\tguard\t', guard
                print '\tbody \t', body
        return theaction

####################################################################################

    def parse(self, file):
        """Parser for 3APL files. Parses 3APL syntax according to the official BNF"""

        # Define literals als constants first
      #  begin = Literal("BEGIN")
        true = Literal("TRUE") | 'true()' | 'true'

        digits = "0123456789"
        nonzero = "123456789"
        #numeric = "0" | Combine(Optional("-"), Word(nonzero, digits) )
        numeric = "0" | Combine(Optional("-") + Word(nonzero, digits) )

        lowerchars   = "abcdefghijklmnopqrstuvwxyz"
        upperchars   = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        charsndigits = lowerchars+upperchars+digits

       # allchars = " QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890~!@#$%^&*()-_=+|}{][`:;?.,<>"
       # comment = Group(Combine(Literal('/*') + Optional(Word(allchars, allchars)) + '*/')).setResultsName("comment")

        lowerident = Word(lowerchars, charsndigits)
        upperident = Word(upperchars, charsndigits)
        #identifier = lowerident | upperident
        identifier = Word(alphas, alphas+nums)

        predname = copy(lowerident)
        functionname = copy(lowerident)
        constname = copy(lowerident)
        agentname = copy(lowerident)
        speechact = copy(lowerident)
        varname = copy(upperident)
        bacname = copy(upperident)

        relation = Literal('==') | '<' | '>' | '=' 
        operator = Literal('-') | '+' | '*' | '/'

        par = Forward()
        parlist = delimitedList(par)
        singlepar = numeric | constname | varname | '(' + par + ')'
        iss = 'is' + Optional('(') + parlist + Optional(')')
        functionpar = functionname + '(' + parlist + ')' | singlepar + operator + par
        opr = Group(singlepar + operator + par).setResultsName("opr")
        operation = Group(Optional('(') + singlepar + operator + par + Optional(')')).setResultsName("operation")
        par << Optional(opr | operation | singlepar | functionpar)

        baction = bacname + '(' + parlist + ')'
        rel = Optional('(') + par + relation + par + Optional(')')
        atom = Group(iss | true | predname + '(' + parlist + ')' | rel ).setResultsName("atom")
        atomlist = delimitedList(atom)

        wff = Forward()
        wffBinOp = oneOf('AND OR')
        wffCompound = Group( '(' + wff + ')' ).setResultsName("wffCompound")
        wffNegation = Group( 'NOT' + ( atom | wffCompound ) ).setResultsName("wffNegation")
        wffTerm = Group(atom | wffNegation | wffCompound ).setResultsName("wffTerm")
        wff << Group(wffTerm + ZeroOrMore( wffBinOp + wffTerm )).setResultsName("wff")

        wfflist = Group(delimitedList(wff)).setResultsName("wfflist")

        programheader = Literal('PROGRAM') + '"' + identifier + '"' + Optional('LOAD' + '"' + identifier + '"')

        # Capabilities
        condition = Literal('{') + Optional(wfflist) + '}'
        capability = Group(Group(condition) + Group(baction) + Group(condition)).setResultsName("Capability")
        caplist = delimitedList(capability)
        caplist.setParseAction(self.addCapabilities())
        capsbase = Literal('CAPABILITIES:') + Optional(caplist)

        # Beliefs
        beliefformula = Group(atom + '.' | atom + ':-' + atomlist + '.').setResultsName("Belief")
        belieflist = ZeroOrMore(beliefformula)
        belieflist.setParseAction(self.addBeliefs())
        beliefbase = Literal('BELIEFBASE:') + Optional(belieflist)

        # Goals
        skipgoal = Literal('SKIP').setResultsName("SkipGoal")
        testgoal = (atom + '?' | '(' + wff + ')?').setResultsName("TestGoal")
        vargoal = copy(varname).setResultsName("VarGoal")
      #  predgoal = predname + '(' + parlist + ')?'     # this does not work, BNF or parse error?
        predgoal = (predname + '(' + parlist + ')').setResultsName("PredicateGoal")
      #  functiongoal = (functionname + '(' + parlist + ')').setResultsName("FunctionGoal")   # this is not in BNF, what to do?
        var_num = varname | numeric
        var_agent = varname | agentname
        var_spact = varname | speechact
        var_wff = varname | wff
        baction = (bacname + '(' + parlist + ')').setResultsName("BasicAction")
        methodcall =  (identifier + '()' | identifier + '(' + parlist + ')').setResultsName("MethodCall")
        sendgoal = (Literal('Send') + '(' + var_num + ',' + var_agent + ',' + var_spact + ',' + var_wff + ')').setResultsName("SendGoal")
        javagoal = (Literal('Java') + '(' + '"' + identifier + '"' + ',' + methodcall + ',' + varname + ')').setResultsName("JavaGoal")
        atomicgoal = ( skipgoal | predgoal | baction | sendgoal | testgoal | javagoal | vargoal).setResultsName("AtomicGoal")
        goal = Forward() 
        ifgoal = Group('IF' + wff + 'THEN' + goal + Optional('ELSE' + goal)).setResultsName("IfGoal")   
        whilegoal = Group(Literal('WHILE') + wff + 'DO' + goal).setResultsName("WhileGoal")
        sgoal = Group(whilegoal| ifgoal | atomicgoal)
        sequencegoal = (Literal('BEGIN') + sgoal + Optional(OneOrMore(';' + sgoal)) + 'END').setResultsName("SequenceGoal")
        complexgoal = (sequencegoal| ifgoal | whilegoal).setResultsName("ComplexGoal")      
        goal << Group( complexgoal | atomicgoal )

        goallist = delimitedList(goal)
        goallist.setParseAction(self.addGoals())
        goalbase = Literal('GOALBASE:') + Optional(goallist)

        # Rules
        head = Optional(goal)
        head.setParseAction(self.debugaction("head")).setResultsName("Head")
        guard = Group(copy(wfflist)).setResultsName("Guard") # to include ',' separator, which is ugly and same as AND
        body = Optional(goal).setResultsName("Body")
        rule = Group(head + '<-' + guard + '|' + body)
        rule.setParseAction(self.debugaction("rule"))
        rulelist = delimitedList(rule)
        rulelist.setParseAction(self.addRules())
        rulebase = Literal('RULEBASE:') + Optional(rulelist)
        rulebase.setParseAction(self.debugaction("RULEBASE"))

        program = programheader + capsbase + beliefbase + goalbase + rulebase

        print "\ntest cleaning"
        program.parseFile(file)


class AAAPLBehaviour(Behaviour):
    """Creates needed bases for agent from the parsed syntax"""

    def __init__(self, name='', datastore=None, filename=None, **namedargs):
        self.debug = True   # Select "True", "False" #Xanders debug setting for print statements
        if datastore is None:
            self.datastore = {}
        else:
            self.datastore = datastore
        self.capabilitybase = Capabilitybase()
        self.beliefbase = Beliefbase()
        self.goalbase = Goalbase()
        self.planbase = Planbase()
        self.rulebase = Rulebase()
        self.currentGoal = None
        self.uni = False
        self.cycle = 0
        self.prolog = prolog.Prolog()

        # maybe only the beliefbase needs to be shared, maybe goals, too?
        self.datastore['capabilitybase'] = self.capabilitybase
        self.datastore['beliefbase'] = self.beliefbase
        self.datastore['goalbase'] = self.goalbase
        self.datastore['planbase'] = self.planbase
        self.datastore['rulebase'] = self.rulebase
        parser = Parser(self)
        parser.parse(filename)
        #  self.FSM2 = fsm2            # XANDER NOTE (2)
        super(AAAPLBehaviour, self).__init__(name, **namedargs)

    def action(self):
        """The deliberation cycle !!!!!"""
        self.cycle = self.cycle + 1


        #  self.__update_beliefs_from_environment()       # XANDER NOTE (3) --> Needed for synchronization with FFFSim

        # Select One of the Received Messages
        if self.debug: 
            print "\n", self.cycle, "\t* 1 *\tSelect One of the Received Messages\n"
        message = self.__select_message()

        # Update the beliefs with the Selected Message
        if self.debug: 
            print "\n", self.cycle, "\t* 2 *\tUpdate the beliefs with the Selected Message\n"
        self.__update_beliefs_from_message(message)

        # Update the beliefs with the state of the environment
        if self.debug: 
            print "\n", self.cycle, "\t* 2b *\tUpdate the beliefs with the state of the environment\n"
        self.__update_beliefs_from_environment()

        # Find Practical Reasoning Rules that Matches Goals
        if self.debug: 
            print "\n", self.cycle, "\t* 3 *\tFind Practical Reasoning Rules that Matches Goals\n"
        if self.planbase != None: 
            if len(self.planbase) == 0:        # Check if there are plans, if not, goal is finished and must be removed!
                if self.currentGoal != None:
                    print "******************\n\nWe update the goalbase first !\n"
                    print "Goalbase     -----> ", self.goalbase
                    print "Current Goal -----> ", self.currentGoal
                    for goal in self.goalbase:
                        if str(self.currentGoal) == str(goal):
                            self.goalbase.remove(goal)
                            self.currentGoal = None
                            print "Goal ", goal, "is finished and therefore removed !!\n\n***********************"
                stillplans = 0  
                desired_rules = self.__find_desired_rules()
            else:
                stillplans = 1
                #self.__select_and_execute_plan()
        else: 
            stillplans = 0
            desired_rules = self.__find_desired_rules()

        # Find Practical Reasoning Rules that Matches Beliefs
        # guard/belief
        if self.debug: 
            print "\n", self.cycle, "\t* 4 *\tFind Practical Reasoning Rules that Matches Beliefs\n"
        if stillplans == 0:
            feasible_rules = self.__find_feasible_rules(desired_rules)

        # Select a Practical Reasoning Rule to Apply to a Goal
        if self.debug: 
            print "\n", self.cycle, "\t* 5 *\tSelect a Practical Reasoning Rule to Apply to a Goal\n"
        if stillplans == 0:
            selected_rule = self.__select_rule(feasible_rules)

        # Apply the Practical Reasoning Rule to the Goal
        if self.debug: 
            print "\n", self.cycle, "\t* 6 *\tApply the Practical Reasoning Rule to the Goal\n"
        if stillplans == 0:
            self.__apply_rule(selected_rule)

        # Find Plans To Execute
        if self.debug: 
            print "\n", self.cycle, "\t* 7 *\tFind Plans To Execute\n"
        if stillplans == 0:
            self.__find_plans()

        # Select a Plan To Execute
        if self.debug: 
            print "\n", self.cycle, "\t* 8 *\tSelect a Plan To Execute\n"
        self.__select_and_execute_plan()

        # without goals we can stop thinking
        #if goals is False:
        #    self.set_done()
        if len(self.goalbase) == 0 and len(self.planbase) == 0:
            self.set_done()

    def __parse(self, filename):
        """Read a 3APL file and parse its content to fill the databases for the deliberation cycle"""
        pass

    def __select_message(self):
        """Select one of the received messages"""
        message = None  # receive messages and check queue
        return message

    def __update_beliefs_from_message(self, message):
        """Update the beliefs with the selected message"""
        pass

    def __update_beliefs_from_environment(self):                        # XANDER NOTE (1).
        """Not defined, presumably FSM behaviour"""
        pass
    #     """Update the beliefs with the state of the environment"""
    #     self.FSM2.updateEnv()

    def __find_desired_rules(self):
        """Find practical reasoning rules that matches goals"""

        desired_rules = []
        for rule in self.rulebase:
            print "head", rule.get_head()
#           numbergoals = len(self.goalbase)
            if len(self.goalbase) > 0:
                match = self.prolog.search(rule.get_head(), [self.goalbase[0]], {}) # look at the first goal only
                if self.debug: 
                    print self.prolog.search
                if self.debug: 
                    print "search:", rule.get_head(), self.goalbase[0], match
                self.uni = match
                if match:
                    print "Yes. Found in goals"
                    desired_rules.append(rule)
                    break # will use only first match
        if len(desired_rules) == 0:
            self.goalbase = self.goalbase[1:]   # Goal removed when nothing is desired! Classic 3APL !
            return desired_rules
        else:
            return desired_rules

    def __find_feasible_rules(self, desired_rules):
        """Find practical reasoning rules that matches beliefs"""

        def __check_feasible(rule):
            """Check whether rule is feasible.
               In case variables can not be bound the first time, it will
               try to unify again until.  This process repeats until all
               variables are bound or when unification is no longer possible 
            """
            guard = rule.get_guard()
            head = rule.get_head()
            guarduni = None
            print "***  ", head.pred, head.args
            if len(head.args) > 0 :
                self.uni = self.uni[0]
            else:
                self.uni = {}
            if self.debug: 
                print "guard\t", guard
                print "beliefs\t", self.beliefbase
            result = supertest(self, self.beliefbase, guard, self.uni)
            if result and (type(result[1]) == list) and len(result[1][0]) == 0:
                if self.debug: 
                    print "EMPTY GUARD"
                feasible_rules.append(rule)
                return self.uni  
            elif result and (type(result[1]) == list):
                guarduni = result
                print "Rule", rule.get_head(), "is feasible."
                feasible_rules.append(rule)
                return self.uni
            elif (result and result[1]) or (not result[0] and not result[1]):
                print "Rule", rule.get_head(), "is feasible."
                feasible_rules.append(rule)
                return self.uni
            else:
                print "Rule", rule.get_head(), "is not feasible."     

        feasible_rules = []        
        for rule in desired_rules:
            __check_feasible(rule)

        return feasible_rules

    def __select_rule(self, feasible_rules):
        """Select a practical reasoning rule to apply to a goal"""

        if len(feasible_rules) > 0:
            # select first
            selected_rule = feasible_rules[0]

            # select at random
            # selected_rule = feasible_rules[random(len(feasible_rules))]
        else:
            selected_rule = False

        return selected_rule

    def __apply_rule(self, selected_rule):
        """Apply the practical reasoning rule to the goal"""

        if selected_rule is not False:
            body = selected_rule.get_body()
            if self.debug: 
                print type(body), body
            self.planbase.append(body)
            #self.currentGoal = selected_rule.get_head()
            self.currentGoal = prolog.Rule(selected_rule.get_head())

    def __find_plans(self):
        """Find plan in planbase"""
        print "planbase", len(self.planbase), self.planbase

    def __select_and_execute_plan(self):
        """Take first plan from planbase and execute it"""
        # Select a Plan
        selected_plan = None
        if len(self.planbase) > 0:
            selected_plan = self.planbase[0]
            if self.debug: 
                print 'selected plan:         ', selected_plan

        # Execute the Plan
        if selected_plan:
            #print 'We will now execute:\t', selected_plan
            if type(selected_plan) == AtomicGoal:
                if self.debug: 
                    print selected_plan.pred, selected_plan.args 
            del self.planbase[0]
            selected_plan.execute()
