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
srmK = '30'

#length = str(sys.argv[1])

brain = Brain("fsaverage", hemi, "inflated", title="zstats human bounds (corrected) srm k=" + srmK,cortex='low_contrast',views=['lat','med'],background="white")

"""
Get a path to the overlay file.
"""
mri_file = '/Volumes/scratch/jamalw/HMM_searchlight_K_sweep_srm_bound_match/zstats_map_srmK=' + srmK + '.nii.gz'
reg_file = '/Applications/freesurfer/average/mni152.register.dat'

data = nib.load(mri_file)
minval = 0.2
maxval = np.max(data.get_data()) 

surf_data_lh = project_volume_data(mri_file,"lh",reg_file)
surf_data_rh = project_volume_data(mri_file,"rh",reg_file)

qmri_file = '/Volumes/scratch/jamalw/HMM_searchlight_K_sweep_srm_bound_match/qstats_map_srmK=' + srmK + '.nii.gz'

qdata_lh = project_volume_data(qmri_file,"lh",reg_file)
surf_data_lh[np.logical_or(qdata_lh>0.005,surf_data_lh<0)] = 0

qdata_rh = project_volume_data(qmri_file,"rh",reg_file)
surf_data_rh[np.logical_or(qdata_rh>0.005, surf_data_rh<0)] = 0

brain.add_overlay(surf_data_lh,min=minval,max=maxval,name="thirty_sec_lh", hemi='lh',sign="pos")
brain.add_overlay(surf_data_rh,min=minval,max=maxval,name="thirty_sec_rh", hemi='rh',sign="pos")

brain.save_image("zstats_human_bounds_srm_k" + srmK + ".png")

mlab.show()

brain.show_view(view)
