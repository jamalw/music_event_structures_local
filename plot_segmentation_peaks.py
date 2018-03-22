import numpy as np
import matplotlib.pyplot as plt
import csv

#with open('beh_peaks.csv', 'rb') as f:
#    reader = csv.reader(f)
#    data = list(reader)

#data = [list(map(int,rec)) for rec in csv.reader(p, delimiter=',')]

with open('beh_peaks.csv','rb') as f:
    data = [[int(x) for x in 

durs = np.load('songs2Dur.npy')

plt.plot(data[])
