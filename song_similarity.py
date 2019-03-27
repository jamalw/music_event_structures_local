import numpy as np
from scipy.signal import spectrogram
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import glob
from scipy import stats
from pydub import AudioSegment
from scipy.fftpack import dct
import matplotlib.animation as animation
from scipy.io import wavfile
from numpy import array
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout


datadir = '/Users/jamalw/Desktop/PNI/music_event_structures/'
genres = ["classical","jazz"]
classical_fn = glob.glob(datadir + genres[0] + '/*.wav')
jazz_fn = glob.glob(datadir + genres[1] + '/*.wav')
all_songs_fn = classical_fn + jazz_fn
#all_songs_fn = ['/Users/jamalw/Desktop/PNI/music_event_structures/classical/St. - Pauls-1.wav']
#song = 'I Love Music'

spects = []
audio_array_holder = []
spects_cut = []
mfccs = []

# load data
FFMPEG_BIN = "ffmpeg"

for j in range(len(all_songs_fn)):
#    raw_audio = AudioSegment.from_wav(all_songs_fn[j]).raw_data
#    
#    # convert raw_audio to audio arrays
#    audio_array = np.fromstring(raw_audio, dtype="int16")
#    audio_array = audio_array.reshape((int(len(audio_array)/2),2))
#    audio_array_holder.append(audio_array)    
#
#    # combine channels
#    audio_array = (audio_array[:,0] * audio_array[:,1])/2
    rate, audio = wavfile.read(all_songs_fn[j])
    audio_array = np.mean(audio, axis=1)
    print('computing spectrogram')
    f,t,spect = spectrogram(audio_array,44100)
    spects.append(spect)
    print('spectrogram computed')

    w = np.round(spect.shape[1]/(len(audio_array)/44100))
    output = np.zeros((spect.shape[0],int(np.round((t.shape[0]/w)))))
    forward_idx = np.arange(0,len(t) + 1,w)
    num_ceps = 10

    for i in range(len(forward_idx)):
        if spect[:,int(forward_idx[i]):int(forward_idx[i])+int(w)].shape[1] != w:
            continue  
        else: 
            output[:,i] = np.mean(spect[:,int(forward_idx[i]):int(forward_idx[i])+int(w)],axis=1).T

    # compute similarity matrix for spectrogram
    spect_corr = np.corrcoef(output.T,output.T)[output.shape[1]:,:output.shape[1]]

    # compute similarity matrix for mfcc
    mfcc = dct(output.T, type=2,axis=1,norm='ortho')[:,1:(num_ceps + 1)]
    (nframes, ncoeff) = mfcc.shape
    n = np.arange(ncoeff)
    cep_lifter = 12
    lift = 1 + (cep_lifter / 2) * np.sin(np.pi * n / cep_lifter)
    mfcc *= lift
    mfcc_corr = np.corrcoef(mfcc,mfcc)[mfcc.shape[0]:,:mfcc.shape[0]]

    # compute normalized mfcc similarity matrix
    mfcc_norm = mfcc
    mfcc_norm -= (np.mean(mfcc_norm,axis=0) + 1e-8)
    mfccs.append(mfcc_norm)
    mfcc_norm_corr = np.corrcoef(mfcc_norm,mfcc_norm)[mfcc_norm.shape[0]:,:mfcc_norm.shape[0]]

for i in range(len(mfccs)):
    mfccs[i] = mfccs[i][0:89]

# create training and testing set
train_classical = np.concatenate(mfccs[0:6],axis=0)
train_jazz = np.concatenate(mfccs[8:14],axis=0)

x_train = np.vstack((train_classical,train_jazz))
y_train = np.append(np.zeros(train_classical.shape[0]),np.ones(train_jazz.shape[0]))

test_classical = np.concatenate(mfccs[6:8],axis=0)
test_jazz = np.concatenate(mfccs[14:16],axis=0)

x_test = np.vstack((test_classical,test_jazz))
y_test = np.append(np.zeros(test_classical.shape[0]),np.ones(test_jazz.shape[0]))

model = Sequential()
model.add(Dense(64, input_dim=10, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(1, activation='sigmoid'))

model.compile(loss='binary_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

model.fit(x_train, y_train,
          epochs=20,
          batch_size=128)
score = model.evaluate(x_test, y_test, batch_size=128)

#mfcc_data = array(mfccs)
#np.save('mfcc_test',mfcc_data)

plt.figure(1)
plt.imshow(spect_corr)
plt.colorbar()
plt.title('Spectral Similarity',fontsize=18)
#plt.savefig('plots/' + song + '_spectrogram')


plt.figure(2)
plt.imshow(mfcc_corr)
plt.colorbar()
plt.title('MFCC Similarity',fontsize=18)
#plt.savefig('plots/' + song + '_mfcc')

plt.figure(3)
plt.imshow(mfcc_norm_corr)
plt.colorbar()
plt.title('Norm-MFCC Similarity',fontsize=18)
#plt.savefig('plots/' + song + '_mfcc_norm')


#spects_mean = np.vstack([np.mean(i,1) for i in spects])
#spects_corr = np.corrcoef(spects_mean,spects_mean)[16:,:16]
#
#plt.imshow(spects_corr) 
#plt.colorbar()
#plt.show()
#
## compute average section of avgCorrD
#corr_eye = np.identity(8)
#classical_within  = spects_corr[0:8,0:8]
#classical_within_off  = classical_within[corr_eye == 0]
#jazz_within       = spects_corr[8:16,8:16]
#jazz_within_off       = jazz_within[corr_eye == 0]
#classJazz_between = spects_corr[8:16,0:8]
#classJazz_between_off = classJazz_between[corr_eye == 0]
#jazzClass_between = spects_corr[0:8,8:16]
#jazzClass_between_off = jazzClass_between[corr_eye == 0]
#
#within = (classical_within + jazz_within)/2
#between = (jazzClass_between + classJazz_between)/2
# 
#plt.figure(2,facecolor="1")
#allComparisonsAvg = np.array([np.mean(within),np.mean(between)])
#allComparisonsSem = np.array([stats.sem(np.reshape(within,(8*8))),stats.sem(np.reshape(between,8*8))])
#N = 2
#ind = np.arange(N)
#width = 0.5
#plt.bar(ind, allComparisonsAvg, width, color='k',yerr = allComparisonsSem,error_kw=dict(ecolor='lightseagreen',lw=3,capsize=0,capthick=0))
#plt.ylabel('Pattern Similarity (r)',fontsize=15)
#plt.title('Average Within and Between-Genre Similarity',fontweight='bold',fontsize=18)
#labels = ['Within','Between']
#plt.xticks(ind + width / 10,labels,fontsize=12)
#plt.plot((0.5,1),(0,0),'k-')
#plt.show()
