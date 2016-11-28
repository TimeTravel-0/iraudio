#!/usr/bin/env python

import pyaudio
import numpy as np
import time

class irtx:
    def __init__(self):
        return
    def __enter__(self):
        self.p = pyaudio.PyAudio()
        self.max_devs = self.p.get_device_count()
        self.soundcard_num = -0
        for i in range(self.max_devs):
            dataset = self.p.get_device_info_by_index(i)
            print dataset["name"]
            if "front" in dataset["name"]:
                print dataset
                self.soundcard_num = i
        '''       
        for j in range(44100,192000,1):
            try:
                if self.p.is_format_supported(j,  # Sample rate
                                 input_device=self.soundcard_num,
                                 input_channels=1,
                                 input_format=pyaudio.paInt8):
                     print j  
            except:
                continue
                #sleep(0.1)
        '''
        self.fs=96000
        self.stream = self.p.open(format=pyaudio.paInt8,channels=1,rate=self.fs,output=True,output_device_index=self.soundcard_num)
        return self
    def __exit__(self,x,y,z):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        return
        
    def genlevel(self, level, duration):
        num = duration * self.fs
        arr = ""
        for i in range(0,int(num)):
            arr+=chr(level)
        return arr
        
    def genpulse(self,duration):
        num = duration * self.fs
        arr=""
        for i in range(0,int(num)/3):
            arr+=chr(127)+chr(0)+chr(0)
        return arr
    def gensilence(self,duration):
        num = duration * self.fs
        return chr(0)*int(num)
        
    def genfreq(self, freq, duration):
        num = duration * self.fs
        arr = ""
        l = self.fs/freq
        for i in range(0,int(num)):
            lvl=(i%l>=(l/2))*127
            
            #print lvl
            arr+=chr(lvl)
        return arr
        
    def genbitz(self, t1, t2):
        #return self.genfreq(38000,t1)+self.genlevel(0,t2)
        #print t1,t2
        x= self.genpulse(t1)+self.gensilence(t2)
        #print x
        return x
    def genone(self):
        return self.genbitz(self.t_oneon, self.t_oneoff)
    def genzero(self):
        return self.genbitz(self.t_zeroon, self.t_zerooff)
        
    def genbit(self, bit):
        if bit:
            return self.genone()
        return self.genzero()
    def genbyte(self, byte):
        b=byte
        buf=""
        for i in range(0,8):
            q = (b>>i)%2
            buf=self.genbit(q)+buf
        return buf
        
    def genbytes(self, b):
        print "command %x"%b
        ret = ""
        ret+=self.genpulse(self.t_initon)
        ret+=self.gensilence(self.t_initoff)
        bytesa=""
        while b>0:
            bytesa=self.genbyte(b%256)+bytesa
            #print ">>>", b%256
            b=int(b/256)
        return ret+bytesa+self.genpulse(0.01)+self.gensilence(0.01)
        
    def settiming(self,oneon,oneoff,zeroon,zerooff, initon, initoff):
        self.t_oneon=oneon
        self.t_oneoff=oneoff
        self.t_zeroon=zeroon
        self.t_zerooff=zerooff
        
        self.t_initon = initon
        self.t_initoff = initoff
    def play(self, samples):
        self.stream.write(samples)    
        
        
        
from time import sleep

with irtx() as tx:
    a=time.time()
    #tx.settiming(446.0/1000000.0,1269.0/1000000.0,446.0/1000000.0,424.0/1000000.0)
    tx.settiming(446.0/1000000.0,1269.0/1000000.0,446.0/1000000.0,424.0/1000000.0, 3468.0/1000000.0, 1731.0/1000000.0)
    
    code = 0x40040e143c26;
    
    # 40 = 64
    # 04 = 04
    # 0e = 14
    # 14 = 20
    # 3c = 60
    # 26 = 38
    
    tx.play(tx.genbytes(0x40040e143c26)*1)
    sleep(1)
    
    tx.play(tx.genbytes(0x40040e143329)*1)
    sleep(1)
    #tx.play(tx.genbyte(255)*10)
    for i in range(0,30):
        tx.play(tx.genbytes(0x40040e14465c)*1)
        sleep(0.1)
    sleep(1)
    tx.play(tx.genbytes(0x40040e143329)*1)
    sleep(2)
    tx.play(tx.genbytes(0x40040e143c26)*1)
    #tx.genbyte(255)
    #tx.play(tx.genfreq(96000/2,2))
    
    #tx.play(tx.genpulse(2))
    b=time.time()
    print(b-a)
