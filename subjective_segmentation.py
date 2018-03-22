## Imports
from psychopy import prefs, sound, visual, event, core, gui, data
from psychopy.hardware.emulator import launchScan
prefs.general['audioLib'] = ['pygame']
import glob, time, random, os, csv

## Session settings
subj_id = 'SS_030218_0'

os.system("mkdir '/Users/jamalw/Desktop/PNI/music_event_structures/subjects/beh/'" + subj_id)
subject_filename = '/Users/jamalw/Desktop/PNI/music_event_structures/subjects/beh/' + subj_id + '/' + subj_id + '_' + 'subjective_segmentation.log'
csv_filename = '/Users/jamalw/Desktop/PNI/music_event_structures/subjects/beh/' + subj_id + '/' + subj_id + '_' + 'subjective_segmentation.csv'

## Static settings
MR_settings = {
    'TR': 1.000,     # duration (sec) per whole-brain volume
    'volumes': 8000,    # number of whole-brain 3D volumes per scanning run
    'sync': '5', # character to use as the sync timing event; assumed to come at start of a volume
    'skip': 0,       # number of volumes lacking a sync pulse at start of scan (for T1 stabilization)
    'sound': False    # in test mode: play a tone as a reminder of scanner noise
    }
duration = MR_settings['volumes'] * MR_settings['TR']

## Prepare log files
csv_file = open(csv_filename,'a')
csv_dw = csv.DictWriter(csv_file, fieldnames=['timestamp','event_type','info'])
csv_dw.writeheader()

## Functions
def log_msg(msg, filename=subject_filename):
    print(msg)
    with open(filename, 'a') as f:
        f.write(msg + '\n')

def log_csv(timestamp, event_type, info=""):
    timestamp = '{:0.20f}'.format(timestamp)
    event_type = str(event_type)
    info = str(info)
    d = dict(timestamp=timestamp, event_type=event_type, info=info)
    csv_dw.writerow(d)
    csv_file.flush()

## Prepare music
songs = glob.glob('/Users/jamalw/Desktop/PNI/music_event_structures/songs/*.wav')
random.shuffle(songs)

## Prepare prompts
with open('/Users/jamalw/Desktop/PNI/music_event_structures/prompts/Subjective_Segmentation_instructions.txt','r') as f:
    file_contents = f.read()
with open('/Users/jamalw/Desktop/PNI/music_event_structures/prompts/song_break.txt','r') as song_break_file:
    song_break_text = song_break_file.read()

## Main loop variables
song_idx = 0 # index of current song in `songs` list
current_state = 'begin' # begin / song / gap / end
current_song = None

## -- Main experiment begins here -- ##
log_msg('Log filename:' + subject_filename)

## User-selections GUI
infoDlg = gui.DlgFromDict(MR_settings, title='fMRI parameters', order=['TR', 'volumes'])
if not infoDlg.OK:
    core.quit()

## Launch main window & clock
win = visual.Window(fullscr=True)
main_label = visual.TextStim(win, height=.15, pos=(0, 0), color=win.rgb + 0.5)
main_label.size = 10
main_label.setText("+")
main_label.draw()
globalClock = core.Clock()
win.flip()

## Launch MRI (operator selects Scan or Test [emulate]; see API docuwmentation)
vol = launchScan(win, MR_settings, globalClock=globalClock,simResponses=None,mode=None,esc_key='escape',instr=file_contents)
# wait for first MRI sync event
while not event.getKeys(MR_settings['sync']):
    time.sleep(0.001)
onset = globalClock.getTime()
vol += 1
log_msg(u"%3d  %7.3f sync\n" % (vol, onset))

## Main loop
while globalClock.getTime() < duration:
    
    # retrieve and log key presses
    all_keys = event.getKeys()
    ts = globalClock.getTime()
    for key in all_keys:
        if key == MR_settings['sync']:
            log_csv(ts, 'sync')
            log_msg(u"%3d  %7.3f sync\n" % (vol, ts))
            vol += 1
        else:
            log_csv(ts, 'button_press', unicode(key))
            log_msg(u"%3d  %7.3f %s\n" % (vol-1, globalClock.getTime(), unicode(key)))
            if key == 'escape':
                log_msg(u'user cancel')
                current_state = 'end'
                break

    if current_state == 'end':
        break

    elif current_state == 'begin':
        current_song = sound.Sound(os.path.join(songs[song_idx]))
        current_song.play() 
        log_csv(ts,'song start',songs[song_idx])
        main_label.setText('+')
        main_label.draw()
        win.flip()
        current_state = 'song'

    elif current_state == 'song':
        if current_song.status == -1: # if song stopped playing
            log_csv(ts,'song end',songs[song_idx])
            # convert to state 'gap':
            current_state = 'gap'
            main_label.setText(song_break_text)
            main_label.draw()
            win.flip()

    elif current_state == 'gap':
        
        # if at last song, move to end state
        if song_idx+1 == len(songs):
            current_state = 'end'
            break
        
        if 'p' in all_keys:

            # advance from 'gap' to 'song' state
            song_idx += 1
            
            current_state = 'song'
            current_song = sound.Sound(os.path.join(songs[song_idx]))
            current_song.play() 
            log_csv(ts,'song start',songs[song_idx])
            main_label.setText('+')
            main_label.draw()
            win.flip()

## End experiment
# display end message
main_label.setText('This concludes the scanning session.')
main_label.draw()
win.flip()
# log end message
t = globalClock.getTime()
log_msg("End of scan (vol 0..%d = %d of %s). Total duration = %7.3f sec" % (vol - 1, vol, MR_settings['volumes'], t))
time.sleep(5)
# close files
csv_file.close()
win.close()
core.quit()
log_msg("Log file saved to: " + subject_filename)
