""" Utilityfunctions to be used with aaapl.py

    This utility uses several small procedures (combined into one) 
    to unify 3APL (Prolog) statements against a 3APL base.
"""

__revision__ = '$Id: aaaplutils.py,v 1.2 2006/04/06 09:36:18 bvdvecht Exp $'

from copy import copy
    
def has_value(dictionary, val):
    """ Checks wether a certain value is in a dictionairy """ 
    if val in dictionary.values(): 
        return True
    else: return False
    

def walkover(self, dic, whattotest, somebase, envi):
    """ Tries to unify NONE values in a unification dictionairy. 
        This function uses prolog.py for testing.
        None values can arrise when mathmatical terms are found which
        can not be evaluated the first time (temporarily value is set to NONE)
    """
    
    print "DEBUG CHECKWALKOVER:\t\t", envi
    envi = dic
    walkoverleft = len(envi.keys())
    while walkoverleft != 0: 
        if None in envi.values():
            envi.update(envi)
            walkoverleft = envi.values().count(None)
            if self.aaapl.debug: 
                print "WE STILL HAVE ......................     ", 
                print walkoverleft, " POSSIBILITIES LEFT"
            newresult = whattotest.test(somebase, envi)
            if newresult and type(newresult[1]) == list:
                envi.update(newresult[1][0])
            else:
                envi = False
                return envi
        else:
            newresult = whattotest.test(somebase, envi)
            if newresult and (type(newresult[1]) == list):
                envi = newresult[1][0]
                return envi
            else:
                envi = False
                return envi            


def make_group(somebase):
    """ Procedure to group duplicate predicates in a list.
        Using this grouping we can compute needed permuations later 
    """ 
        
    somebase, somelist = copy(somebase), []
    while len(somebase) > 0:
        temp, counter, belief = [], 0, somebase.pop(0)
        temp.append(belief)
        while counter < len(somebase):
            if somebase[counter].head.pred == belief.head.pred: 
                temp.append(somebase.pop(counter))
            else: counter += 1
        if len(temp) > 1: 
            somelist.append(temp)
    return somelist

    
    
def perm_the_base(self, somebase, whattocheck):
    """ Procedure initializes and starts the permutation process """
        
    def gen_comb(self, ind): 
        """ Computes needed permutations of grouping. Using early matching 
            (lazy evaluation) a permutation is crested and tested. 
            If still no result is found, the next permuation is created. 
        """ 
    
        if ind == max_n: 
            perm = [somelist[i][ind_lst[i]] for i in range(max_n)]
            for forgottenitem in somebase:
                if forgottenitem not in perm:
                    perm.append(forgottenitem)
            envi = {}
            val = whattocheck.test(perm, envi) # check using prolog.py
            if val == None: 
                return False
            elif type(val[1]) == list: 
                return val, perm
            else: 
                return False
             
        for ofs in range(max_list[ind]): 
            ind_lst[ind] = ofs  
            newcomb = gen_comb(self, ind+1)
            if newcomb: 
                return newcomb
        return False
        
        
    # Start making grouping
    somelist = make_group(somebase)
    
    # Prepare for permutation procedure
    max_n = len(somelist) 
    ind_lst = [0 for i in range(max_n)] 
    max_list = [len(somelist[i]) for i in range (max_n)]        
    
    # Start permuation procedure
    checkuni = gen_comb(self, 0)
    if checkuni == False: 
        return False, False
    else: return checkuni
    
    
def supertest(self, somebase, whattocheck, envi):
    """ Entire procedure for testing, using alternatives when needed """
    
    res = whattocheck.test(somebase, envi)
    if res and type(res[1]) == list:        
        for dics in res[1]:
            if has_value(dics, None): 
                new_dic = walkover(self, dics, whattocheck, somebase, envi)
                dics = new_dic
                return res
            else: return res
    elif res[0] is True and res[1] is True:
        return res
    else:
        #if self.aaapl.debug: 
        #    print "\n-------------------------------------------------------------"
        #    print "- *** First possibility failed! Checking alternatives! **** -"
        #    print "-------------------------------------------------------------\n"
        res, perm = perm_the_base(self, somebase, whattocheck)
        if res and type(res[1]) == list:
            for dics in res[1]:
                if has_value(dics, None): 
                    new_dic = walkover(self, res[1], whattocheck, perm, dics)  
                    dics = new_dic
                    return new_dic
                else:
                    return res
        else: return (True, False)
