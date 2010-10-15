'''Various extensions to distributions

* skew normal and skew t distribution by Azzalini, A. & Capitanio, A.
* Gram-Charlier expansion distribution (using 4 moments),
* distributions based on non-linear transformation
  - Transf_gen
  - ExpTransf_gen, LogTransf_gen
  - TransfTwo_gen
    (defines as examples: square, negative square and abs transformations)
  - this versions are without __new__
* mnvormcdf, mvstdnormcdf : cdf, rectangular integral for multivariate normal
  distribution

TODO:
* Where is Transf_gen for general monotonic transformation ? found and added it
* write some docstrings, some parts I don't remember
* add Box-Cox transformation, parameterized ?


this is only partially cleaned, still includes test examples as functions

main changes
* add transf_gen (2010-05-09)
* added separate example and tests (2010-05-09)
* collect transformation function into classes

Example
-------

>>> logtg = Transf_gen(stats.t, np.exp, np.log,
                numargs = 1, a=0, name = 'lnnorm',
                longname = 'Exp transformed normal',
                extradoc = '\ndistribution of y = exp(x), with x standard normal'
                'precision for moment andstats is not very high, 2-3 decimals')
>>> logtg.cdf(5, 6)
0.92067704211191848
>>> stats.t.cdf(np.log(5), 6)
0.92067704211191848

>>> logtg.pdf(5, 6)
0.021798547904239293
>>> stats.t.pdf(np.log(5), 6)
0.10899273954837908
>>> stats.t.pdf(np.log(5), 6)/5.  #derivative
0.021798547909675815


Author: josef-pktd
License: BSD

'''

#note copied from distr_skewnorm_0.py

from scipy import stats, special, integrate  # integrate is for scipy 0.6.0 ???
from scipy.stats import distributions
from stats_extras import mvsk2mc, mc2mvsk
import numpy as np

class SkewNorm_gen(distributions.rv_continuous):
    '''univariate Skew-Normal distribution of Azzalini

    class follows scipy.stats.distributions pattern
    but with __init__

    '''
    def __init__(self):
        #super(SkewNorm_gen,self).__init__(
        distributions.rv_continuous.__init__(self,
            name = 'Skew Normal distribution', shapes = 'alpha',
            extradoc = ''' '''                                 )

    def _argcheck(self, alpha):
        return 1 #(alpha >= 0)

    def _rvs(self, alpha):
        # see http://azzalini.stat.unipd.it/SN/faq.html
        delta = alpha/np.sqrt(1+alpha**2)
        u0 = stats.norm.rvs(size=self._size)
        u1 = delta*u0 + np.sqrt(1-delta**2)*stats.norm.rvs(size=self._size)
        return np.where(u0>0, u1, -u1)

    def _munp(self, n, alpha):
        # use pdf integration with _mom0_sc if only _pdf is defined.
        # default stats calculation uses ppf, which is much slower
        return self._mom0_sc(n, alpha)

    def _pdf(self,x,alpha):
        # 2*normpdf(x)*normcdf(alpha*x)
        return 2.0/np.sqrt(2*np.pi)*np.exp(-x**2/2.0) * special.ndtr(alpha*x)

    def _stats_skip(self,x,alpha,moments='mvsk'):
        #skip for now to force moment integration as check
        pass

def example_n():
    skewnorm = SkewNorm_gen()
    print skewnorm.pdf(1,0), stats.norm.pdf(1), skewnorm.pdf(1,0) - stats.norm.pdf(1)
    print skewnorm.pdf(1,1000), stats.chi.pdf(1,1), skewnorm.pdf(1,1000) - stats.chi.pdf(1,1)
    print skewnorm.pdf(-1,-1000), stats.chi.pdf(1,1), skewnorm.pdf(-1,-1000) - stats.chi.pdf(1,1)
    rvs = skewnorm.rvs(0,size=500)
    print 'sample mean var: ', rvs.mean(), rvs.var()
    print 'theoretical mean var', skewnorm.stats(0)
    rvs = skewnorm.rvs(5,size=500)
    print 'sample mean var: ', rvs.mean(), rvs.var()
    print 'theoretical mean var', skewnorm.stats(5)
    print skewnorm.cdf(1,0), stats.norm.cdf(1), skewnorm.cdf(1,0) - stats.norm.cdf(1)
    print skewnorm.cdf(1,1000), stats.chi.cdf(1,1), skewnorm.cdf(1,1000) - stats.chi.cdf(1,1)
    print skewnorm.sf(0.05,1000), stats.chi.sf(0.05,1), skewnorm.sf(0.05,1000) - stats.chi.sf(0.05,1)

# generated the same way as distributions in stats.distributions
class SkewNorm2_gen(distributions.rv_continuous):
    '''univariate Skew-Normal distribution of Azzalini

    class follows scipy.stats.distributions pattern

    '''
    def _argcheck(self, alpha):
        return 1 #where(alpha>=0, 1, 0)

    def _pdf(self,x,alpha):
        # 2*normpdf(x)*normcdf(alpha*x
        return 2.0/np.sqrt(2*np.pi)*np.exp(-x**2/2.0) * special.ndtr(alpha*x)

skewnorm2 = SkewNorm2_gen(name = 'Skew Normal distribution', shapes = 'alpha',
                          extradoc = '''  -inf < alpha < inf''')



class ACSkewT_gen(distributions.rv_continuous):
    '''univariate Skew-T distribution of Azzalini

    class follows scipy.stats.distributions pattern
    but with __init__
    '''
    def __init__(self):
        #super(SkewT_gen,self).__init__(
        distributions.rv_continuous.__init__(self,
            name = 'Skew T distribution', shapes = 'alpha',
            extradoc = '''
Skewed T distribution by Azzalini, A. & Capitanio, A. (2003)_

the pdf is given by:
 pdf(x) = 2.0 * t.pdf(x, df) * t.cdf(df+1, alpha*x*np.sqrt((1+df)/(x**2+df)))

with alpha >=0

Note: different from skewed t distribution by Hansen 1999
.._
Azzalini, A. & Capitanio, A. (2003), Distributions generated by perturbation of
symmetry with emphasis on a multivariate skew-t distribution,
appears in J.Roy.Statist.Soc, series B, vol.65, pp.367-389

'''                               )

    def _argcheck(self, df, alpha):
        return (alpha == alpha)*(df>0)

##    def _arg_check(self, alpha):
##        return np.where(alpha>=0, 0, 1)
##    def _argcheck(self, alpha):
##        return np.where(alpha>=0, 1, 0)

    def _rvs(self, df, alpha):
        # see http://azzalini.stat.unipd.it/SN/faq.html
        #delta = alpha/np.sqrt(1+alpha**2)
        V = stats.chi2.rvs(df, size=self._size)
        z = skewnorm.rvs(alpha, size=self._size)
        return z/np.sqrt(V/df)

    def _munp(self, n, df, alpha):
        # use pdf integration with _mom0_sc if only _pdf is defined.
        # default stats calculation uses ppf
        return self._mom0_sc(n, df, alpha)

    def _pdf(self,x,df,alpha):
        # 2*normpdf(x)*normcdf(alpha*x)
        return 2.0*distributions.t._pdf(x, df) * special.stdtr(df+1, alpha*x*np.sqrt((1+df)/(x**2+df)))

def example_T():
    skewt = ACSkewT_gen()
    rvs = skewt.rvs(10,0,size=500)
    print 'sample mean var: ', rvs.mean(), rvs.var()
    print 'theoretical mean var', skewt.stats(10,0)
    print 't mean var', stats.t.stats(10)
    print skewt.stats(10,1000) # -> folded t distribution, as alpha -> inf
    rvs = np.abs(stats.t.rvs(10,size=1000))
    print rvs.mean(), rvs.var()

##
##def mvsk2cm(*args):
##    mu,sig,sk,kur = args
##    # Get central moments
##    cnt = [None]*4
##    cnt[0] = mu
##    cnt[1] = sig #*sig
##    cnt[2] = sk * sig**1.5
##    cnt[3] = (kur+3.0) * sig**2.0
##    return cnt
##
##
##def mvsk2m(args):
##    mc, mc2, skew, kurt = args#= self._stats(*args,**mdict)
##    mnc = mc
##    mnc2 = mc2 + mc*mc
##    mc3  = skew*(mc2**1.5) # 3rd central moment
##    mnc3 = mc3+3*mc*mc2+mc**3 # 3rd non-central moment
##    mc4  = (kurt+3.0)*(mc2**2.0) # 4th central moment
##    mnc4 = mc4+4*mc*mc3+6*mc*mc*mc2+mc**4
##    return (mc, mc2, mc3, mc4), (mnc, mnc2, mnc3, mnc4)
##
##def mc2mvsk(args):
##    mc, mc2, mc3, mc4 = args
##    skew = mc3 / mc2**1.5
##    kurt = mc4 / mc2**2.0 - 3.0
##    return (mc, mc2, skew, kurt)
##
##def m2mc(args):
##    mnc, mnc2, mnc3, mnc4 = args
##    mc = mnc
##    mc2 = mnc2 - mnc*mnc
##    #mc3  = skew*(mc2**1.5) # 3rd central moment
##    mc3 = mnc3 - (3*mc*mc2+mc**3) # 3rd central moment
##    #mc4  = (kurt+3.0)*(mc2**2.0) # 4th central moment
##    mc4 = mnc4 - (4*mc*mc3+6*mc*mc*mc2+mc**4)
##    return (mc, mc2, mc3, mc4)


from numpy import poly1d,sqrt, exp
import scipy
def _hermnorm(N):
    # return the negatively normalized hermite polynomials up to order N-1
    #  (inclusive)
    #  using the recursive relationship
    #  p_n+1 = p_n(x)' - x*p_n(x)
    #   and p_0(x) = 1
    plist = [None]*N
    plist[0] = poly1d(1)
    for n in range(1,N):
        plist[n] = plist[n-1].deriv() - poly1d([1,0])*plist[n-1]
    return plist

def pdf_moments_st(cnt):
    """Return the Gaussian expanded pdf function given the list of central
    moments (first one is mean).

    version of scipy.stats, any changes ?
    the scipy.stats version has a bug and returns normal distribution

    """

    N = len(cnt)
    if N < 2:
        raise ValueError, "At least two moments must be given to" + \
              "approximate the pdf."

    totp = poly1d(1)
    sig = sqrt(cnt[1])
    mu = cnt[0]
    if N > 2:
        Dvals = _hermnorm(N+1)
    for k in range(3,N+1):
        # Find Ck
        Ck = 0.0
        for n in range((k-3)/2):
            m = k-2*n
            if m % 2: # m is odd
                momdiff = cnt[m-1]
            else:
                momdiff = cnt[m-1] - sig*sig*scipy.factorial2(m-1)
            Ck += Dvals[k][m] / sig**m * momdiff
        # Add to totp
        raise
        print Dvals
        print Ck
        totp = totp +  Ck*Dvals[k]

    def thisfunc(x):
        xn = (x-mu)/sig
        return totp(xn)*exp(-xn*xn/2.0)/sqrt(2*np.pi)/sig
    return thisfunc, totp

def pdf_mvsk(mvsk):
    """Return the Gaussian expanded pdf function given the list of 1st, 2nd
    moment and skew and Fisher (excess) kurtosis.



    Parameters
    ----------
    mvsk : list of mu, mc2, skew, kurt
        distribution is matched to these four moments

    Returns
    -------
    pdffunc : function
        function that evaluates the pdf(x), where x is the non-standardized
        random variable.


    Notes
    -----

    Changed so it works only if four arguments are given. Uses explicit
    formula, not loop.

    This implements a Gram-Charlier expansion of the normal distribution
    where the first 2 moments coincide with those of the normal distribution
    but skew and kurtosis can deviate from it.

    In the Gram-Charlier distribution it is possible that the density
    becomes negative. This is the case when the deviation from the
    normal distribution is too large.



    References
    ----------
    http://en.wikipedia.org/wiki/Edgeworth_series
    Johnson N.L., S. Kotz, N. Balakrishnan: Continuous Univariate
    Distributions, Volume 1, 2nd ed., p.30
    """
    N = len(mvsk)
    if N < 4:
        raise ValueError, "Four moments must be given to" + \
              "approximate the pdf."

    mu, mc2, skew, kurt = mvsk

    totp = poly1d(1)
    sig = sqrt(mc2)
    if N > 2:
        Dvals = _hermnorm(N+1)
        C3 = skew/6.0
        C4 = kurt/24.0
        # Note: Hermite polynomial for order 3 in _hermnorm is negative
        # instead of positive
        totp = totp -  C3*Dvals[3] +  C4*Dvals[4]

    def pdffunc(x):
        xn = (x-mu)/sig
        return totp(xn)*np.exp(-xn*xn/2.0)/np.sqrt(2*np.pi)/sig
    return pdffunc

def pdf_moments(cnt):
    """Return the Gaussian expanded pdf function given the list of central
    moments (first one is mean).

    Changed so it works only if four arguments are given. Uses explicit
    formula, not loop.

    Notes
    -----

    This implements a Gram-Charlier expansion of the normal distribution
    where the first 2 moments coincide with those of the normal distribution
    but skew and kurtosis can deviate from it.

    In the Gram-Charlier distribution it is possible that the density
    becomes negative. This is the case when the deviation from the
    normal distribution is too large.



    References
    ----------
    http://en.wikipedia.org/wiki/Edgeworth_series
    Johnson N.L., S. Kotz, N. Balakrishnan: Continuous Univariate
    Distributions, Volume 1, 2nd ed., p.30
    """
    N = len(cnt)
    if N < 2:
        raise ValueError, "At least two moments must be given to" + \
              "approximate the pdf."



    mc, mc2, mc3, mc4 = cnt
    skew = mc3 / mc2**1.5
    kurt = mc4 / mc2**2.0 - 3.0  # Fisher kurtosis, excess kurtosis

    totp = poly1d(1)
    sig = sqrt(cnt[1])
    mu = cnt[0]
    if N > 2:
        Dvals = _hermnorm(N+1)
##    for k in range(3,N+1):
##        # Find Ck
##        Ck = 0.0
##        for n in range((k-3)/2):
##            m = k-2*n
##            if m % 2: # m is odd
##                momdiff = cnt[m-1]
##            else:
##                momdiff = cnt[m-1] - sig*sig*scipy.factorial2(m-1)
##            Ck += Dvals[k][m] / sig**m * momdiff
##        # Add to totp
##        raise
##        print Dvals
##        print Ck
##        totp = totp +  Ck*Dvals[k]
        C3 = skew/6.0
        C4 = kurt/24.0
        totp = totp -  C3*Dvals[3] +  C4*Dvals[4]

    def thisfunc(x):
        xn = (x-mu)/sig
        return totp(xn)*np.exp(-xn*xn/2.0)/np.sqrt(2*np.pi)/sig
    return thisfunc

class NormExpan_gen(distributions.rv_continuous):
    '''Gram-Charlier Expansion of Normal distribution

    class follows scipy.stats.distributions pattern
    but with __init__

    '''
    def __init__(self,args, **kwds):
        #todo: replace with super call
        distributions.rv_continuous.__init__(self,
            name = 'Normal Expansion distribution', shapes = 'alpha',
            extradoc = '''
        The distribution is defined as the Gram-Charlier expansion of
        the normal distribution using the first four moments. The pdf
        is given by

        pdf(x) = (1+ skew/6.0 * H(xc,3) + kurt/24.0 * H(xc,4))*normpdf(xc)

        where xc = (x-mu)/sig is the standardized value of the random variable
        and H(xc,3) and H(xc,4) are Hermite polynomials

        Note: This distribution has to be parameterized during
        initialization and instantiation, and does not have a shape
        parameter after instantiation (similar to frozen distribution
        except for location and scale.) Location and scale can be used
        as with other distributions, however note, that they are relative
        to the initialized distribution.
        '''  )
        #print args, kwds
        mode = kwds.get('mode', 'sample')

        if mode == 'sample':
            mu,sig,sk,kur = stats.describe(args)[2:]
            self.mvsk = (mu,sig,sk,kur)
            cnt = mvsk2mc((mu,sig,sk,kur))
        elif mode == 'mvsk':
            cnt = mvsk2mc(args)
            self.mvsk = args
        elif mode == 'centmom':
            cnt = args
            self.mvsk = mc2mvsk(cnt)
        else:
            raise ValueError, "mode must be 'mvsk' or centmom"

        self.cnt = cnt
        #self.mvsk = (mu,sig,sk,kur)
        #self._pdf = pdf_moments(cnt)
        self._pdf = pdf_mvsk(self.mvsk)

    def _munp(self,n):
        # use pdf integration with _mom0_sc if only _pdf is defined.
        # default stats calculation uses ppf
        return self._mom0_sc(n)

    def _stats_skip(self):
        # skip for now to force numerical integration of pdf for testing
        return self.mvsk


def examples_normexpand():
    skewnorm = SkewNorm_gen()
    rvs = skewnorm.rvs(5,size=100)
    normexpan = NormExpan_gen(rvs, mode='sample')

    smvsk = stats.describe(rvs)[2:]
    print 'sample: mu,sig,sk,kur'
    print smvsk

    dmvsk = normexpan.stats(moments='mvsk')
    print 'normexpan: mu,sig,sk,kur'
    print dmvsk
    print 'mvsk diff distribution - sample'
    print np.array(dmvsk) - np.array(smvsk)
    print 'normexpan attributes mvsk'
    print mc2mvsk(normexpan.cnt)
    print normexpan.mvsk


    mc, mnc = mvsk2m(dmvsk)
    print 'central moments'
    print mc
    print 'non-central moments'
    print mnc


    pdffn = pdf_moments(mc)
    print '\npdf approximation from moments'
    print 'pdf at', mc[0]-1,mc[0]+1
    print pdffn([mc[0]-1,mc[0]+1])
    print normexpan.pdf([mc[0]-1,mc[0]+1])


## copied from nonlinear_transform_gen.py

''' A class for the distribution of a non-linear monotonic transformation of a continuous random variable

simplest usage:
example: create log-gamma distribution, i.e. y = log(x),
            where x is gamma distributed (also available in scipy.stats)
    loggammaexpg = Transf_gen(stats.gamma, np.log, np.exp)

example: what is the distribution of the discount factor y=1/(1+x)
            where interest rate x is normally distributed with N(mux,stdx**2)')?
            (just to come up with a story that implies a nice transformation)
    invnormalg = Transf_gen(stats.norm, inversew, inversew_inv, decr=True, a=-np.inf)

This class does not work well for distributions with difficult shapes,
    e.g. 1/x where x is standard normal, because of the singularity and jump at zero.

Note: I'm working from my version of scipy.stats.distribution.
      But this script runs under scipy 0.6.0 (checked with numpy: 1.2.0rc2 and python 2.4)

This is not yet thoroughly tested, polished or optimized

TODO:
  * numargs handling is not yet working properly, numargs needs to be specified (default = 0 or 1)
  * feeding args and kwargs to underlying distribution is untested and incomplete
  * distinguish args and kwargs for the transformed and the underlying distribution
    - currently all args and no kwargs are transmitted to underlying distribution
    - loc and scale only work for transformed, but not for underlying distribution
    - possible to separate args for transformation and underlying distribution parameters

  * add _rvs as method, will be faster in many cases


Created on Tuesday, October 28, 2008, 12:40:37 PM
Author: josef-pktd
License: BSD

'''

from scipy import integrate # for scipy 0.6.0

from scipy import stats, info
from scipy.stats import distributions
import numpy as np

def get_u_argskwargs(**kwargs):
    #Todo: What's this? wrong spacing, used in Transf_gen TransfTwo_gen
    u_kwargs = dict((k.replace('u_','',1),v) for k,v in kwargs.items()
                    if k.startswith('u_'))
    u_args = u_kwargs.pop('u_args',None)
    return u_args, u_kwargs

class Transf_gen(distributions.rv_continuous):
    '''a class for non-linear monotonic transformation of a continuous random variable

    '''
    def __init__(self, kls, func, funcinv, *args, **kwargs):
        #print args
        #print kwargs

        self.func = func
        self.funcinv = funcinv
        #explicit for self.__dict__.update(kwargs)
        #need to set numargs because inspection does not work
        self.numargs = kwargs.pop('numargs', 0)
        #print self.numargs
        name = kwargs.pop('name','transfdist')
        longname = kwargs.pop('longname','Non-linear transformed distribution')
        extradoc = kwargs.pop('extradoc',None)
        a = kwargs.pop('a', -np.inf)
        b = kwargs.pop('b', np.inf)
        self.decr = kwargs.pop('decr', False)
            #defines whether it is a decreasing (True)
            #       or increasing (False) monotonic transformation


        self.u_args, self.u_kwargs = get_u_argskwargs(**kwargs)
        self.kls = kls   #(self.u_args, self.u_kwargs)
                         # possible to freeze the underlying distribution

        super(Transf_gen,self).__init__(a=a, b=b, name = name,
                                longname = longname, extradoc = extradoc)

    def _cdf(self,x,*args, **kwargs):
        #print args
        if not self.decr:
            return self.kls._cdf(self.funcinv(x),*args, **kwargs)
            #note scipy _cdf only take *args not *kwargs
        else:
            return 1.0 - self.kls._cdf(self.funcinv(x),*args, **kwargs)
    def _ppf(self, q, *args, **kwargs):
        if not self.decr:
            return self.func(self.kls._ppf(q,*args, **kwargs))
        else:
            return self.func(self.kls._ppf(1-q,*args, **kwargs))


def inverse(x):
    return np.divide(1.0,x)

mux, stdx = 0.05, 0.1
mux, stdx = 9.0, 1.0
def inversew(x):
    return 1.0/(1+mux+x*stdx)
def inversew_inv(x):
    return (1.0/x - 1.0 - mux)/stdx #.np.divide(1.0,x)-10

def identit(x):
    return x

invdnormalg = Transf_gen(stats.norm, inversew, inversew_inv, decr=True, #a=-np.inf,
                numargs = 0, name = 'discf', longname = 'normal-based discount factor',
                extradoc = '\ndistribution of discount factor y=1/(1+x)) with x N(0.05,0.1**2)')

lognormalg = Transf_gen(stats.norm, np.exp, np.log,
                numargs = 2, a=0, name = 'lnnorm',
                longname = 'Exp transformed normal',
                extradoc = '\ndistribution of y = exp(x), with x standard normal'
                'precision for moment andstats is not very high, 2-3 decimals')


loggammaexpg = Transf_gen(stats.gamma, np.log, np.exp, numargs=1)

## copied form nonlinear_transform_short.py

'''univariate distribution of a non-linear monotonic transformation of a
random variable

'''
from scipy import stats
from scipy.stats import distributions
import numpy as np

class ExpTransf_gen(distributions.rv_continuous):
    '''Distribution based on log/exp transformation

    the constructor can be called with a distribution class
    and generates the distribution of the transformed random variable

    '''
    def __init__(self, kls, *args, **kwargs):
        #print args
        #print kwargs
        #explicit for self.__dict__.update(kwargs)
        if 'numargs' in kwargs:
            self.numargs = kwargs['numargs']
        else:
            self.numargs = 1
        if 'name' in kwargs:
            name = kwargs['name']
        else:
            name = 'Log transformed distribution'
        if 'a' in kwargs:
            a = kwargs['a']
        else:
            a = 0
        super(ExpTransf_gen,self).__init__(a=0, name = 'Log transformed distribution')
        self.kls = kls
    def _cdf(self,x,*args):
        #print args
        return self.kls._cdf(np.log(x),*args)
    def _ppf(self, q, *args):
        return np.exp(self.kls._ppf(q,*args))

class LogTransf_gen(distributions.rv_continuous):
    '''Distribution based on log/exp transformation

    the constructor can be called with a distribution class
    and generates the distribution of the transformed random variable

    '''
    def __init__(self, kls, *args, **kwargs):
        #explicit for self.__dict__.update(kwargs)
        if 'numargs' in kwargs:
            self.numargs = kwargs['numargs']
        else:
            self.numargs = 1
        if 'name' in kwargs:
            name = kwargs['name']
        else:
            name = 'Log transformed distribution'
        if 'a' in kwargs:
            a = kwargs['a']
        else:
            a = 0

        super(LogTransf_gen,self).__init__(a=a, name = name)
        self.kls = kls

    def _cdf(self,x, *args):
        #print args
        return self.kls._cdf(np.exp(x),*args)
    def _ppf(self, q, *args):
        return np.log(self.kls._ppf(q,*args))

def examples_transf():
    ##lognormal = ExpTransf(a=0.0, xa=-10.0, name = 'Log transformed normal')
    ##print lognormal.cdf(1)
    ##print stats.lognorm.cdf(1,1)
    ##print lognormal.stats()
    ##print stats.lognorm.stats(1)
    ##print lognormal.rvs(size=10)

    print 'Results for lognormal'
    lognormalg = ExpTransf_gen(stats.norm, a=0, name = 'Log transformed normal general')
    print lognormalg.cdf(1)
    print stats.lognorm.cdf(1,1)
    print lognormalg.stats()
    print stats.lognorm.stats(1)
    print lognormalg.rvs(size=5)

    ##print 'Results for loggamma'
    ##loggammag = ExpTransf_gen(stats.gamma)
    ##print loggammag._cdf(1,10)
    ##print stats.loggamma.cdf(1,10)

    print 'Results for expgamma'
    loggammaexpg = LogTransf_gen(stats.gamma)
    print loggammaexpg._cdf(1,10)
    print stats.loggamma.cdf(1,10)
    print loggammaexpg._cdf(2,15)
    print stats.loggamma.cdf(2,15)


    # this requires change in scipy.stats.distribution
    #print loggammaexpg.cdf(1,10)

    print 'Results for loglaplace'
    loglaplaceg = LogTransf_gen(stats.laplace)
    print loglaplaceg._cdf(2,10)
    print stats.loglaplace.cdf(2,10)
    loglaplaceexpg = ExpTransf_gen(stats.laplace)
    print loglaplaceexpg._cdf(2,10)




## copied from transformtwo.py

'''
Created on Apr 28, 2009

@author: Josef Perktold
'''

''' A class for the distribution of a non-linear u-shaped or hump shaped transformation of a
continuous random variable

This is a companion to the distributions of non-linear monotonic transformation to the case
when the inverse mapping is a 2-valued correspondence, for example for absolute value or square

simplest usage:
example: create squared distribution, i.e. y = x**2,
            where x is normal or t distributed


This class does not work well for distributions with difficult shapes,
    e.g. 1/x where x is standard normal, because of the singularity and jump at zero.


This verifies for normal - chi2, normal - halfnorm, foldnorm, and t - F

TODO:
  * numargs handling is not yet working properly,
    numargs needs to be specified (default = 0 or 1)
  * feeding args and kwargs to underlying distribution works in t distribution example
  * distinguish args and kwargs for the transformed and the underlying distribution
    - currently all args and no kwargs are transmitted to underlying distribution
    - loc and scale only work for transformed, but not for underlying distribution
    - possible to separate args for transformation and underlying distribution parameters

  * add _rvs as method, will be faster in many cases

'''


class TransfTwo_gen(distributions.rv_continuous):
    '''Distribution based on a non-monotonic (u- or hump-shaped transformation)

    the constructor can be called with a distribution class, and functions
    that define the non-linear transformation.
    and generates the distribution of the transformed random variable

    Note: the transformation, it's inverse and derivatives need to be fully
    specified: func, funcinvplus, funcinvminus, derivplus,  derivminus.
    Currently no numerical derivatives or inverse are calculated

    This can be used to generate distribution instances similar to the
    distributions in scipy.stats.

    '''
    #a class for non-linear non-monotonic transformation of a continuous random variable
    def __init__(self, kls, func, funcinvplus, funcinvminus, derivplus,
                 derivminus, *args, **kwargs):
        #print args
        #print kwargs

        self.func = func
        self.funcinvplus = funcinvplus
        self.funcinvminus = funcinvminus
        self.derivplus = derivplus
        self.derivminus = derivminus
        #explicit for self.__dict__.update(kwargs)
        #need to set numargs because inspection does not work
        self.numargs = kwargs.pop('numargs', 0)
        #print self.numargs
        name = kwargs.pop('name','transfdist')
        longname = kwargs.pop('longname','Non-linear transformed distribution')
        extradoc = kwargs.pop('extradoc',None)
        a = kwargs.pop('a', -np.inf) # attached to self in super
        b = kwargs.pop('b', np.inf)  # self.a, self.b would be overwritten
        self.shape = kwargs.pop('shape', False)
            #defines whether it is a `u` shaped or `hump' shaped
            #       transformation


        self.u_args, self.u_kwargs = get_u_argskwargs(**kwargs)
        self.kls = kls   #(self.u_args, self.u_kwargs)
                         # possible to freeze the underlying distribution

        super(TransfTwo_gen,self).__init__(a=a, b=b, name = name,
                                longname = longname, extradoc = extradoc)

    def _rvs(self, *args):
        self.kls._size = self._size   #size attached to self, not function argument
        return self.func(self.kls._rvs(*args))

    def _pdf(self,x,*args, **kwargs):
        #print args
        if self.shape == 'u':
            signpdf = 1
        elif self.shape == 'hump':
            signpdf = -1
        else:
            raise ValueError, 'shape can only be `u` or `hump`'

        return signpdf * (self.derivplus(x)*self.kls._pdf(self.funcinvplus(x),*args, **kwargs) -
                   self.derivminus(x)*self.kls._pdf(self.funcinvminus(x),*args, **kwargs))
            #note scipy _cdf only take *args not *kwargs

    def _cdf(self,x,*args, **kwargs):
        #print args
        if self.shape == 'u':
            return self.kls._cdf(self.funcinvplus(x),*args, **kwargs) - \
                   self.kls._cdf(self.funcinvminus(x),*args, **kwargs)
            #note scipy _cdf only take *args not *kwargs
        else:
            return 1.0 - self._sf(x,*args, **kwargs)

    def _sf(self,x,*args, **kwargs):
        #print args
        if self.shape == 'hump':
            return self.kls._cdf(self.funcinvplus(x),*args, **kwargs) - \
                   self.kls._cdf(self.funcinvminus(x),*args, **kwargs)
            #note scipy _cdf only take *args not *kwargs
        else:
            return 1.0 - self._cdf(x, *args, **kwargs)

    def _munp(self, n,*args, **kwargs):
        return self._mom0_sc(n,*args)
# ppf might not be possible in general case?
# should be possible in symmetric case
#    def _ppf(self, q, *args, **kwargs):
#        if self.shape == 'u':
#            return self.func(self.kls._ppf(q,*args, **kwargs))
#        elif self.shape == 'hump':
#            return self.func(self.kls._ppf(1-q,*args, **kwargs))

#TODO: rename these functions to have unique names

class SquareFunc(object):
    '''class to hold quadratic function with inverse function and derivative

    using instance methods instead of class methods, if we want extension
    to parameterized function
    '''
    def inverseplus(self, x):
        return np.sqrt(x)

    def inverseminus(self, x):
        return 0.0 - np.sqrt(x)

    def derivplus(self, x):
        return 0.5/np.sqrt(x)

    def derivminus(self, x):
        return 0.0 - 0.5/np.sqrt(x)

    def squarefunc(self, x):
        return np.power(x,2)

sqfunc = SquareFunc()

squarenormalg = TransfTwo_gen(stats.norm, sqfunc.squarefunc, sqfunc.inverseplus,
                sqfunc.inverseminus, sqfunc.derivplus, sqfunc.derivminus,
                shape='u', a=0.0, b=np.inf,
                numargs = 0, name = 'squarenorm', longname = 'squared normal distribution',
                extradoc = '\ndistribution of the square of a normal random variable' +\
                           ' y=x**2 with x N(0.0,1)')
                        #u_loc=l, u_scale=s)
squaretg = TransfTwo_gen(stats.t, sqfunc.squarefunc, sqfunc.inverseplus,
                sqfunc.inverseminus, sqfunc.derivplus, sqfunc.derivminus,
                shape='u', a=0.0, b=np.inf,
                numargs = 1, name = 'squarenorm', longname = 'squared t distribution',
                extradoc = '\ndistribution of the square of a t random variable' +\
                           ' y=x**2 with x t(dof,0.0,1)')

def inverseplus(x):
    return np.sqrt(-x)

def inverseminus(x):
    return 0.0 - np.sqrt(-x)

def derivplus(x):
    return 0.0 - 0.5/np.sqrt(-x)

def derivminus(x):
    return 0.5/np.sqrt(-x)

def negsquarefunc(x):
    return -np.power(x,2)


negsquarenormalg = TransfTwo_gen(stats.norm, negsquarefunc, inverseplus, inverseminus,
                derivplus, derivminus, shape='hump', a=-np.inf, b=0.0,
                numargs = 0, name = 'negsquarenorm', longname = 'negative squared normal distribution',
                extradoc = '\ndistribution of the negative square of a normal random variable' +\
                           ' y=-x**2 with x N(0.0,1)')
                        #u_loc=l, u_scale=s)

def inverseplus(x):
    return x

def inverseminus(x):
    return 0.0 - x

def derivplus(x):
    return 1.0

def derivminus(x):
    return 0.0 - 1.0

def absfunc(x):
    return np.abs(x)


absnormalg = TransfTwo_gen(stats.norm, np.abs, inverseplus, inverseminus,
                derivplus, derivminus, shape='u', a=0.0, b=np.inf,
                numargs = 0, name = 'absnorm', longname = 'absolute of normal distribution',
                extradoc = '\ndistribution of the absolute value of a normal random variable' +\
                           ' y=abs(x) with x N(0,1)')


#copied from mvncdf.py
'''multivariate normal probabilities and cumulative distribution function
a wrapper for scipy.stats.kde.mvndst


      SUBROUTINE MVNDST( N, LOWER, UPPER, INFIN, CORREL, MAXPTS,
     &                   ABSEPS, RELEPS, ERROR, VALUE, INFORM )
*
*     A subroutine for computing multivariate normal probabilities.
*     This subroutine uses an algorithm given in the paper
*     "Numerical Computation of Multivariate Normal Probabilities", in
*     J. of Computational and Graphical Stat., 1(1992), pp. 141-149, by
*          Alan Genz
*          Department of Mathematics
*          Washington State University
*          Pullman, WA 99164-3113
*          Email : AlanGenz@wsu.edu
*
*  Parameters
*
*     N      INTEGER, the number of variables.
*     LOWER  REAL, array of lower integration limits.
*     UPPER  REAL, array of upper integration limits.
*     INFIN  INTEGER, array of integration limits flags:
*            if INFIN(I) < 0, Ith limits are (-infinity, infinity);
*            if INFIN(I) = 0, Ith limits are (-infinity, UPPER(I)];
*            if INFIN(I) = 1, Ith limits are [LOWER(I), infinity);
*            if INFIN(I) = 2, Ith limits are [LOWER(I), UPPER(I)].
*     CORREL REAL, array of correlation coefficients; the correlation
*            coefficient in row I column J of the correlation matrix
*            should be stored in CORREL( J + ((I-2)*(I-1))/2 ), for J < I.
*            THe correlation matrix must be positive semidefinite.
*     MAXPTS INTEGER, maximum number of function values allowed. This
*            parameter can be used to limit the time. A sensible
*            strategy is to start with MAXPTS = 1000*N, and then
*            increase MAXPTS if ERROR is too large.
*     ABSEPS REAL absolute error tolerance.
*     RELEPS REAL relative error tolerance.
*     ERROR  REAL estimated absolute error, with 99% confidence level.
*     VALUE  REAL estimated value for the integral
*     INFORM INTEGER, termination status parameter:
*            if INFORM = 0, normal completion with ERROR < EPS;
*            if INFORM = 1, completion with ERROR > EPS and MAXPTS
*                           function vaules used; increase MAXPTS to
*                           decrease ERROR;
*            if INFORM = 2, N > 500 or N < 1.
*



>>> scipy.stats.kde.mvn.mvndst([0.0,0.0],[10.0,10.0],[0,0],[0.5])
(2e-016, 1.0, 0)
>>> scipy.stats.kde.mvn.mvndst([0.0,0.0],[100.0,100.0],[0,0],[0.0])
(2e-016, 1.0, 0)
>>> scipy.stats.kde.mvn.mvndst([0.0,0.0],[1.0,1.0],[0,0],[0.0])
(2e-016, 0.70786098173714096, 0)
>>> scipy.stats.kde.mvn.mvndst([0.0,0.0],[0.001,1.0],[0,0],[0.0])
(2e-016, 0.42100802096993045, 0)
>>> scipy.stats.kde.mvn.mvndst([0.0,0.0],[0.001,10.0],[0,0],[0.0])
(2e-016, 0.50039894221391101, 0)
>>> scipy.stats.kde.mvn.mvndst([0.0,0.0],[0.001,100.0],[0,0],[0.0])
(2e-016, 0.50039894221391101, 0)
>>> scipy.stats.kde.mvn.mvndst([0.0,0.0],[0.01,100.0],[0,0],[0.0])
(2e-016, 0.5039893563146316, 0)
>>> scipy.stats.kde.mvn.mvndst([0.0,0.0],[0.1,100.0],[0,0],[0.0])
(2e-016, 0.53982783727702899, 0)
>>> scipy.stats.kde.mvn.mvndst([0.0,0.0],[0.1,100.0],[2,2],[0.0])
(2e-016, 0.019913918638514494, 0)
>>> scipy.stats.kde.mvn.mvndst([0.0,0.0],[0.0,0.0],[0,0],[0.0])
(2e-016, 0.25, 0)
>>> scipy.stats.kde.mvn.mvndst([0.0,0.0],[0.0,0.0],[-1,0],[0.0])
(2e-016, 0.5, 0)
>>> scipy.stats.kde.mvn.mvndst([0.0,0.0],[0.0,0.0],[-1,0],[0.5])
(2e-016, 0.5, 0)
>>> scipy.stats.kde.mvn.mvndst([0.0,0.0],[0.0,0.0],[0,0],[0.5])
(2e-016, 0.33333333333333337, 0)
>>> scipy.stats.kde.mvn.mvndst([0.0,0.0],[0.0,0.0],[0,0],[0.99])
(2e-016, 0.47747329317779391, 0)
'''

#from scipy.stats import kde

informcode = {0: 'normal completion with ERROR < EPS',
              1: '''completion with ERROR > EPS and MAXPTS function values used;
                    increase MAXPTS to decrease ERROR;''',
              2: 'N > 500 or N < 1'}

def mvstdnormcdf(lower, upper, corrcoef, **kwds):
    '''standardized multivariate normal cumulative distribution function

    This is a wrapper for scipy.stats.kde.mvn.mvndst which calculates
    a rectangular integral over a standardized multivariate normal
    distribution.

    This function assumes standardized scale, that is the variance in each dimension
    is one, but correlation can be arbitrary, covariance = correlation matrix

    Parameters
    ----------
    lower, upper : array_like, 1d
       lower and upper integration limits with length equal to the number
       of dimensions of the multivariate normal distribution. It can contain
       -np.inf or np.inf for open integration intervals
    corrcoef : float or array_like
       specifies correlation matrix in one of three ways, see notes
    optional keyword parameters to influence integration
        * maxpts : int, maximum number of function values allowed. This
             parameter can be used to limit the time. A sensible
             strategy is to start with `maxpts` = 1000*N, and then
             increase `maxpts` if ERROR is too large.
        * abseps : float absolute error tolerance.
        * releps : float relative error tolerance.

    Returns
    -------
    cdfvalue : float
        value of the integral


    Notes
    -----
    The correlation matrix corrcoef can be given in 3 different ways
    If the multivariate normal is two-dimensional than only the
    correlation coefficient needs to be provided.
    For general dimension the correlation matrix can be provided either
    as a one-dimensional array of the upper triangular correlation
    coefficients stacked by rows, or as full square correlation matrix

    See Also
    --------
    mvnormcdf : cdf of multivariate normal distribution without
        standardization

    Examples
    --------

    >>> print mvstdnormcdf([-np.inf,-np.inf], [0.0,np.inf], 0.5)
    0.5
    >>> corr = [[1.0, 0, 0.5],[0,1,0],[0.5,0,1]]
    >>> print mvstdnormcdf([-np.inf,-np.inf,-100.0], [0.0,0.0,0.0], corr, abseps=1e-6)
    0.166666399198
    >>> print mvstdnormcdf([-np.inf,-np.inf,-100.0],[0.0,0.0,0.0],corr, abseps=1e-8)
    something wrong completion with ERROR > EPS and MAXPTS function values used;
                        increase MAXPTS to decrease ERROR; 1.048330348e-006
    0.166666546218
    >>> print mvstdnormcdf([-np.inf,-np.inf,-100.0],[0.0,0.0,0.0], corr,
                            maxpts=100000, abseps=1e-8)
    0.166666588293

    '''
    n = len(lower)
    #don't know if converting to array is necessary,
    #but it makes ndim check possible
    lower = np.array(lower)
    upper = np.array(upper)
    corrcoef = np.array(corrcoef)

    correl = np.zeros(n*(n-1)/2.0)  #dtype necessary?

    if (lower.ndim != 1) or (upper.ndim != 1):
        raise ValueError, 'can handle only 1D bounds'
    if len(upper) != n:
        raise ValueError, 'bounds have different lengths'
    if n==2 and corrcoef.size==1:
        correl = corrcoef
        #print 'case scalar rho', n
    elif corrcoef.ndim == 1 and len(corrcoef) == n*(n-1)/2.0:
        #print 'case flat corr', corrcoeff.shape
        correl = corrcoef
    elif corrcoef.shape == (n,n):
        #print 'case square corr',  correl.shape
        for ii in range(n):
            for jj in range(ii):
                correl[ jj + ((ii-2)*(ii-1))/2] = corrcoef[ii,jj]
    else:
        raise ValueError, 'corrcoef has incorrect dimension'

    if not 'maxpts' in kwds:
        if n >2:
            kwds['maxpts'] = 10000*n

    lowinf = np.isneginf(lower)
    uppinf = np.isposinf(upper)
    infin = 2.0*np.ones(n)

    np.putmask(infin,lowinf,0)# infin.putmask(0,lowinf)
    np.putmask(infin,uppinf,1) #infin.putmask(1,uppinf)
    #this has to be last
    np.putmask(infin,lowinf*uppinf,-1)

##    #remove infs
##    np.putmask(lower,lowinf,-100)# infin.putmask(0,lowinf)
##    np.putmask(upper,uppinf,100) #infin.putmask(1,uppinf)

    #print lower,',',upper,',',infin,',',correl
    #print correl.shape
    #print kwds.items()
    error, cdfvalue, inform = scipy.stats.kde.mvn.mvndst(lower,upper,infin,correl,**kwds)
    if inform:
        print 'something wrong', informcode[inform], error
    return cdfvalue


def mvnormcdf(upper, mu, cov, lower=None,  **kwds):
    '''multivariate normal cumulative distribution function

    This is a wrapper for scipy.stats.kde.mvn.mvndst which calculates
    a rectangular integral over a multivariate normal distribution.

    Parameters
    ----------
    lower, upper : array_like, 1d
       lower and upper integration limits with length equal to the number
       of dimensions of the multivariate normal distribution. It can contain
       -np.inf or np.inf for open integration intervals
    mu : array_lik, 1d
       list or array of means
    cov : array_like, 2d
       specifies covariance matrix
    optional keyword parameters to influence integration
        * maxpts : int, maximum number of function values allowed. This
             parameter can be used to limit the time. A sensible
             strategy is to start with `maxpts` = 1000*N, and then
             increase `maxpts` if ERROR is too large.
        * abseps : float absolute error tolerance.
        * releps : float relative error tolerance.

    Returns
    -------
    cdfvalue : float
        value of the integral


    Notes
    -----
    This function normalizes the location and scale of the multivariate
    normal distribution and then uses `mvstdnormcdf` to call the integration.

    See Also
    --------
    mvstdnormcdf : location and scale standardized multivariate normal cdf
    '''

    upper = np.array(upper)
    if lower is None:
        lower = -np.ones(upper.shape) * np.inf
    else:
        lower = np.array(lower)
    cov = np.array(cov)
    stdev = np.sqrt(np.diag(cov)) # standard deviation vector
    #do I need to make sure stdev is float and not int?
    #is this correct to normalize to corr?
    lower = (lower - mu)/stdev
    upper = (upper - mu)/stdev
    divrow = np.atleast_2d(stdev)
    corr = cov/divrow/divrow.T
    #v/np.sqrt(np.atleast_2d(np.diag(covv)))/np.sqrt(np.atleast_2d(np.diag(covv))).T

    return mvstdnormcdf(lower, upper, corr, **kwds)



