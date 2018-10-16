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

brain = Brain("fsaverage", hemi, "inflated", title="zstats human bound match fit to all subjs (corrected)",cortex='low_contrast',views=['lat','med'],background="white")

"""
Get a path to the overlay file.
"""
mri_file = '/Volumes/norman/jamalw/MES/prototype/link/scripts/data/searchlight_output/HMM_searchlight_human_bounds_fit_to_all/ttest_results/zstats_map_both_runs.nii.gz'
reg_file = '/Applications/freesurfer/average/mni152.register.dat'

data = nib.load(mri_file)
minval = 0.1
maxval = np.max(data.get_data()) 

surf_data_lh = project_volume_data(mri_file,"lh",reg_file)
surf_data_rh = project_volume_data(mri_file,"rh",reg_file)

qmri_file = '/Volumes/norman/jamalw/MES/prototype/link/scripts/data/searchlight_output/HMM_searchlight_human_bounds_fit_to_all/ttest_results/qstats_map_both_runs.nii.gz'

qdata_lh = project_volume_data(qmri_file,"lh",reg_file)
surf_data_lh[np.logical_or(qdata_lh>0.005,surf_data_lh<0)] = 0

qdata_rh = project_volume_data(qmri_file,"rh",reg_file)
surf_data_rh[np.logical_or(qdata_rh>0.005, surf_data_rh<0)] = 0

brain.add_overlay(surf_data_lh,min=minval,max=maxval,name="thirty_sec_lh", hemi='lh',sign="pos")
brain.add_overlay(surf_data_rh,min=minval,max=maxval,name="thirty_sec_rh", hemi='rh',sign="pos")

brain.save_image("human_bounds_match_plots/zstats_ttest_both_runs.png")

mlab.show()

brain.show_view(view)
