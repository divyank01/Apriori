import itertools as itr
import sys
import rule_process as rule
import linecache

#################################################################################
#                                                                               #
#                          Apriori Implementation                               #
#                                                                               #
#################################################################################

class Apriori:
    rows=list()
    total_txn=0
    table = dict()
    minSup=0
    n_freq_set=set()
    minConf=0
    ki=set()
    '''
        Calcuate the support for the item
    '''
    def __get_support(self,item):
        return (float(len(self.table[item]))/self.total_txn)*100
    
    def __confidence(self,rule,head):
        rule=list(rule.split(','))
        rule.sort()
        head=list(head.split(','))
        head.sort()
        rule=('-'.join(e for e in rule))
        head=('-'.join(e for e in head))
        if rule in self.table:
            return (float(len(self.table[rule]))/len(self.table[head]))*100
        else:
            return None

    '''
        Calcuate the support for the item count
    '''
    def __support(self,counts):
        return (float(counts)/self.total_txn)*100

    '''
        Read file and setup the dictionary for singular set keys.
    '''
    def __setup(self,file_loc):
        file = open(file_loc,'r')
        for line in file:
            count=0
            row=list()
            cols=line.split('\t')
            for s in cols:
                count+=1
                if count <= len(cols)-1:
                    row.append('G'+str(count)+'_'+s)
                    self.ki.add('G'+str(count)+'_'+s)
            self.rows.append(row)
            self.total_txn+=1
        count=1
        for row in self.rows:        
            for item in row:
                if count <= len(self.rows):
                    if not self.table.has_key(item):
                        doc_ids=set()
                        doc_ids.add(count)
                        self.table[item]=doc_ids
                    else:
                        if count not in self.table[item]:
                            self.table[item].add(count)
            count+=1
        file.close()
        print(len(self.table))

    '''
        prune singular keys and forward the keys for candidate generation.
    '''
    def __create_candidates(self,minSup):
        for key in self.table.keys():
            if self.__get_support(key)>=minSup:
                b=None
            else:
                self.table.pop(key)
        self.__get_candidates(minSup,self.table.keys()[:])

    '''
        Get combinations for frequent item sets
    '''
    def __combo(self,sets,keys):
        new_set=set()
        for item in keys:
            for s in sets:
                s_cpy=set(s.split('-'))
                s_cpy.add(item);
                l=list(s_cpy)
                string=self.__toStr(l)
                if string not in self.n_freq_set:
                    intersection=self.__intersection(s_cpy)
                    support=self.__support(len(intersection))
                    if support>=self.minSup:
                        new_set.add(string)
                    else:
                        self.n_freq_set.add(string)
                    del intersection
                del s_cpy
                del l
        return sets.union(new_set)
    
    '''
        generate candiates
    '''
    def __get_candidates(self,minSup,f_list):
        s_keys=set(f_list[:])
        com=self.__combo(set(self.table.keys()),s_keys)
        initial=len(self.table)
        while True:
            l=list(com)
            for k in l:
                if k not in self.table:
                    lst=k.split('-') 
                    self.table[k]=self.__intersection(lst)
            del l
            keys=set(self.table.keys())
            com=self.__combo(keys,s_keys)
            b=len(com)
            if initial==len(self.table) or len(keys.union(com))==len(keys):
                break
            initial=len(self.table)
    
    '''
        list to required string representation
    '''
    def __toStr(self,lst):
        lst.sort()
        retval='-'.join(a for a in lst)
        del lst
        return retval 
    '''
        get desired union of all keys in set
    '''
    def __union(self,seq):
        s=set()
        for a in seq:
            b=set(self.table[a])
            s=s.union(b)
        return s

    '''
        get desired intersection 
    '''
    def __intersection(self,seq):
        s=set()
        for a in seq:
            b=set(self.table[a])
            if len(s)==0:
                s=s.union(b)
            else:
                if len(s.intersection(b))==0:
                    return set()
                else:
                    s=s.intersection(b)
        return s

    def __is_freq(self,item):
        return self.__support(item)>=self.minSup;
    '''
        init apriori and setup
    '''
    def __init__(self,file_loc,minSup,minConf):
        self.minSup=minSup
        self.minConf=minConf
        self.__setup(file_loc)
        self.__create_candidates(minSup)

    '''
        filter results based on confidence
    '''
    def filter_conf(self,retVal,a):
        string,r,body,out=a
        if self.__confidence(r,body)>self.minConf:
            retVal.add((string,out))

    '''
        process params
    '''
    def __process_params(self,items,isBody,isHead,cond=None):
        keys=self.table.keys()
        items=set(items)
        retVal=set()
        for key in keys:
            s=set(key.split('-'))
            if cond == 'NONE' and not isBody and not isHead:
                if len(items.intersection(s))==0:
                    for a in rule.make_rules(s,items,isBody,isHead,cond):
                        self.filter_conf(retVal,a)    
            elif cond != 'NONE':
                if cond == 'ANY':
                    if len(s.intersection(items))>0:
                        for a in rule.make_rules(s,items,isBody,isHead,None):
                            self.filter_conf(retVal,a)
                else:
                    if len(items.intersection(s))>0:
                        for a in rule.make_rules(s,items,isBody,isHead):
                            self.filter_conf(retVal,a)
            elif cond == 'NONE':
                for a in rule.make_rules(s,items,isBody,isHead,cond):
                    self.filter_conf(retVal,a)
            elif cond is None:
                if len(items.intersection(s))>0:
                    for a in rule.make_rules(s,items,isBody,isHead,cond):
                        self.filter_conf(retVal,a)
        return retVal


    '''
        generate results for template 2
    '''
    def template2(self,part,count):
        keys=self.table.keys()
        retVal=set()
        for key in keys:
            s=set(key.split('-'))
            if part == 'HEAD':
                for r in rule.make_rules(s,None,False,True,count):
                    self.filter_conf(retVal,r)
            if part == 'BODY':
                for r in rule.make_rules(s,None,True,False,count):
                    self.filter_conf(retVal,r)
            if part == 'RULE':
                for r in rule.make_rules(s,None,False,False,count):
                    self.filter_conf(retVal,r)
        return self.__extract_set(retVal)

    '''
        generate results for template 3
    '''
    def template3(self,op,t11=None,t12=None,t13=None,t21=None,t22=None,t23=None):
        try:
            if op == '1or1':
                return self.template1(t11,t12,t13).union(self.template1(t21,t22,t23))
            if op == '1and1':
                return self.template1(t11,t12,t13).intersection(self.template1(t21,t22,t23))
            if op == '1or2':
                return self.template1(t11,t12,t13).union(self.template2(t21,t22))
            if op == '1and2':
                return self.template1(t11,t12,t13).intersection(self.template2(t21,t22))
            if op == '2and2':
                return self.template2(t11,t12).intersection(self.template2(t21,t22))
            if op == '2or2':
                return self.template2(t11,t12).union(self.template2(t21,t22))
        except Exception as ex:
            PrintException()

    '''
        generate results for template 1
    '''
    def template1(self,part,cond,items):
        try:
            if not isinstance(cond,int):
                if cond == 'ANY':
                    if part == 'BODY':
                        return self.__extract_set(self.__process_params(items,True,False,cond))
                    elif part == 'RULE':
                        return self.__extract_set(self.__process_params(items,False,False,cond))
                    elif part == 'HEAD':
                        return self.__extract_set(self.__process_params(items,False,True,cond))
                elif cond == 'NONE':
                    if part == 'BODY':
                        return self.__extract_set(self.__process_params(items,True,False,cond))
                    elif part == 'RULE':
                        return self.__extract_set(self.__process_params(items,False,False,cond))
                    elif part == 'HEAD':
                        return self.__extract_set(self.__process_params(items,False,True,cond))
            elif isinstance(cond,int):
                if part == 'BODY':
                    s=set()
                    for item in items:
                        l=list()
                        l.append(item)
                        rules=self.__process_params(l,True,False)
                        for i in rules:
                            if len(i[1].body.intersection(set(items)))==cond:
                                s.add(i[0])
                    return s
                elif part == 'RULE':
                    s=set()
                    for item in items:
                        l=list()
                        l.append(item)
                        rules=self.__process_params(l,False,False)
                        for i in rules:
                            if len(i[1].rule.intersection(set(items)))==cond:
                                s.add(i[0])
                    return s
                elif part == 'HEAD':
                    s=set()
                    for item in items:
                        l=list()
                        l.append(item)
                        rules=self.__process_params(l,False,True)
                        for i in rules:
                            if len(i[1].head.intersection(set(items)))==cond:
                                s.add(i[0])
                    return s
        except Exception as ex:
            PrintException()
    
    def __filter_1(self,s,diff):
        ret=set()
        for i in s:
            for j in diff:
                if i.find(j) < 0:
                    ret.add(j)
        return ret
    
    def __extract_set(self,s):
        ret=set()
        for i in s:
            ret.add(i[0])
        return ret


    '''
        output results for template 1
    '''
    def handle_t1(self,arr,asso,file,query):
        try:
            print('printing queries for template 1'+str(arr))
            result=asso.template1(arr[0],arr[1],arr[2].split(','))
            file.write('QUERY: '+query+'\n')
            file.write('Total number of rules generated is:'+str(len(result))+'\n')
            for out in result:
                file.write(out+'\n')
            file.write('\n========================================================================================\n')   
        except Exception as ex:
            print(str(ex)+'+')
            PrintException()
    
    '''
        output results for template 2
    '''
    def handle_t2(self,arr,asso,file,query):
        try:
            print('printing queries for template 2'+str(arr))
            result=asso.template2(arr[0],int(arr[1]))
            file.write('QUERY: '+query+'\n')
            file.write('Total number of rules generated is:'+str(len(result))+'\n')
            for out in result:
                file.write(out+'\n')
            file.write('\n========================================================================================\n')   
        except Exception as ex:
            print(str(ex)+'*')
            PrintException()
    
    '''
        output results for template 3
    '''
    def handle_t3(self,arr,asso,file,query):
        try:
            print('printing queries for template 3'+str(arr))
            result=[]
            if arr[0] == '1or1' or arr[0] == '1and1':
                result=asso.template3(op=arr[0],t11=arr[1],t12=arr[2],t13=arr[3].split(','),t21=arr[4],t22=arr[5],t23=arr[6].split(','))
            if arr[0] == '1or2' or arr[0] == '1and2':
                result=asso.template3(op=arr[0],t11=arr[1],t12=arr[2],t13=arr[3].split(','),t21=arr[4],t22=arr[5])
            if arr[0] == '2or2' or arr[0] == '2and2':
                result=asso.template3(op=arr[0],t11=arr[1],t12=arr[2],t21=arr[3],t22=arr[4])
            file.write('QUERY: '+query+'\n')
            file.write('Total number of rules generated is:'+str(len(result))+'\n')
            for out in result:
                file.write(out+'\n')
            file.write('\n========================================================================================\n')   
        except Exception as ex:
            print(str(ex)+'#')
            PrintException()
            raise ex
            PrintException()

    '''
        output freq itemsets given support and confidence
    '''
    def output_freq_itemsets(self,file):
        keys=self.table.keys()
        out=dict()
        for key in keys:
            a=len(key.split('-'))
            if a in out:
                out[a]=out[a]+1
            else:
                out[a]=1
        ks=out.keys()
        ks.sort()
        file.write('=========================================RESULTS=========================================\n')
        file.write('Support:'+str(self.minSup)+'%\n')
        file.write('Confidence:'+str(self.minConf)+'%\n\n')
        for k in ks:
            file.write('Number of length-'+str(k)+' frequent itemsets: '+str(out[k])+'\n')
        file.write('Total frequent sets:'+str(len(keys))+'\n')
        file.write('========================================================================================\n')
        print(out)
####################################################################################################################

###########################     GLOBALS     ########################################################################

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('{}, LINE {} "{}": {}'.format(filename, lineno, line.strip(), exc_obj))

def do_arr(arr):
    for i in range(0,len(arr)):
        try:
            ret=int(arr[i])
            arr[i]=ret
        except ValueError:
            arr[i]=arr[i].replace('\n','')
            continue


def main(arr):
    q_file=open(arr[5],'r')
    o_file=open(arr[6],'w')
    asso=Apriori(arr[7],int(arr[2]),int(arr[4]))
    asso.output_freq_itemsets(o_file)

    try:
        for query in q_file:
            params=query.split('-')
            do_arr(params)
            if params[0] is not '#':
                if params[0] == 't1':
                    asso.handle_t1(params[1:],asso,o_file,query)
                if params[0] == 't2':
                    asso.handle_t2(params[1:],asso,o_file,query)
                if params[0] == 't3':
                    asso.handle_t3(params[1:],asso,o_file,query)


    #############################testing####################
        #print(asso.template2('BODY',1)).intersection(asso.template2('HEAD',2))
    except Exception as ex:
        print(ex)
        PrintException()
    q_file.close()
    o_file.close()

####################################    MAIN    #################################################
if __name__ == '__main__':
    if len(sys.argv)<=7:
        print('*******************************ERROR***************************************\n')
        print('Usage: python apriori.py -s 50 -c 70 input_query.txt output_rules.txt data.txt\n')
    else:
        try:
            main(sys.argv)
        except Exception as ex:
            print(ex)