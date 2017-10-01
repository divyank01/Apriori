import itertools as itr

class Rule_Pair:
    rule=None
    head=None
    body=None
    head_str=None
    rule_set_str=None
    def __init__(self,body,head,rule):
        self.rule=rule
        self.head=head
        self.body=body
        self.head_str=','.join(a for a in head)
        self.rule_set_str=','.join(a for a in rule)

def __rule_str(s,l,item,isBody,isHead,cond=None):
    if item is None:
        if not isBody and not isHead:
            if len(s) < cond:
                return None
        comb=set(l)
        if isBody and len(comb)<cond:
            return None        
        body = ''
        diff=s.difference(comb)
        comb=list(comb)
        comb.sort()
        body=body+','.join(a for a in comb)
        
        if isHead and len(diff)<cond:
            return None
        head=''
        diff=list(diff)
        diff.sort()
        head=head+','.join(a for a in diff)
        return ('{'+body+'}->{'+head+'}',body+','+head,body,Rule_Pair(frozenset(comb),frozenset(diff),frozenset(s)))
    elif cond is None:
        comb=set(l)
        if isBody and len(item.intersection(comb))==0:
            return None        
        body = ''
        diff=s.difference(comb)
        comb=list(comb)
        comb.sort()
        body=body+','.join(a for a in comb)
        
        if isHead and len(item.intersection(diff))==0:
            return None
        head=''
        diff=list(diff)
        diff.sort()
        head=head+','.join(a for a in diff)
        return ('{'+body+'}->{'+head+'}',body+','+head,body,Rule_Pair(body=frozenset(comb),head=frozenset(diff),rule=frozenset(s)))
    elif cond == 'NONE':
        comb=set(l)
        if isBody and len(item.intersection(comb))>0:
            return None        
        body = ''
        diff=s.difference(comb)
        comb=list(comb)
        comb.sort()
        body=body+','.join(a for a in comb)
        
        if isHead and len(item.intersection(diff))>0:
            return None
        head=''
        diff=list(diff)
        diff.sort()
        head=head+','.join(a for a in diff)
        return ('{'+body+'}->{'+head+'}',body+','+head,body,Rule_Pair(body=frozenset(comb),head=frozenset(diff),rule=frozenset(s)))
        

def make_rules(s,item,isBody,isHead,cond=None):
    retVal=set()
    for i in range(1,len(s)):
        for comb in itr.combinations(s,i):
            rule=__rule_str(s,comb,item,isBody,isHead,cond)
            if rule is not None:
                retVal.add(rule)
    return retVal

def __make_rule_str(comb,s):
    s=set(s)
    diff=s.difference(comb)
    rp=Rule_Pair(body=frozenset(comb),head=frozenset(diff),rule=frozenset(s))
    body=','.join(a for a in comb)
    head=','.join(a for a in diff)
    return ('{'+body+'}->{'+head+'}',rp)

def make_all_rules(l):
    retVal=dict()
    for key in l:
        s=set(key.split('-'))
        for i in range(1,len(s)):
            for comb in itr.combinations(s,i):
                val=__make_rule_str(comb,s)
                retVal[val[0]]=val[1]
    return retVal
