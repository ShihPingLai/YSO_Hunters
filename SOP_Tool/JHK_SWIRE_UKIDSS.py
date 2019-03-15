#!/usr/bin/ipython
'''-------------------------------------------------------------------------------------
This program is to replace old 2MASS J,H,K mag with new UKIDSS Jw, Hw, Kw mag
Input : (1)SWIRE catalog to be replaced
        (2)UKIDSS catalog to replace
        (3)Output catalog filename

Output: (1)New catalog with UKIDSS J, H, K band magnitude and error

*NOTE: 
    1. empty column on SWIRE format catalog for storing magnitude
       (1) magnitude: J[35] H[56] K[77]
       (2) mag_err: J[36], H[57], K[78]
    2. if a 2MASS object is found more than one source in UKIDSS catalog,
       only the last source in catalog will take into consideration.
---------------------------------------------------------------------------------------
latest update : 2019/03/15 Jordan Wu'''

from sys import argv, exit
import numpy as np
import time

if len(argv) != 4:
    exit('Wrong Input Argument!\
        \nExample: python [program] [Swire] [UKIDSS] [output file name]\
        \nNote: Replace [Swire] J,H,K with [UKIDSS]')
else:
    print('\nStart input check ...')

data1 = open(str(argv[1]), 'r')
two_mass_cat = data1.readlines()
data1.close()

data2 = open(str(argv[2]), 'r')
UK_cat_origin = data2.readlines()[14:]
data2.close()

if len(two_mass_cat) < len(UK_cat_origin):
    t_start = time.time()
    UK_cat = [UK_cat_origin[0]]
    for i in range(len(UK_cat_origin)-1):
        col_1 = UK_cat_origin[i].split()
        col_2 = UK_cat_origin[i+1].split()
        UK_cat.append(UK_cat_origin[i+1])
        if col_1[1] == col_2[1]:
            UK_cat.remove(UK_cat_origin[i])
    t_end = time.time()
    print('\nDealing with repeated sources in catalog took %.6f secs ...' % (t_end - t_start))
    print('\nNR in new UKIDSS ELAIS N1 catalog: %i' % len(UK_cat))

    Output = open(str(argv[2])+'_reduction', 'w')
    for row in UK_cat:
        Output.write(str(row))
    Output.close()
    
    # Save and Reload catalog corrected
    data1 = open(str(argv[1]), 'r')
    data2 = open(str(argv[2])+'_reduction', 'r')
    swire = np.array(data1.readlines())
    ukidss = np.array(data2.readlines())
    data1.close(); data2.close();
else:
    swire = np.array(two_mass_cat)
    ukidss = np.array(UK_cat_origin)

print('\nStart replacing ...\n')
t_start = time.time()
swire_ra = []
for row in swire:
    swire_ra.append(row.split()[0])
swire_ra = np.array(swire_ra)

for i in range(len(ukidss)):
    row_u = ukidss[i]
    ra = row_u.split()[1]
    ra = ra.strip(',')
    ra = ra.strip('+')
    mag_J, mag_H, mag_K = row_u[10].strip(','), row_u[12].strip(','), row_u[14].strip(',')
    err_J, err_H, err_K = row_u[11].strip(','), row_u[13].strip(','), row_u[15].strip(',')
    index = int(np.where(swire_ra == ra)[0][0])
    row = swire[index]
    row_s = row.split()
    row_s[35], row_s[56], row_s[77] = mag_J, mag_H, mag_K
    row_s[36], row_s[57], row_s[78] = err_J, err_H, err_K
    swire[index] = '\t'.join(row_s)
    
    # Percentage Indicator
    if i>100 and i%100==0: 
        print('%.6f' % (float(i)/float(len(ukidss))) + '%') 

t_end = time.time()
print('\nReplace procedure took %.6f secs ...' % (t_end - t_start))

Output = open(str(argv[3]), 'w')
for ls in Out_catalog:
    row = '\t'.join(list(ls))
    Output.write(row + '\n')
Output.close()
