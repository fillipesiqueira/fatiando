# Copyright 2012 The Fatiando a Terra Development Team
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
Base Regularizer class with the format expected by all inverse problem solvers,
plus a range of regularizing functions already implemented.

**Tikhonov regularization**

* :class:`fatiando.inversion.regularizer.Damping`

----

"""
__author__ = 'Leonardo Uieda (leouieda@gmail.com)'
__date__ = 'Created 19-Jan-2012'


import numpy
import scipy.sparse

from fatiando import logger

log = logger.dummy()

class Regularizer(object):
    """
    A generic regularizing function module.

    Use this class as a skeleton for building custom regularizer modules, like
    smoothness, damping, total variation, etc.

    Regularizer classes are how each inverse problem solver knows how to
    calculate things like:

    * Value of the regularizing function
    * Gradient of the regularizing function
    * Hessian of the regularizing function

    Not all solvers use all of the above. For examples, heuristic solvers don't
    require gradient and hessian calculations.

    This class has templates for all of these methods so that all solvers know
    what to expect.

    Constructor parameters common to all methods:

    * mu
        The regularizing parameter. A positve scalar that controls the tradeoff
        between data fitting and regularization.
        
    """

    def __init__(self, mu):
        self.mu = mu

    def value(self, p):
        pass

    def sum_gradient(self, gradient, p=None):
        """
        Sums the gradient vector of this regularizer module to *gradient* and
        returns the result.

        Parameters:

        * gradient
            Array with the old gradient vector
        * p
            Array with the parameter vector
            
        Solvers for linear problems will use ``p = None`` so that the class
        knows how to calculate gradients more efficiently for these cases.

        Returns:

        * new_gradient
            Array with the new gradient vector
        
        """
        pass
        
    def sum_hessian(self, hessian, p=None):
        """
        Sums the Hessian matrix of this regularizer module to *hessian* and
        returns the result.

        Parameters:

        * hessian
            2D array with the old Hessian matrix
        * p
            Array with the parameter vector
            
        Solvers for linear problems will use ``p = None`` so that the class
        knows how to calculate gradients more efficiently for these cases.
        
        Returns:

        * new_hessian
            2D array with the new Hessian matrix
        
        """
        pass

class Damping(Regularizer):
    """
    Damping regularization. Also known as Tikhonov order 0, Ridge Regression, or
    Minimum Norm.

    Requires that the estimate have its l2-norm as close as possible to zero.

    The gradient and Hessian matrix are, respectively:
    
    .. math::

        \\bar{g}(\\bar{p}) = 2\\bar{\\bar{I}}\\bar{p}

    and

    .. math::

        \\bar{\\bar{H}}(\\bar{p}) = 2\\bar{\\bar{I}}

    where :math:`\\bar{\\bar{I}}` is the identity matrix.

    Example::

        >>> import numpy
        >>> p = [1, 2, 2]
        >>> hessian = numpy.array([[1, 0, 0], [2, 0, 0], [4, 0, 0]])
        >>> damp = Damping(0.1)
        >>> print damp.value(p)
        0.3
        >>> print damp.sum_hessian(hessian, p)
        [[ 1.2  0.   0. ]
         [ 2.   0.2  0. ]
         [ 4.   0.   0.2]]
    

    Parameters:
        
    * mu
        The regularizing parameter. A positve scalar that controls the tradeoff
        between data fitting and regularization. I.e., how much damping to apply
    * nparams
        Number of parameters in the inversion
    
    """

    def __init__(self, mu, nparams):
        Regularizer.__init__(self, mu)
        self.eye = self._get_identity(nparams)

    def _get_identity(self, nparams):
        return numpy.identity(nparams)

    def value(self, p):
        return self.mu*numpy.linalg.norm(p)**2

    def sum_gradient(self, gradient, p=None):
        if p is None:
            return gradient
        return gradient + (self.mu*2.)*p

    def sum_hessian(self, hessian, p=None):
        return hessian + (self.mu*2.)*self.eye

class DampingSparse(Damping):
    """
    Same as Damping regularizer but using sparse matrices instead.
    """

    def __init__(self, mu, nparams):
        Damping.__init__(self, mu, nparams)

    def _get_identity(self, nparams):
        return scipy.sparse.identity(nparams, dtype='f', format='csr')    

    def sum_hessian(self, hessian, p=None):
        return hessian + (self.mu*2.)*self.eye

class Smoothness1D(Regularizer):
    """
    Smoothness regularization for 1D problems. Also known as Tikhonov order 1.
    Imposes that adjacent parameters be as close as possible. By adjacent, I
    mean next to each other in the parameter vector, e.g., p[2] and p[3].

    The gradient and Hessian matrix are, respectively:
    
    .. math::

        \\bar{g}(\\bar{p}) = 2\\bar{\\bar{R}}^T\\bar{\\bar{R}}\\bar{p}

    and

    .. math::

        \\bar{\\bar{H}}(\\bar{p}) = 2\\bar{\\bar{R}}^T\\bar{\\bar{R}}

    where :math:`\\bar{\\bar{R}}` is a finite difference matrix. For example, if
    there are 7 parameters, matrix :math:`\\bar{\\bar{R}}` will be

    .. math::

        \\bar{\\bar{R}} = 
        \\begin{bmatrix}
        1 & -1 & 0 & 0 & 0 & 0 & 0\\\\
        0 & 1 & -1 & 0 & 0 & 0 & 0\\\\
        0 & 0 & 1 & -1 & 0 & 0 & 0\\\\    
        0 & 0 & 0 & 1 & -1 & 0 & 0\\\\    
        0 & 0 & 0 & 0 & 1 & -1 & 0\\\\   
        0 & 0 & 0 & 0 & 0 & 1 & -1    
        \\end{bmatrix}    

    Parameters:
        
    * mu
        The regularizing parameter. A positve scalar that controls the tradeoff
        between data fitting and regularization. I.e., how much smoothness to
        apply.
    
    """

    def __init__(self, mu, nparams):
        Regularizer.__init__(self, mu)
        fdmat = self._makefd(nparams)
        self.rtr = numpy.dot(fdmat.T, fdmat)

    def _makefd(self, nparams):
        fdmat = numpy.zeros((nparams - 1, nparams), dtype='f')
        for i in xrange(nparams - 1):
            fdmat[i][i] = 1
            fdmat[i][i + 1] = -1
        return fdmat
            
    def value(self, p):
        return self.mu*numpy.dot(p.T, numpy.dot(self.rtr, p))

    def sum_gradient(self, gradient, p=None):
        if p is None:
            return gradient
        return gradient + (self.mu*2.)*numpy.dot(self.rtr, p)

    def sum_hessian(self, hessian, p=None):
        return hessian + (self.mu*2.)*self.rtr
        
def _test():
    import doctest
    doctest.testmod()
    print "doctest finished"

if __name__ == '__main__':
    _test()
