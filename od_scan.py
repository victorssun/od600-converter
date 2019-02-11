# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 01:55:58 2018

@author: A
"""
# OD spectrometer
# how do you know it is calibrated?
# for input, do not press enter twice
# for first turn on computer, add 2nd arg to init spec
# blank should be ~11k for 600 nm 
# -0 means its unf

import numpy as np
import pandas as pd
import time, struct, math, serial, sys
import matplotlib.pyplot as plt
#from pandas.tools.plotting import table
from pandas.plotting import table

def initSpec():
    spec = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)
    spec.write('a\n')
    spec.write('K0\n')
    print spec.readlines()
    spec.close()
    spec2 = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
    spec2.write('a\n')
    print spec2.readlines()
    spec.close()
    print('spec init done.')

def px2nm(pixel):
    pixels = np.arange(1,2049)
    a = -2.7726e-08
    b = 4.6758e-07
    c = 0.58435
    d = 172.35
    nm = a*pixels**3. + b*pixels**2. + c*pixels + d
    nm_specifc = nm[pixel]
    return nm_specifc, nm

def plotSpec(nm, data, ifsave=False, savefig_title='default'):
    fig = plt.figure()
    ax = fig.add_subplot(111)	
    ax.set_ylim(0, 1.1*max(data)) # square?	
    ax.set_xlim(180, 1130)
    ax.set_xlabel('wavelength / nm')
    ax.plot(nm, data)
    if ifsave == True:
        plt.savefig(savefig_title + '.png')
        np.savetxt(savefig_title + '.txt', np.array([nm, data]).T)
    return

def acquireData(spec, integration, averages):
    # acquire data
    spec.write('S\n') # idk
    read_byte = spec.read(9) # ?
    print('acquiring...')
    time.sleep(integration * averages/1000.) # acquiring...
    data = []
    # get first data point
    try:
        read_byte = spec.read(1)
        raw = read_byte.encode('hex') # ?
        raw = struct.unpack('>b', raw.decode('hex'))[0] # ?
    except struct.error:
        read_byte = spec.read(2)
        raw = read_byte.encode('hex') # ?
        raw = struct.unpack('>H', raw.decode('hex'))[0] # ?
    data.append(raw) # why
    
    # get the rest of data
    for p in range(2047): # why 2047 when background is 2048
        read_byte = spec.read(1)
        raw = read_byte.encode('hex')
        raw = struct.unpack('>b', raw.decode('hex'))[0]
        if abs(raw) == 128: # ?
            read_byte = spec.read(2)
            value = read_byte.encode('hex')
            value = struct.unpack('>H', value.decode('hex'))[0]
            # what is this?
            if value < 0:
                print "value" + '   ' + str(value)
                print "hex" + '   ' + str(read_byte.encode('hex'))
        else:
            value = data[-1] + raw
        data.append(value)  
    #print data # print spec
    data[0] = data[1] #Otherwise bg1 is zero - can't fix it easily?
    return data

def selectPx(data, bg, px_select):
    data_cor = data[px_select] - bg[px_select]
    intensity_cor = float(data_cor) # intensity 
    intensity_uncor = float(data[px_select]) # intensity without bg correct
    return intensity_cor, intensity_uncor


### MAIN CODE ###
if len(sys.argv) == 2:
    initSpec()
# init
averages = 30 # 25
iterations = 1  # 3
integration = 1000 # 1000
#px_select = 752 - 1 # 600; 903, 680; 660, 550
px_select = [751, 752, 550, 549] # 599.46, 600.00, 550.06, 549.51

spec = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
print('readlines...')
print(spec.readlines()) # ?
spec.write('b\n') # idk
print(spec.readlines()) # ?
spec.write('I%d\n' % integration) # set integration
print(spec.readlines()) # ?
spec.write('A%d\n' % averages) # set averages
print(spec.readlines()) # ?
#spec.write('S\n') # idk
time.sleep(1)

# bg
raw_input('taking bg, turn off light... ENTER INPUT')
#read_byte = spec.read(9) # ?
#time.sleep(integration * averages/1000. + 1) # acquiring...
bg1 = acquireData(spec, integration, averages)
#plotSpec(nm, )


'''
# get first data point
try:
    read_byte = spec.read(1)
    raw = read_byte.encode('hex') # ?
    raw = struct.unpack('>b', raw.decode('hex'))[0] # ?
except struct.error:
    read_byte = spec.read(2)
    raw = read_byte.encode('hex') # ?
    raw = struct.unpack('>H', raw.decode('hex'))[0] # ?
bg1.append(raw) # why

# get the rest of data
for p in range(2047): # why 2047 when background is 2048
    read_byte = spec.read(1)
    raw = read_byte.encode('hex')
    raw = struct.unpack('>b', raw.decode('hex'))[0]
    if abs(raw) == 128: # ?
        read_byte = spec.read(2)
        value = read_byte.encode('hex')
        value = struct.unpack('>H', value.decode('hex'))[0]
        # what is this?
        if value < 0:
            print "value" + '   ' + str(value)
            print "hex" + '   ' + str(read_byte.encode('hex'))
    else:
        value = bg1[-1] + raw
    bg1.append(value)  
print bg1 # print spec
bg1[0] = bg1[1] #Otherwise bg1 is zero - can't fix it easily?
'''

od_df = pd.DataFrame()
od_df_unsub = pd.DataFrame()
for i in range(iterations):
    # grab blank
    raw_input('taking blank, turn on light/put in blank... ENTER INPUT')
    blank1 = acquireData(spec, integration, averages)
    blank_cor_list = []
    blank_uncor_list = []
    wl_list = []
    for px in px_select:
        wl_list.append(round(px2nm(px)[0], 3)) # grab wl for column naming
        blank_cor, blank_uncor = selectPx(blank1, bg1, px)
	print('Blank: ' + str(round(blank_cor, 3)))
	#print('Blank: ' + str(round(blank_uncor, 3)))
        blank_cor_list.append(blank_cor)
        blank_uncor_list.append(blank_uncor)
    
    # grab data
    raw_input('taking sample, place sample... PRESS ENTER')
    data1 = acquireData(spec, integration, averages)
    sample_cor_list = []
    sample_uncor_list = []
    for px in px_select:    
        sample_cor, sample_uncor = selectPx(data1, bg1, px)
        sample_cor_list.append(sample_cor)
        sample_uncor_list.append(sample_uncor)        
    
    # determine 
    trial_list = []
    trial_list_unsub = []
    for j in range(len(sample_cor_list)):
	try:
            od_value = 2 - math.log10(sample_cor_list[j] / blank_cor_list[j] * 100)
	except:
	    od_value = -0.000
        print 'OD600 = ' + str(od_value)
	try:
            unsub = math.log10(blank_uncor_list[j] / sample_uncor_list[j])
	except:
	    unsub = -0.000
        print 'Unsub OD600 is ' + str(unsub)
        trial_list.append(od_value)
        trial_list_unsub.append(unsub)
    od_df = od_df.append([trial_list], ignore_index=True)
    od_df_unsub = od_df_unsub.append([trial_list_unsub], ignore_index=True)
    od_df = od_df.round(2)
    od_df_unsub = od_df_unsub.round(2)
od_df.columns = wl_list
od_df_unsub.columns = wl_list

#od_df = pd.DataFrame()
#for j in range(3):
#    test = []
#    for i in range(3):
#        test.append(i)
#    od_df = od_df.append([test], ignore_index=True)
#od_df.columns = [121, 122, 123] # input wl_list
#od_df_unsub = od_df
nm_range = px2nm(0)[1]
plotSpec(nm_range, data1)

fig = plt.figure()
ax = fig.add_subplot(211, frame_on=False)
ax2 = fig.add_subplot(212, frame_on=False)
ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)
ax.set_title('OD - bg subtracted')
ax2.xaxis.set_visible(False)
ax2.yaxis.set_visible(False)
ax2.set_title('OD - no bg sub')
#ax.table(cellText=test_df)
table(ax, od_df, loc='center')
table(ax2, od_df_unsub, loc='center')
plt.show()

#data1_cor = data1 - bg1
#int_sample = float(data1_cor[px_select]) # blank intensity 
#unSubSampleT = float(data1[px_select]) # blank intensity without bg correct

# determine od
#T = 2 - math.log10(sampleT / blankT * 100)
#TP = T * 100
#od_value = 2 - math.log10(TP)
#unSubOD600 = math.log10(unSubBlankT/unSubSampleT)
#print 'Unsub OD600 is ' + str(unSubOD600) 
#print 'OD600 = ' + str(od_value)





#background = np.zeros(2048) # ?
#bg = zeros(2048) # ?

#blank = []
#sample = []
#blankT = 0
#sampleT = 0
#od_intensity = 0.00

#unSubOD600 = 0.00
#unSubBlankT = 0.00
#unSubSampleT = 0.00


spec.close()
