from mayavi import mlab
from surfer import Brain, project_volume_data
import scipy
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np

"""
Bring up the visualization window.
"""
#mlab.options.backend = 'envisage'
view = "lateral"
hemi = "split"

song_name = 'Waltz_of_Flowers'

brain = Brain("fsaverage", hemi, "inflated", title=song_name,cortex='low_contrast',views=['lat','med'],background="white")

"""
Get a path to the overlay file.
"""
mri_file = '/Users/jamalw/Desktop/PNI/music_event_structures/' + song_name + '/globals_avg_z_n25.nii.gz'
reg_file = '/Applications/freesurfer/average/mni152.register.dat'

data = nib.load(mri_file)
minval = 0.5
maxval = np.max(data.get_data())
#maxval = .027
surf_data_lh = project_volume_data(mri_file,"lh",reg_file)
surf_data_rh = project_volume_data(mri_file,"rh",reg_file)

brain.add_overlay(surf_data_lh,min=minval,max=maxval,name="thirty_sec_lh", hemi='lh',sign="pos")
brain.add_overlay(surf_data_rh,min=minval,max=maxval,name="thirty_sec_rh", hemi='rh',sign="pos")

brain.save_image('/Users/jamalw/Desktop/PNI/music_event_structures/' + song_name + '/avg_z_' + song_name + ".png")

mlab.show()

brain.show_view(view)
