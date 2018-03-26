import numpy as np
import nibabel as nib
from scipy import stats
from surfer import Brain, project_volume_data
from mayavi import mlab
import matplotlib.pyplot as plt

view = "lateral"
hemi = "split"

songs = np.array(['St_Pauls_Suite','I_Love_Music','Moonlight_Sonata','Change_of_the_Guard','Waltz_of_Flowers','The_Bird','Island','Allegro_Moderato','Finlandia','Early_Summer','Capriccio_Espagnole','Symphony_Fantastique','Boogie_Stop_Shuffle','My_Favorite_Things','Blue_Monk','All_Blues'])

nii_template = nib.load('/Users/jamalw/Desktop/PNI/music_event_structures/trans_filtered_func_data.nii')
datadir = '/Users/jamalw/Desktop/PNI/music_event_structures/'

zvals = np.arange(0.05,.25,.01)
#zvals = [0.05]

for s in range(len(songs)):
    for z in zvals: 
        # load,zscore,then store each dataset for each K in a list
        k_data = np.zeros((91,109,91,14))
        z_data = np.zeros((91,109,91,14))
        thresh = np.zeros((91,109,91))
        maxval_per_maxK = np.zeros((91,109,91,14)) 

        for i in range(3,17):
            data = nib.load(datadir + songs[s] + '/globals_avg_real_n25_k' + str(i) + '.npy').get_data()
            load_z = nib.load(datadir + songs[s] + '/globals_avg_z_n25_k' + str(i) + '.npy').get_data()
            k_data[:,:,:,i-3] = data
            z_data[:,:,:,i-3] = load_z 

        max_K = np.argmax(k_data,axis=3) + 3
        max_K[np.sum(k_data, axis=3) == 0] = 0       
 
        for i in range(91):
            for j in range(109):
                for k in range(91):
                    thresh[i,j,k] = z_data[i,j,k,max_K[i,j,k]-3]

        max_K[thresh < z] = 0
        max_K = max_K.astype(float)
    
        # save final map as nifti
        maxval = np.max(max_K)
        minval = np.min(max_K)
        img = nib.Nifti1Image(max_K,affine = nii_template.affine)
        img.header['cal_min'] = minval
        img.header['cal_max'] = maxval
        nib.save(img, datadir + songs[s] +  '/best_k_map_z' + str(z) + '.nii.gz')

        brain = Brain("fsaverage", hemi, "inflated", title= songs[s] + ' Z='+str(z),cortex='low_contrast',views=['lat','med'],background="white")

        """
        Get a path to the overlay file.
        """
        mri_file = '/Users/jamalw/Desktop/PNI/music_event_structures/' + songs[s] + '/best_k_map_z' + str(z) + '.nii.gz'
        reg_file = '/Applications/freesurfer/average/mni152.register.dat'

        data = nib.load(mri_file)
        minval = 0
        maxval = np.max(data.get_data())

        surf_data_lh = project_volume_data(mri_file,"lh",reg_file)
        surf_data_rh = project_volume_data(mri_file,"rh",reg_file)

        brain.add_overlay(surf_data_lh,min=minval,max=maxval,name="thirty_sec_lh", hemi='lh')
        brain.add_overlay(surf_data_rh,min=minval,max=maxval,name="thirty_sec_rh", hemi='rh')

        for overlay in brain.overlays_dict["thirty_sec_lh"]:
            overlay.remove()
        for overlay in brain.overlays_dict["thirty_sec_rh"]:
            overlay.remove()

        brain.add_data(surf_data_lh, 0,maxval, colormap="rainbow", alpha=.65,
                   hemi='lh')
        brain.add_data(surf_data_rh, 0,maxval, colormap="rainbow", alpha=.65,
                   hemi='rh')

        brain.save_image(datadir + songs[s] + '/plots/avg_raw_zthresh_' + str(z) + ".png")
    
#mlab.show()   
 
#brain.show_view(view)
