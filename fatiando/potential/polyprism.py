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
Calculate the potential fields and derivatives of the 3D prism with polygonal
crossection. Uses forumla of Plouff (1976)
"""
__author__ = 'Leonardo Uieda (leouieda@gmail.com)'
__date__ = 'Created 28-Sep-2011'

import logging

import numpy

from fatiando.potential import _polyprism


def gz(xp, yp, zp, prisms):
    """
    Calculates the :math:`g_z` gravity acceleration component.

    The coordinate system of the input parameters is to be x -> North,
    y -> East and z -> **DOWN**.

    **NOTE**: All input values in **SI** units(!) and output in **mGal**!

    Parameters:
    * xp, yp, zp
        Lists with (x,y,z) coordinates of the computation points.
        Ex: points = [[1,2,3], [2,3,4]]
    * prisms
        List of PolygonalPrism3D objects. (see :mod:`fatiando.mesher.polyprism`)

    Returns:
    * List with the :math:`g_z` component calculated on *points*

    """
    if xp.shape != yp.shape != zp.shape:
        raise ValueError, "Input arrays xp, yp, and zp must have same shape!"
    res = numpy.zeros_like(xp)
    for p in prisms:
        if p is not None:
            res += _polyprism.polyprism_gz(p['density'], p['bottom'], p['top'],
                                           p['x'], p['y'], xp, yp, zp)
    return res
