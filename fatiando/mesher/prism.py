# Copyright 2010 The Fatiando a Terra Development Team
#
# This file is part of Fatiando a Terra.
#
# Fatiando a Terra is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Fatiando a Terra is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Fatiando a Terra.  If not, see <http://www.gnu.org/licenses/>.
"""
Create and operate on meshes of right rectangular prisms
"""
__author__ = 'Leonardo Uieda (leouieda@gmail.com)'
__date__ = '13-Sep-2010'

import numpy
import matplotlib.mlab

from fatiando import logger

log = logger.dummy()

_allowed_keys = ('x1', 'x2', 'y1', 'y2', 'z1', 'z2', 'density')


def Prism3D(x1, x2, y1, y2, z1, z2, density=0):
    """
    Create a 3D right rectangular prism.

    Parameters:
    * x1, x2
        South and north borders of the prism
    * y1, y2
        West and east borders of the prism
    * z1, z2
        Bottom and top of the prism
    * density
        Density value assigned to the prism
    Returns:
    * prism
        Dictionary describing the prism

    """
    prism = {'x1':x1, 'x2':x2, 'y1':y1, 'y2':y2, 'z1':z1, 'z2':z2,
             'density':density}
    return prism


def Relief3D(x, y, z, shape, zref):
    """
    Create a 3D relief discretized using prisms.
    Use to generate:
    * topographic model
    * basin model
    * Moho model

    The mesh is dictionary with keys:
    * 'cells': a list of Prism3D
    * 'shape': (1,ny,nx).
    * 'size': ny*nx.

    Parameters:
    * x, y, z
        Arrays with the x, y and z coordinates of the relief. Must be a regular
        grid!
    * shape
        Shape of the regular grid, ie (ny, nx).
    * zref
        Reference level. Prisms will have: bottom on zref and top on z if
        z > zref; bottom on z and top on zref otherwise.
    Returns:
    * mesh

    """
    mesh = {}


def Mesh3D(x1, x2, y1, y2, z1, z2, shape):
    """
    Dived a volume into right rectangular prisms.

    The mesh is dictionary with keys:
    * 'cells': a list of Prism3D
    * 'shape': (nz,ny,nx).
    * 'size': nz*ny*nx.
    * 'volume': (x1,x2,y1,y2,z1,z2).

    Parameters:
    * x1, x2
        Lower and upper limits of the volume in the x direction
    * y1, y2
        Lower and upper limits of the volume in the y direction
    * z1, z2
        Lower and upper limits of the volume in the z direction
    * shape
        Number of prisms in the x, y, and z directions, ie (nz, ny, nx)
    Returns:
    * mesh

    """
    log.info("Generating 3D right rectangular prism mesh:")
    nz, ny, nx = shape
    size = nx*ny*nz
    dx = float(x2 - x1)/nx
    dy = float(y2 - y1)/ny
    dz = float(z2 - z1)/nz
    log.info("  shape = (nz, ny, nx) = %s" % (str(shape)))
    log.info("  number of prisms = %d" % (size))
    log.info("  prism dimensions = (dz, dy, dx) = %s" % (str((dz, dy, dx))))
    mesh = {'shape':shape, 'volume':(x1,x2,y1,y2,z1,z2), 'size':size,
            'cells':[None]*size}
    c = 0
    for k, cellz1 in enumerate(numpy.arange(z1, z2, dz)):
        # To ensure that there are the right number of cells. arange
        # sometimes makes more cells because of floating point rounding
        if k >= nz:
            break
        for j, celly1 in enumerate(numpy.arange(y1, y2, dy)):
            if j >= ny:
                break
            for i, cellx1 in enumerate(numpy.arange(x1, x2, dx)):
                if i >= nx:
                    break
                mesh['cells'][c] = Prism3D(cellx1, cellx1 + dx, celly1,
                                           celly1 + dy, cellz1, cellz1 + dz)
                c += 1
    return mesh


def flagtopo(mesh, x, y, height):
    """
    Flag prisms from a 3D prism mesh that are above the topography.
    Also flags prisms outside of the topography grid (not directly under).
    The topography height information does not need to be on a regular grid.

    Flags by replacing Prism3D objects in mesh['cells'] with None.

    Parameters:
    * mesh
        A 3D prism mesh. See :func:`fatiando.mesher.prism_mesh3D`
    * x, y
        Arrays with x and y coordinates of the grid points
    * height
        Array with the height of the topography
    Returns:
    * New filtered mesh

    """
    nz, ny, nx = mesh['shape']
    x1, x2, y1, y2, z1, z2 = mesh['volume']
    size = mesh['size']
    dx = float(x2 - x1)/nx
    dy = float(y2 - y1)/ny
    dz = float(z2 - z1)/nz
    # The coordinates of the centers of the cells
    xc = numpy.arange(x1, x2, dx) + 0.5*dx
    if len(xc) > nx:
        x = x[:-1]
    yc = numpy.arange(y1, y2, dy) + 0.5*dy
    if len(yc) > ny:
        y = y[:-1]
    X, Y = numpy.meshgrid(xc, yc)
    # -1 if to transform height into z coordinate
    topo = -1*matplotlib.mlab.griddata(x, y, height, X, Y).ravel()
    # griddata returns a masked array. If the interpolated point is out of
    # of the data range, mask will be True. Use this to remove all cells
    # bellow a masked topo point (ie, one with no height information)
    if numpy.ma.isMA(topo):
        topo_mask = topo.mask
    else:
        topo_mask = [False]*len(topo)
    flagged = mesh.copy()
    flagged['cells'] = [None]*mesh['size']
    c = 0
    for layer in numpy.reshape(mesh['cells'], mesh['shape']):
        for cell, h, mask in zip(layer.ravel(), topo, topo_mask) :
            if 0.5*(cell['z1'] + cell['z2']) >=  h and not mask:
                flagged['cells'][c] = cell.copy()
                c += 1
    return flagged


def fill(values, key, mesh):
    """
    Fill the ``key`` of each prism of mesh with given values

    Will ignore the value corresponding to a prism flagged as None
    (see :func:`fatiando.mesher.prism.flagtopo`)

    Parameters:
    * values
        1D array with the value of each prism
    * key
        Key to fill in the *mesh*
    * mesh
        Mesh to fill
    Returns:
    * filled mesh

    """
    if key not in _allowed_keys:
        msg = "Invalid key: %s. Must be one of: %s" % (key, _allowed_keys)
        raise ValueError, msg
    def filledprism(p, v):
        if p is None:
            return None
        fp = p.copy()
        fp[key] = v
        return fp
    filled = mesh.copy()
    filled['cells'] = [filledprism(p,v) for v, p in zip(values, mesh['cells'])]
    return filled


def extract(key, mesh):
    """
    Extract the values of a key from each prism in the mesh

    Parameters:
    * key
        string representing the key whose value will be extracted.
        Should be one of the arguments to the Prism3D function.
    * mesh
        A Mesh3D.
    Returns:
    * Array with the extracted values

    """
    if key not in _allowed_keys:
        msg = "Invalid key: %s. Must be one of: %s" % (key, _allowed_keys)
        raise ValueError, msg
    def getkey(p):
        if p is None:
            return None
        return p[key]
    res = numpy.array([getkey(p) for p in mesh['cells']])
    return res


def copy(mesh):
    """
    Make a copy of mesh.

    Parameters:
    * mesh
        Mesh to copy
    Returns:
    * A copy of mesh

    """
    copied = mesh.copy()
    def copyprism(p):
        if p is None:
            return None
        return p.copy()
    copied['cells'] = [copyprism(p) for p in mesh['cells']]
    return copied


def vfilter(mesh, vmin, vmax, key):
    """
    Return prism from mesh with a key that lies within a given range.

    Parameters:
    * mesh
        A given mesh, can be any
    * vmin
        Minimum value
    * vmax
        Maximum value
    * key
        The key of the prisms whose value will be used to filter
    Returns:
    * filtered mesh. NOTE: will not have the 'shape' or 'volume' keys!

    """
    if key not in _allowed_keys:
        msg = "Invalid key: %s. Must be one of: %s" % (key, _allowed_keys)
        raise ValueError, msg
    cells = [p for p in mesh['cells'] if p is not None and p[key] >= vmin and
             p[key] <= vmax]
    filtered = {'size':len(cells), 'cells':cells}
    return filtered
