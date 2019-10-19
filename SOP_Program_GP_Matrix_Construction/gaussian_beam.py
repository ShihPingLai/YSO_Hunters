#!/usr/bin/ipython
from pylab import *
from numpy import *
from sys import argv
from os import system, chdir

sigma = 2 # STD for Gaussian Smooth
bond = 7  # Max Smooth Radius
ref = 6.0 # Reference Beam Dimension

# 6band Gaussian Beam for Smooth
six_band_beam = []
for i in range(-bond, 1+bond):
    for j in range(-bond, 1+bond):
        for k in range(-bond, 1+bond):
            for l in range(-bond, 1+bond):
                for m in range(-bond, 1+bond):
                    for n in range(-bond, 1+bond):
                        r_sqa = float(i**2+j**2+k**2+l**2+m**2+n**2)
                        G = exp(-(r_sqa/(2*(sigma*(6.0/ref)**0.5)**2)))
                        if r_sqa <= bond**2:
                            vec = [i, j, k, l, m, n, G]
                            six_band_beam.append(vec)

# 5band Gaussian Beam for Smooth
five_band_beam = []
for i in range(-bond, 1+bond):
   for j in range(-bond, 1+bond):
      for k in range(-bond, 1+bond):
         for l in range(-bond, 1+bond):
            for m in range(-bond, 1+bond):
               r_sqa = float(i**2+j**2+k**2+l**2+m**2)
               G = exp(-(r_sqa/(2*(sigma*(5.0/ref)**0.5)**2)))
               if r_sqa <= bond**2:
                  vec = [i, j, k, l, m, G]
                  five_band_beam.append(vec)

# 4band Gaussian Beam for Smooth
four_band_beam=[]
for i in range(-bond, 1+bond):
   for j in range(-bond, 1+bond):
      for k in range(-bond, 1+bond):
         for l in range(-bond, 1+bond):
            r_sqa = float(i**2+j**2+k**2+l**2)
            G = exp(-(r_sqa/(2*(sigma*(4.0/ref)**0.5)**2)))
            if r_sqa <= bond**2:
                vec = [i,j,k,l,G]
                four_band_beam.append(vec)

# 3band Gaussian Beam for Smooth
three_band_beam=[]
for i in range(-bond, 1+bond):
   for j in range(-bond, 1+bond):
      for k in range(-bond, 1+bond):
            r_sqa = float(i**2+j**2+k**2)
            G = exp(-(r_sqa/(2*(sigma*(3.0/ref)**0.5)**2)))
            if r_sqa <= bond**2:
                vec = [i,j,k,G]
                three_band_beam.append(vec)

# Save Gaussian Beam
system('mkdir GPV_smooth_sigma' + str(sigma))
chdir('GPV_smooth_sigma' + str(sigma))
save('6d_beam_sigma' + str(sigma), six_band_beam)
save('5d_beam_sigma' + str(sigma), five_band_beam)
save('4d_beam_sigma' + str(sigma), four_band_beam)
save('3d_beam_sigma' + str(sigma), three_band_beam)

# Plot Figures
fig0 = []
for i in range(len(six_band_beam)):
    if six_band_beam[i][0] == 0 and six_band_beam[i][1] == 0 and six_band_beam[i][2] == 0 and six_band_beam[i][3] == 0 and six_band_beam[i][4] == 0:
        fig0.append(six_band_beam[i][6])
fig1 = []
for i in range(len(five_band_beam)):
    if five_band_beam[i][0] == 0 and five_band_beam[i][1] == 0 and five_band_beam[i][2] == 0 and five_band_beam[i][3] == 0:
        fig1.append(five_band_beam[i][5])
fig2 = []
for i in range(len(four_band_beam)):
    if four_band_beam[i][0] == 0 and four_band_beam[i][1] == 0 and four_band_beam[i][2] == 0:
        fig2.append(four_band_beam[i][4])
fig3 = []
for i in range(len(three_band_beam)):
    if three_band_beam[i][0] == 0 and three_band_beam[i][1] == 0:
        fig3.append(three_band_beam[i][3])

XX = []
for i in range(-bond, 1+bond):
    XX.append(float(i+0.5))
plot(XX, fig0, ls='steps')
plot(XX, fig1, ls='steps')
plot(XX, fig2, ls='steps')
plot(XX, fig3, ls='steps')
xlabel("cube: cube_size mag")
ylabel("counts")
system('mkdir ND_Beam_sigma' + str(sigma))
chdir('ND_Beam_sigma' + str(sigma))
savefig("Beam_in_diff_dim.png")
