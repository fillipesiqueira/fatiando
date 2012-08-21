"""
Perform a 2D finite difference simulation of SH wave propagation in a medium
with a discontinuity (i.e., Moho).

The simulation shows that the SH waves get trapped in the top most layer and
that longer periods travel faster.

.. warning:: Can be very slow on old computers!


"""
import time
import numpy as np
import fatiando as ft

log = ft.log.get()

sources = [ft.seis.wavefd.MexHatSource(0, 20, 2, 0.7, delay=1.5)]
shape = (80, 400)
spacing = (1000, 1000)
area = (0, spacing[1]*shape[1], 0, spacing[0]*shape[0])
moho_index = 30
moho = moho_index*spacing[0]
dens = np.ones(shape)
dens[:moho_index,:] *= 2700
dens[moho_index:,:] *= 3100
svel = np.ones(shape)
svel[:moho_index,:] *= 3000
svel[moho_index:,:] *= 6000

dt = 0.05
timesteps = ft.seis.wavefd.elastic_sh(spacing, shape, svel, dens, dt, 4200,
    sources, padding=0.8)

# This part makes an animation by updating the plot every few iterations
ft.vis.ion()
ft.vis.figure(figsize=(10,3))
ft.vis.axis('scaled')
x, z = ft.grd.regular(area, shape)
plot = ft.vis.pcolor(x, z, np.zeros(shape).ravel(), shape,
    vmin=-10**(-7), vmax=10**(-7))
ft.vis.hlines([moho], 0, area[1], 'k', '-')
ft.vis.text(area[1] - 35000, moho - 1000, 'Moho')
ft.vis.text(area[1] - 100000, 15000,
    r'$\rho = %g g/cm^3$ $\beta = %g km/s$' % (2.7, 3))
ft.vis.text(area[1] - 100000, area[-1] - 10000,
    r'$\rho = %g g/cm^3$ $\beta = %g km/s$' % (3.1, 6))
ft.vis.ylim(area[-1], area[-2])
ft.vis.m2km()
ft.vis.xlabel("x (km)")
ft.vis.ylabel("z (km)")
start = time.clock()
for i, u in enumerate(timesteps):
    if i%100 == 0:
        ft.vis.title('time: %0.1f s' % (i*dt))
        plot.set_array(u[0:-1,0:-1].ravel())
        ft.vis.draw()
ft.vis.ioff()
print 'Frames per second (FPS):', float(i)/(time.clock() - start)
ft.vis.show()

# Comment the above and uncomment bellow to save snapshots of the simulation
#ft.vis.figure(figsize=(10,3))
#ft.vis.axis('scaled')
#x, z = ft.grd.regular(area, shape)
#plot = ft.vis.pcolor(x, z, np.zeros(shape).ravel(), shape,
    #vmin=-10**(-7), vmax=10**(-7))
#ft.vis.hlines([moho], 0, area[1], 'k', '-')
#ft.vis.text(area[1] - 35000, moho - 1000, 'Moho')
#ft.vis.text(area[1] - 100000, 15000,
    #r'$\rho = %g g/cm^3$ $\beta = %g km/s$' % (2.7, 3))
#ft.vis.text(area[1] - 100000, area[-1] - 10000,
    #r'$\rho = %g g/cm^3$ $\beta = %g km/s$' % (3.1, 6))
#ft.vis.ylim(area[-1], area[-2])
#ft.vis.m2km()
#ft.vis.xlabel("x (km)")
#ft.vis.ylabel("z (km)")
#for i, u in enumerate(timesteps):
    #if i%10 == 0:
        #ft.vis.title('time: %0.1f s' % (i*dt))
        #plot.set_array(u[0:-1,0:-1].ravel())
        #ft.vis.draw()
        #ft.vis.savefig('frames/f%06d.png' % ((i)/10 + 1), dpi=60)