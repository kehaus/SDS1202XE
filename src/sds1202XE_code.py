#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 11:57:18 2020

@author: kh
"""



import visa
import matplotlib.pyplot as plt
import numpy as np

import json

# ======
# auxiliary functions
# ======

CHANNELS = [
    'c1',
    'c2',
    'math',
]

# ======
# auxiliary functions
# ======
class SDS1000Exception():
    """ """
    pass

def _check_channel_format(channel):
    """ """
    if channel not in CHANNELS:
        raise SDS1000Exception("channel value {} not valid.".format(channel))
    return

def save_wf(t, v, fn='test.json'):
    dct = {
        'time': t,
        'volt': v
    }
    with open(fn, 'w') as outfile:
        json.dump(dct, outfile,  indent=4, sort_keys=True)
    return
    
    
def load_wf(fn='test.json'):
    with open(fn, 'r') as outfile:
        data = json.load(outfile)
    return data['time'], data['volt']
    
def save_to_json(fn, data):
    print('here33')
    # serialized numpy.ndarrays
    for key, val in data.items():
        if type(val) == np.ndarray:
            data[key] = list(val)        
    
    with open(fn, 'w') as outfile:
        json.dump(data, outfile,  indent=4, sort_keys=True)
    return

def load_from_json(fn='test.json'):
    with open(fn, 'r') as outfile:
        data = json.load(outfile)
    return data


# ======
# hardware communication
# ======

def get_waveform(channel, do_plot=False):
    _check_channel_format(channel)
    
    _rm = visa.ResourceManager()
    sds = _rm.open_resource("USB0::0xF4ED::0xEE3A::SDS1ECDX2R3290::INSTR")
    sds.write("chdr off")
    vdiv = sds.query("c1:vdiv?")
    ofst = sds.query("c1:ofst?")
    tdiv = sds.query("tdiv?")
    sara = sds.query("sara?")
    sara_unit = {'G':1E9,'M':1E6,'k':1E3}
    for unit in sara_unit.keys():
        if sara.find(unit)!=-1:
            sara = sara.split(unit)
            sara = float(sara[0])*sara_unit[unit]
            break
    sara = float(sara)
    sds.timeout = 30000 #default value is 2000(2s)
    sds.chunk_size = 20*1024*1024 #default value is 20*1024(20k bytes)
#    sds.write("c1:wf? dat2")
    sds.write(channel+":wf? dat2")
    recv = list(sds.read_raw())[15:]
    recv.pop()
    recv.pop()
    volt_value = []
    for data in recv:
        if data > 127:
            data = data - 255
        else:
            pass
        volt_value.append(data)
    
    time_value = []
    for idx in range(0,len(volt_value)):
        volt_value[idx] = volt_value[idx]/25*float(vdiv)-float(ofst)
        time_data = -(float(tdiv)*14/2)+idx*(1/sara)
        time_value.append(time_data)
    
    if do_plot:
        plt.figure(figsize=(7,5))
        plt.plot(time_value,volt_value,markersize=2,label=u"Y-T")
        plt.legend()
        plt.grid()
        plt.show()
    
    return time_value, volt_value

def read_values(raw_vals):
    
    recv = list(raw_vals)[15:]
    recv.pop()
    recv.pop()
    volt_vals = []
    for data_point in recv:
        if data_point > 127:
            data_point = data_point - 255
        else:
            pass
        volt_vals.append(data_point)
    return volt_vals



def get_both_waveforms():    
    _rm = visa.ResourceManager()
    sds = _rm.open_resource("USB0::0xF4ED::0xEE3A::SDS1ECDX2R3290::INSTR")
    sds.write("chdr off")
    vdiv1 = sds.query("c1:vdiv?")
    ofst1 = sds.query("c1:ofst?")
    vdiv2 = sds.query("c2:vdiv?")
    ofst2 = sds.query("c2:ofst?")
    tdiv = sds.query("tdiv?")
    sara = sds.query("sara?")
    sara_unit = {'G':1E9,'M':1E6,'k':1E3}
    for unit in sara_unit.keys():
        if sara.find(unit)!=-1:
            sara = sara.split(unit)
            sara = float(sara[0])*sara_unit[unit]
            break
    sara = float(sara)
    sds.timeout = 30000 #default value is 2000(2s)
    sds.chunk_size = 20*1024*1024 #default value is 20*1024(20k bytes)

    # ==================
    # get data channel 1
    # ==================
    sds.write("c1:wf? dat2")
    recv1 = list(sds.read_raw())[15:]
    recv1.pop()
    recv1.pop()
    volt_value1 = []
    for data in recv1:
        if data > 127:
            data = data - 255
        else:
            pass
        volt_value1.append(data)
    
    time_value1 = []
    for idx in range(0,len(volt_value1)):
        volt_value1[idx] = volt_value1[idx]/25*float(vdiv1)-float(ofst1)
        time_data1 = -(float(tdiv)*14/2)+idx*(1/sara)
        time_value1.append(time_data1)
    
    # ==================
    # get data channel 2
    # ==================
    sds.write("c2:wf? dat2")
    recv2 = list(sds.read_raw())[15:]
    recv2.pop()
    recv2.pop()
    volt_value2= []
    for data in recv2:
        if data > 127:
            data = data - 255
        else:
            pass
        volt_value2.append(data)
    
    time_value2 = []
    for idx in range(0,len(volt_value2)):
        volt_value2[idx] = volt_value2[idx]/25*float(vdiv2)-float(ofst2)
        time_data2 = -(float(tdiv)*14/2)+idx*(1/sara)
        time_value2.append(time_data2)
    
#    if do_plot:
#        plt.figure(figsize=(7,5))
#        plt.plot(time_value,volt_value,markersize=2,label=u"Y-T")
#        plt.legend()
#        plt.grid()
#        plt.show()
    
    return time_value1, volt_value1, time_value2, volt_value2

    

print('hereerere')
    
if __name__=='__main__':
#    t1, v1 = get_waveform('c1')
#    t2, v2 = get_waveform('c2')
#    
#    plt.figure()
#    plt.plot(t1, v1)
#    plt.plot(t2, v2)
#    plt.grid()
#    plt.show()
#    
#    save_wf(t1, v1, '20-07-02_ch1_wf0.json')
#    save_wf(t2, v2, '20-07-02_ch2_wf0.json')

    pass