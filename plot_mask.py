from mayavi import mlab
from surfer import Brain, project_volume_data
import scipy
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import sys
"""
Bring up the visualization window.
"""
#mlab.options.backend = 'envisage'
view = "lateral"
hemi = "split"

#length = str(sys.argv[1])

brain = Brain("fsaverage", hemi, "inflated", title="Temporal ISC",cortex='low_contrast',views=['lat','med'],background="white")

"""
Get a path to the overlay file.
"""
mri_file = '/Users/jamalw/Desktop/PNI/music_event_structures/isc/temporal/tmp_isc_rmap.nii.gz'
reg_file = '/Applications/freesurfer/average/mni152.register.dat'

data = nib.load(mri_file)
minval = 0.05
maxval = np.max(data.get_data()) 

surf_data_lh = project_volume_data(mri_file,"lh",reg_file)
surf_data_rh = project_volume_data(mri_file,"rh",reg_file)

brain.add_overlay(surf_data_lh,min=minval,max=maxval,name="thirty_sec_lh", hemi='lh',sign="pos")
brain.add_overlay(surf_data_rh,min=minval,max=maxval,name="thirty_sec_rh", hemi='rh',sign="pos")
#
#for overlay in brain.overlays_dict["thirty_sec_lh"]:
#    overlay.remove()
#for overlay in brain.overlays_dict["thirty_sec_rh"]:
#    overlay.remove()
#
#brain.add_data(surf_data_lh, minval,maxval, colormap="CMRmap", alpha=1,
#               hemi='lh')
#brain.add_data(surf_data_rh, minval,maxval, colormap="CMRmap", alpha=1,
#               hemi='rh')
#
brain.save_image("isc/plots/temporal_isc.png")
#
mlab.show()

brain.show_view(view)
