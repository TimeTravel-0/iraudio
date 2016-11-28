#!/usr/bin/env python

# takes ".csv" export from pulseview
# - comes up with groups of similar pulses
# - extracts symbols without prior knowledge of IR signal
# - (after human-specified symbols) parses symols into data, e.g. binary (and hex)
#
# tested with panasonic camcorder remote, matches lirc capture someone else made down to each bit - great :D


def pulsebin(pd):
    keys = pd.keys()
    keys.sort()
    
    # take length with most occurences
    # find nearby other values up to distance x from each other (10% of pulse length?)
    # if none found in this range start over with next group
    
    groups = []
    
    for i in range(0,len(keys)):
        for j in range(0,len(keys)):
            key_difference = abs(keys[i]-keys[j])
            
            if key_difference<0.1*(keys[i]+keys[j])/2:
                # same group :)
                
                found = False
                for group in groups:
                    for skey in group:
                        #print keys[i], keys[j], skey
                        if keys[i] == skey or keys[j] == skey:
                            # we got a hit!
                            group.append(keys[i])
                            group.append(keys[j])
                            #print "yay"
                            found = True
                            break
                if not found:
                    groups.append([keys[i],keys[j]])
                        
            else:
                # not same group :(
                pass
                
                
    mmgroups = []
    for group in groups:
        mmgroups.append([min(group),max(group)])
                
    #print mmgroups
    
    return mmgroups
    
def findinbins(dur,bins):
    for idx in range(0,len(bins)):
        if dur>=bins[idx][0] and dur<=bins[idx][-1]:
            return idx
            
    

def findsignal(lines):
    idcnt=0
    firstchange=-1
    lastchange=-1
    lastval=False
    for val in lines:
        if val[0]!=";":
            if val != lastval:
                if firstchange==-1:
                    firstchange=idcnt
                lastchange=idcnt
                lastval=val
        else:
            lastval=lines[idcnt+1]
        
        idcnt+=1
        
    #print ">>>>",firstchange, lastchange, len(lines)
        
    return lines[firstchange:lastchange]
        

def findmarkspace(lines):
    lastval=False
    digcnt=0
    lengthsfound_hi = dict()
    lengthsfound_lo = dict()
    sequence = []
    firstedge=True
    for val in lines:
        
        if lastval!=val:
            if firstedge:
                firstedge=False
                digcnt=0
                lastval=val
                continue
            if val[0]=="1":
                sequence.append(["1",digcnt])
                try:
                    lengthsfound_hi[digcnt]+=1
                except:
                    lengthsfound_hi[digcnt]=1
            else:
                sequence.append(["0",digcnt])
                try:
                    lengthsfound_lo[digcnt]+=1
                except:
                    lengthsfound_lo[digcnt]=1
            lastval=val
            digcnt=0
        else:
            digcnt+=1
           
    k_hi = lengthsfound_hi.keys()
    k_hi.sort()
    
    k_lo = lengthsfound_lo.keys()
    k_lo.sort()
    
    
    bins_hi=pulsebin(lengthsfound_hi)
    bins_lo=pulsebin(lengthsfound_lo)
    
    #print sequence
    
    
    symbols = []
    
    for seq in sequence:
        value, duration = seq
        
        if value=="1":
            symbols.append( findinbins(duration, bins_hi) )
        if value=="0":
            symbols.append( -findinbins(duration, bins_lo) )
            
    return symbols
            
        
        
    # longest pulse followed by longes gap is init sequence
    # rest are bit encoded by long and short pulses

def parsesymbols(symbols, symboldict):
    
    # repeatedly check which symbols from symboldict fits the first symbols from "symbols"
    
    returnstring=""
    
    sym = symbols[:]
    done = False
    while not done:
        found = False
        for k in symboldict.keys():
            if symboldict[k] == sym[0:len(symboldict[k])]:
                returnstring+=k
                sym = sym[len(symboldict[k]):]
                found=True
                break
                
        if not found:
            done=True
    
    #print returnstring
    return returnstring
    
    
def bintohex(binstr):
    return hex(int(binstr, 2))


def parsecsv(fn):
    f = open(fn,"r")
    lines = f.readlines()
    f.close()
    
    
    puresignal = findsignal(lines)
    #print puresignal
    
    
    
    symbols = findmarkspace(puresignal)
    
    
    symboldict=dict()
    symboldict[""]=[1,-2]
    symboldict["0"]=[0,0]
    symboldict["1"]=[0,-1]
    
    return parsesymbols(symbols, symboldict)
        
        
if __name__ == "__main__":
    from sys import argv
    for arg in argv[1:]:
        parsed = parsecsv(arg)
        print arg+" "*(40-len(arg))+parsed+" "+bintohex(parsed)
