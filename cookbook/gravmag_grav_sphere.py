"""
GravMag: Forward modeling of the gravity anomaly and the gzz component of the
gravity gradient tensor using spheres (calculate on random points)
"""
from fatiando import mesher, gridder, utils, gravmag
from fatiando.vis import mpl

spheres = [mesher.Sphere(0, 0, 2000, 1000, {'density':1000})]
# Create a set of points at 100m height
area = (-5000, 5000, -5000, 5000)
xp, yp, zp = gridder.scatter(area, 500, z=-100)
# Calculate the anomaly
gz = utils.contaminate(gravmag.sphere.gz(xp, yp, zp, spheres), 0.1)
gzz = utils.contaminate(gravmag.sphere.gzz(xp, yp, zp, spheres), 5.0)
# Plot
shape = (100, 100)
mpl.figure()
mpl.title("gz (mGal)")
mpl.axis('scaled')
mpl.plot(yp*0.001, xp*0.001, '.k')
mpl.contourf(yp*0.001, xp*0.001, gz, shape, 15, interp=True)
mpl.colorbar()
mpl.xlabel('East y (km)')
mpl.ylabel('North x (km)')
mpl.figure()
mpl.title("gzz (Eotvos)")
mpl.axis('scaled')
mpl.plot(yp*0.001, xp*0.001, '.k')
mpl.contourf(yp*0.001, xp*0.001, gzz, shape, 15, interp=True)
mpl.colorbar()
mpl.xlabel('East y (km)')
mpl.ylabel('North x (km)')
mpl.show()
