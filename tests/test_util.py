from __future__ import division
from builtins import object

import pytest

import numpy as np
import os
import platform
import collections

from sporco import util
from sporco import metric


def fn(prm):
    x = prm[0]
    return (x - 0.1)**2


def fnv(prm):
    x = prm[0]
    return ((x - 0.1)**2, (x - 0.5)**2)


def kronsum(S, B, C):

    A = np.zeros((B.shape[0] * C.shape[0], B.shape[1] * C.shape[1]))
    for i in range(B.shape[2]):
        A += S[i] * np.kron(B[..., i], C[..., i])
    return A



class TestSet01(object):

    def test_01(self):
        nt = collections.namedtuple('NT', ('A', 'B', 'C'))
        t0 = nt(0, 1, 2)
        t0a = util.ntpl2array(t0)
        t1 = util.array2ntpl(t0a)
        assert t0 == t1


    def test_02(self):
        nt = collections.namedtuple('NT', ('A', 'B', 'C'))
        lst = [nt(0, 1, 2), nt(3, 4, 5)]
        lsttp = util.transpose_ntpl_list(lst)
        assert lst[0].A == lsttp.A[0]


    def test_03(self):
        D = np.random.randn(64, 64)
        im = util.tiledict(D, sz=(8, 8))


    def test_04(self):
        D = np.random.randn(8, 8, 64)
        im = util.tiledict(D)


    def test_05(self):
        D = np.random.randn(8, 8, 64)
        im = util.tiledict(D, sz=((6, 6, 32), (8, 8, 32)))


    def test_06(self):
        D = np.random.randn(8, 8, 3, 64)
        im = util.tiledict(D)


    def test_07(self):
        img = np.random.randn(64, 64)
        blk = util.extractblocks(img, (8, 8))


    def test_08(self):
        rgb = np.random.randn(64, 64, 3)
        gry = util.rgb2gray(rgb)


    def test_09(self):
        img = np.random.randn(64, 64)
        imgn = util.spnoise(img, 0.5)


    def test_10(self):
        msk = util.rndmask((16, 17), 0.25)


    def test_11(self):
        msk = util.rndmask((16, 17), 0.25, dtype=np.float32)


    def test_12(self):
        img = np.random.randn(64, 64)
        iml, imh = util.tikhonov_filter(img, 5.0)


    def test_13(self):
        img = np.random.randn(16, 16, 16)
        iml, imh = util.tikhonov_filter(img, 2.0, npd=8)


    def test_14(self):
        x = np.linspace(-1, 1, 21)
        sprm, sfvl, fvmx, sidx = util.grid_search(fn, (x,))
        assert np.abs(sprm[0] - 0.1) < 1e-14
        assert sidx[0] == 11


    def test_15(self):
        x = np.linspace(-1, 1, 21)
        sprm, sfvl, fvmx, sidx = util.grid_search(fnv, (x,))
        assert np.abs(sprm[0][0] - 0.1) < 1e-14
        assert np.abs(sprm[0][1] - 0.5) < 1e-14
        assert sidx[0][0] == 11
        assert sidx[0][1] == 15


    def test_16(self):
        D = util.convdicts()['G:12x12x72']
        assert D.shape == (12, 12, 72)


    def test_17(self):
        ei = util.ExampleImages()
        im = ei.images()
        assert len(im) > 0
        gp = ei.groups()
        assert len(gp) > 0
        gi = ei.groupimages(gp[0])
        assert len(gi) > 0
        im1 = ei.image('sail.png')
        im2 = ei.image('sail.png', scaled=True, dtype=np.float32,
                       idxexp=np.s_[:, 10:-10], zoom=0.5)


    def test_18(self):
        pth = os.path.join(os.path.dirname(util.__file__), 'data')
        ei = util.ExampleImages(pth=pth)
        im = ei.images()
        assert len(im) > 0


    def test_19(self):
        t = util.Timer()
        t.start()
        t0 = t.elapsed()
        t.stop()
        t1 = t.elapsed()
        assert t0 >= 0.0
        assert t1 >= t0
        assert len(t.__str__()) > 0
        assert len(t.labels()) > 0


    def test_20(self):
        t = util.Timer('a')
        t.start(['a', 'b'])
        t0 = t.elapsed('a')
        t.stop('a')
        t.stop('b')
        t.stop(['a', 'b'])
        assert t.elapsed('a') >= 0.0
        assert t.elapsed('b') >= 0.0
        assert t.elapsed('a', total=False) == 0.0


    def test_21(self):
        t = util.Timer('a')
        t.start(['a', 'b'])
        t.reset('a')
        assert t.elapsed('a') == 0.0
        t.reset('all')
        assert t.elapsed('b') == 0.0


    def test_22(self):
        t = util.Timer()
        with util.ContextTimer(t):
            t0 = t.elapsed()
        assert t.elapsed() >= 0.0


    def test_23(self):
        t = util.Timer()
        t.start()
        with util.ContextTimer(t, action='StopStart'):
            t0 = t.elapsed()
        t.stop()
        assert t.elapsed() >= 0.0


    def test_24(self):
        with pytest.raises(ValueError):
            dat = util.netgetdata('http://devnull', maxtry=0)


    def test_25(self):
        with pytest.raises(util.urlerror.URLError):
            dat = util.netgetdata('http://devnull')


    def test_26(self):
        val = util.in_ipython()
        assert val is True or val is False


    def test_27(self):
        val = util.in_notebook()
        assert val is True or val is False


    @pytest.mark.skipif(platform.system() == 'Windows',
                        reason='Feature not supported under Windows')
    def test_28(self):
        assert util.idle_cpu_count() >= 1


    def test_29(self):
        A = np.random.rand(4, 5, 6, 7, 3)
        blksz = (2, 3, 2)
        stpsz = (2, 1, 2)
        A_blocks = util.extractblocks(A, blksz, stpsz)
        A_recon = util.combineblocks(A_blocks, A.shape, stpsz, np.median)
        assert(np.allclose(np.where(np.isnan(A_recon), np.nan, A),
                           A_recon, equal_nan=True))


    def test_30(self):
        A = np.random.rand(4, 5, 6, 7, 3)
        blksz = (2, 3, 2)
        stpsz = (2, 1, 2)
        A_blocks = util.extractblocks(A, blksz, stpsz)
        noise = np.random.rand(*A_blocks.shape)
        A_average_recon = util.averageblocks(A_blocks + noise, A.shape, stpsz)
        A_combine_recon = util.combineblocks(A_blocks + noise, A.shape,
                                             stpsz, np.mean)
        assert np.allclose(A_combine_recon, A_average_recon, equal_nan=True)


    def test_31(self):
        shape = (7, 5, 6)
        g = util.gaussian(shape)
        assert g.shape == shape


    def test_32(self):
        s = np.random.rand(16, 17, 3)
        scn, smn, snrm = util.local_contrast_normalise(s)
        assert np.linalg.norm(snrm * scn + smn - s) < 1e-7


    def test_33(self):
        U = np.random.randn(5, 10)
        B, S, C = util.pca(U, centre=False)
        assert np.linalg.norm(B.dot(B.T) - np.eye(U.shape[0])) < 1e-10


    def test_34(self):
        U = np.random.randn(5, 10)
        B, S, C = util.pca(U, centre=True)
        assert np.linalg.norm(B.dot(B.T) - np.eye(U.shape[0])) < 1e-10


    def test_35(self):
        x = np.arange(20).reshape((4, 5))
        y = util.rolling_window(x, (3, 3))
        assert y.shape == (3, 3, 2, 3)
        assert y[-1, -1, -1, -1] == 19


    def test_36(self):
        x = np.arange(20).reshape((4, 5))
        y = util.subsample_array(x, (2, 2), pad=True)
        assert y.shape == (2, 2, 2, 3)
        assert y[0, 0, -1, -1] == 14


    def test_37(self):
        x = np.arange(0, 11).astype(np.float32)
        m0 = 2.0
        c0 = 1.0
        y0 = m0 * x + c0
        y = y0.copy()
        y[4] += 2.0
        A = np.vstack([x, np.ones(x.shape[0:])]).T
        m1, c1 = util.lstabsdev(A, y)
        assert(np.abs(m0 - m1) < 1e-5)
        assert(np.abs(c0 - c1) < 1e-5)


    def test_38(self):
        x = np.arange(0, 11).astype(np.float32)
        m0 = 2.0
        c0 = 1.0
        y0 = m0 * x + c0
        y = y0.copy()
        y[0::2] += 2.0
        y[1::2] -= 2.0
        A = np.vstack([x, np.ones(x.shape[0:])]).T
        m1, c1 = util.lstmaxdev(A, y)
        assert(np.abs(m0 - m1) < 1e-5)
        assert(np.abs(c0 - c1) < 1e-5)


    def test_39(self):
        B0 = np.arange(1, 7).reshape(3, 2)
        C0 = np.arange(1, 5).reshape(2, 2)
        A0 = np.kron(B0, C0)
        B, C = util.nkp(A0, B0.shape, C0.shape)
        assert(metric.mse(A0, np.kron(B, C)) < 1e-12)
        r = B0[0, 0] / B[0, 0]
        B *= r
        C /= r
        assert(metric.mse(B0, B) < 1e-12)
        assert(metric.mse(C0, C) < 1e-12)


    def test_40(self):
        B0 = np.random.randn(3, 5, 2)
        C0 = np.random.randn(4, 6, 2)
        A0 = kronsum(np.ones((2,)), B0, C0)
        S, B, C = util.kpsvd(A0, B0.shape[0:2], C0.shape[0:2])
        A = kronsum(S, B[..., 0:2], C[..., 0:2])
        assert(metric.mse(A0, A) < 1e-12)
