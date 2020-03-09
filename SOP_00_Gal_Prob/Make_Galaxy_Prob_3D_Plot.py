#!/usr/bin/python
'''----------------------------------------------------------------
-------------------------------------------------------------------
latest update :  Jordan Wu'''

from __future__ import print_function
import time
import numpy as np
from sys import argv, exit
from os import system, chdir, path
from itertools import combinations
from Hsieh_Functions import *
from Useful_Functions import *

# For non-interactive backend (No request for showing pictures)
import matplotlib
matplotlib.use('Agg')
matplotlib.rc('figure', max_open_warning = 0)
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

if len(argv) != 8:
    exit('\n\tError: Wrong Arguments\
    \n\tExample: [program] [dim] [cube size] [sigma] [bond] [ref-D] [num_slice] [inclination]\
    \n\t[dim]: dimension for smooth (for now only "6")\
    \n\t[cube size]: length of multi-d cube in magnitude unit\
    \n\t[sigma]: standard deviation for gaussian dist. in magnitude\
    \n\t[bond]: boundary radius of gaussian beam unit in cell\
    \n\t[ref-D]: reference dimension which to modulus other dimension to\
    \n\t[deg_slice]: number of slices of position angle\
    \n\t[inclination]: inclination degree of viewing angle')

#=======================================================
# Input variables
band_name  = band_name
dim        = int(argv[1])       # Dimension of position vector
cube       = float(argv[2])     # Beamsize for each cube
sigma      = int(argv[3])       # STD for Gaussian Smooth
bond       = int(argv[4])
refD       = int(argv[5])       # Reference Beam Dimension
deg_slice  = int(argv[6])
incli      = int(argv[7])

shape_dir  = 'GPV_{:d}Dposvec_bin{:.1f}/'.format(dim, cube)
smooth_dir = 'GPV_after_smooth_{:d}D_bin{:.1f}_sigma{:d}_bond{:d}_refD{:d}/'.format(dim, cube, sigma, bond, refD)
output_dir = 'GPV_after_smooth_{:d}D_bin{:.1f}_sigma{:d}_bond{:d}_refD{:d}_GPtomo/'.format(dim, cube, sigma, bond, refD)
all_shape  = np.load(shape_dir + 'Shape.npy')
print('\n', all_shape)

# Check storage directory
if not path.isdir(output_dir):
    system('mkdir {}'.format(output_dir))

#=======================================================
# Functions
def sort_inp_gal(gal_pos, gal_num):
    '''
    sort gal_pos, gal_num and then return list after sorting
    '''
    out_pos, out_num = [], []
    for i in range(len(gal_num)):
        if gal_num[i] >= 1.:
            out_pos.append(gal_pos[i])
            out_num.append(gal_num[i])
    return out_pos, out_num

def plot_3d_scatter(pos_array, num_array, shape, bd_ind, bd_name, sl_num, incli):
    '''
    Plot 2D plot along band 3
    '''
    bd0 = pos_array[:, bd_ind[0]]
    bd1 = pos_array[:, bd_ind[1]]
    bd2 = pos_array[:, bd_ind[2]]

    for i, deg in enumerate(np.linspace(0, 360, sl_num, endpoint=False)):
        drawProgressBar(float(i+1)/sl_num)
        fig = plt.figure(figsize=(12, 8))
        ax  = fig.add_subplot(111, projection='3d')
        ax.scatter(bd0, bd1, bd2, s=0.5, alpha=0.8)
        ax.set_title('{}{}{}_{}'.format(bd_name[0], bd_name[1], bd_name[2], bd_name[0]))
        ax.set_xlabel('{} ({:d})'.format(bd_name[0], shape[0]))
        ax.set_ylabel('{} ({:d})'.format(bd_name[1], shape[1]))
        ax.set_zlabel('{} ({:d})'.format(bd_name[2], shape[2]))
        ax.set_xticks(np.arange(0-0.5, shape[0]+0.5, 1))
        ax.set_yticks(np.arange(0-0.5, shape[1]+0.5, 1))
        ax.set_zticks(np.arange(0-0.5, shape[2]+0.5, 1))
        ax.w_xaxis.set_ticklabels([0])
        ax.w_yaxis.set_ticklabels([0])
        ax.w_zaxis.set_ticklabels([0])
        ax.view_init(incli, deg)
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig('{}{}{}_{:0>3d}'.format(bd_name[0], bd_name[1], bd_name[2], i))
        plt.clf()

#=======================================================
# Main Programs
m_start = time.time()
# Just for debugging test: band_ind_list = np.array([0, 1, 2])
band_ind_list = np.arange(0, dim, 1)
for comb in combinations(band_ind_list, 3):

    #=======================================================
    # Generate band input
    band_ind = ''
    for band in comb:
        band_ind += str(band)
    bd_ind, shape, bd_name = [], [], []
    for ind in band_ind:
        bd_ind.append(int(ind))
        shape.append(all_shape[int(ind)])
        bd_name.append(band_name[int(ind)])
    print('\n# band: ' + band_ind)

    #=======================================================
    # Load galaxy pos/num
    l_start = time.time()
    gal_pos = np.load(smooth_dir + 'after_smooth_lack_{:d}_{}_all_cas_pos.npy'.format(dim-len(band_ind), band_ind))
    gal_num = np.load(smooth_dir + 'after_smooth_lack_{:d}_{}_all_cas_num.npy'.format(dim-len(band_ind), band_ind))
    out_pos, out_num = sort_inp_gal(gal_pos, gal_num)
    pos_array, num_array = np.array(out_pos), np.array(out_num)
    l_end   = time.time()
    #print('Loading took {:.3f} secs'.format(l_end-l_start))

    #=======================================================
    # Start plotting
    p_start = time.time()
    chdir(output_dir)
    tomo_dir = 'tomo_{}/'.format(band_ind)
    if not path.isdir(tomo_dir):
        system('mkdir {}'.format(tomo_dir))
    chdir(tomo_dir)
    all_dir  = 'all_{}_n{:d}_i{:d}/'.format(band_ind, deg_slice, incli)
    if not path.isdir(all_dir):
        system('mkdir {}'.format(all_dir))
    chdir(all_dir)
    plot_3d_scatter(pos_array, num_array, shape, bd_ind, bd_name, deg_slice, incli)
    chdir('../')
    system('convert -delay 100 -loop 0 {}*.png {}_all_{}.gif'.format(all_dir, band_ind, bd_ind[0]))
    chdir('../../')
    p_end   = time.time()
    print('\nPlotting took {:.3f} secs'.format(p_end-p_start))

#=======================================================
m_end   = time.time()
print('\nWhole Process took {:.3f} secs\n'.format(m_end-m_start))