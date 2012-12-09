import numpy as np
from numpy.testing import assert_raises, assert_approx_equal, \
                          assert_, run_module_suite, TestCase,\
                          assert_allclose, assert_array_equal,\
                          assert_array_almost_equal_nulp
from scipy import signal, fftpack
from scipy.signal import periodogram, welch, lombscargle


class TestPeriodogram(TestCase):
    def test_real_onesided_even(self):
        x = np.zeros(16)
        x[0] = 1
        f, p = periodogram(x)
        assert_allclose(f, np.linspace(0, 0.5, 9))
        q = np.ones(9)
        q[...,(0,-1)] /= 2.0
        q /= 8
        assert_allclose(p, q)
        
    def test_real_onesided_odd(self):
        x = np.zeros(15)
        x[0] = 1
        f, p = periodogram(x)
        assert_allclose(f, np.arange(8.0)/15.0)
        q = np.ones(8)
        q[...,(0,-1)] /= 2.0
        q *= 2.0/15.0
        assert_allclose(p, q)

    def test_real_twosided(self):
        x = np.zeros(16)
        x[0] = 1
        f, p = periodogram(x, sides='twosided')
        assert_allclose(f, fftpack.fftfreq(16, 1.0))
        assert_allclose(p, np.ones(16)/16.0)

    def test_real_spectrum(self):
        x = np.zeros(16)
        x[0] = 1
        f, p = periodogram(x, scaling='spectrum')
        g, q = periodogram(x, scaling='density')
        assert_allclose(f, np.linspace(0, 0.5, 9))
        assert_allclose(p, q/16.0) 

    def test_complex(self):
        x = np.zeros(16, np.complex128)
        x[0] = 1.0 + 2.0j
        f, p = periodogram(x)
        assert_allclose(f, fftpack.fftfreq(16, 1.0))
        assert_allclose(p, 5.0*np.ones(16)/16.0)
    
    def test_complex_one_sided(self):
        assert_raises(ValueError, periodogram, np.zeros(4, np.complex128),
                sides='onesided')

    def test_unk_sides(self):
        assert_raises(ValueError, periodogram, np.zeros(4, np.double),
                sides='threesided')

    def test_unk_scaling(self):
        assert_raises(ValueError, periodogram, np.zeros(4, np.complex128),
                scaling='foo')
    
    def test_nd_axis_m1(self):
        x = np.zeros(20, dtype=np.float64)
        x = x.reshape((2,1,10))
        x[:,:,0] = 1.0
        f, p = periodogram(x)
        assert_array_equal(p.shape, (2, 1, 6))
        assert_array_almost_equal_nulp(p[0,0,:], p[1,0,:], 60)
        f0, p0 = periodogram(x[0,0,:])
        assert_array_almost_equal_nulp(p0[np.newaxis,:], p[1,:], 60)

    def test_nd_axis_0(self):
        x = np.zeros(20, dtype=np.float64)
        x = x.reshape((10,2,1))
        x[0,:,:] = 1.0
        f, p = periodogram(x, axis=0)
        assert_array_equal(p.shape, (6,2,1))
        assert_array_almost_equal_nulp(p[:,0,0], p[:,1,0], 60)
        f0, p0 = periodogram(x[:,0,0])
        assert_array_almost_equal_nulp(p0, p[:,1,0])        

    def test_window_external(self):
        x = np.zeros(16)
        x[0] = 1
        f, p = periodogram(x, 10, 'hanning')
        win = signal.get_window('hanning', 16)
        fe, pe = periodogram(x, 10, win)
        assert_array_almost_equal_nulp(p, pe)
        assert_array_almost_equal_nulp(f, fe)


class TestWelch(TestCase):
    def test_real_onesided_even(self):
        x = np.zeros(16)
        x[0] = 1
        x[8] = 1
        f, p = welch(x, nfft=8)
        assert_allclose(f, np.linspace(0, 0.5, 5))
        assert_allclose(p, np.array([ 0.08333333,  0.15277778,  0.22222222,
            0.22222222,  0.11111111]))
        
    def test_real_onesided_odd(self):
        x = np.zeros(16)
        x[0] = 1
        x[8] = 1
        f, p = welch(x, nfft=9)
        assert_allclose(f, np.arange(5.0)/9.0)
        assert_allclose(p, np.array([ 0.15958226,  0.24193954,  0.24145223,
            0.24100919,  0.12188675]))

    def test_real_twosided(self):
        x = np.zeros(16)
        x[0] = 1
        x[8] = 1
        f, p = welch(x, nfft=8, sides='twosided')
        assert_allclose(f, fftpack.fftfreq(8, 1.0))
        assert_allclose(p, np.array([ 0.08333333,  0.07638889,  0.11111111,
            0.11111111,  0.11111111,  0.11111111,  0.11111111,  0.07638889]))

    def test_real_spectrum(self):
        x = np.zeros(16)
        x[0] = 1
        x[8] = 1
        f, p = welch(x, nfft=8, scaling='spectrum')
        assert_allclose(f, np.linspace(0, 0.5, 5))
        assert_allclose(p, np.array([ 0.015625, 0.028645833333333332,
            0.041666666666666664, 0.041666666666666664, 0.020833333333333332]))

    def test_complex(self):
        x = np.zeros(16, np.complex128)
        x[0] = 1.0 + 2.0j
        x[8] = 1.0 + 2.0j
        f, p = welch(x, nfft=8)
        assert_allclose(f, fftpack.fftfreq(8, 1.0))
        assert_allclose(p, np.array([ 0.41666667,  0.38194444,  0.55555556,
            0.55555556,  0.55555556, 0.55555556,  0.55555556,  0.38194444]))
    
    def test_complex_one_sided(self):
        assert_raises(ValueError, welch, np.zeros(4, np.complex128),
                sides='onesided')

    def test_unk_sides(self):
        assert_raises(ValueError, welch, np.zeros(4, np.double),
                sides='threesided')

    def test_unk_scaling(self):
        assert_raises(ValueError, welch, np.zeros(4, np.complex128),
                scaling='foo')
    
    def test_detrend_linear(self):
        x = np.arange(10, dtype=np.float64)+0.04
        f, p = welch(x, nfft=10, detrend='linear')
        assert_allclose(p, np.zeros_like(p), atol=1e-15)

    def test_detrend_external(self):
        x = np.arange(10, dtype=np.float64)+0.04
        f, p = welch(x, nfft=10, 
                detrend=lambda seg: signal.detrend(seg, type='l'))
        assert_allclose(p, np.zeros_like(p), atol=1e-15)

    def test_detrend_external_nd_m1(self):
        x = np.arange(40, dtype=np.float64)+0.04
        x = x.reshape((2,2,10))
        f, p = welch(x, nfft=10, 
                detrend=lambda seg: signal.detrend(seg, type='l'))
        assert_allclose(p, np.zeros_like(p), atol=1e-15)

    def test_detrend_external_nd_0(self):
        x = np.arange(20, dtype=np.float64)+0.04
        x = x.reshape((2,1,10))
        x = np.rollaxis(x, 2, 0)
        f, p = welch(x, nfft=10, axis=0,
                detrend=lambda seg: signal.detrend(seg, axis=0, type='l'))
        assert_allclose(p, np.zeros_like(p), atol=1e-15)

    def test_nd_axis_m1(self):
        x = np.arange(20, dtype=np.float64)+0.04
        x = x.reshape((2,1,10))
        f, p = welch(x, nfft=10)
        assert_array_equal(p.shape, (2, 1, 6))
        assert_array_almost_equal_nulp(p[0,0,:], p[1,0,:], 60)
        f0, p0 = welch(x[0,0,:], nfft=10)
        assert_array_almost_equal_nulp(p0[np.newaxis,:], p[1,:], 60)

    def test_nd_axis_0(self):
        x = np.arange(20, dtype=np.float64)+0.04
        x = x.reshape((10,2,1))
        f, p = welch(x, nfft=10, axis=0)
        assert_array_equal(p.shape, (6,2,1))
        assert_array_almost_equal_nulp(p[:,0,0], p[:,1,0], 60)
        f0, p0 = welch(x[:,0,0], nfft=10)
        assert_array_almost_equal_nulp(p0, p[:,1,0])        

    def test_window_external(self):
        x = np.zeros(16)
        x[0] = 1
        x[8] = 1
        f, p = welch(x, 10, 'hanning', 8)
        win = signal.get_window('hanning', 8)
        fe, pe = welch(x, 10, win, 8)
        assert_array_almost_equal_nulp(p, pe)
        assert_array_almost_equal_nulp(f, fe)


class TestLombscargle:
    def test_frequency(self):
        """Test if frequency location of peak corresponds to frequency of
        generated input signal.
        """

        # Input parameters
        ampl = 2.
        w = 1.
        phi = 0.5 * np.pi
        nin = 100
        nout = 1000
        p = 0.7 # Fraction of points to select

        # Randomly select a fraction of an array with timesteps
        np.random.seed(2353425)
        r = np.random.rand(nin)
        t = np.linspace(0.01*np.pi, 10.*np.pi, nin)[r >= p]

        # Plot a sine wave for the selected times
        x = ampl * np.sin(w*t + phi)

        # Define the array of frequencies for which to compute the periodogram
        f = np.linspace(0.01, 10., nout)

        # Calculate Lomb-Scargle periodogram
        P = lombscargle(t, x, f)

        # Check if difference between found frequency maximum and input
        # frequency is less than accuracy
        delta = f[1] - f[0]
        assert_(w - f[np.argmax(P)] < (delta/2.))

    def test_amplitude(self):
        """Test if height of peak in normalized Lomb-Scargle periodogram
        corresponds to amplitude of the generated input signal.
        """

        # Input parameters
        ampl = 2.
        w = 1.
        phi = 0.5 * np.pi
        nin = 100
        nout = 1000
        p = 0.7 # Fraction of points to select

        # Randomly select a fraction of an array with timesteps
        np.random.seed(2353425)
        r = np.random.rand(nin)
        t = np.linspace(0.01*np.pi, 10.*np.pi, nin)[r >= p]

        # Plot a sine wave for the selected times
        x = ampl * np.sin(w*t + phi)

        # Define the array of frequencies for which to compute the periodogram
        f = np.linspace(0.01, 10., nout)

        # Calculate Lomb-Scargle periodogram
        pgram = lombscargle(t, x, f)

        # Normalize
        pgram = np.sqrt(4 * pgram / t.shape[0])

        # Check if difference between found frequency maximum and input
        # frequency is less than accuracy
        assert_approx_equal(np.max(pgram), ampl, significant=2)

    def test_wrong_shape(self):
        t = np.linspace(0, 1, 1)
        x = np.linspace(0, 1, 2)
        f = np.linspace(0, 1, 3)
        assert_raises(ValueError, lombscargle, t, x, f)

    def test_zero_division(self):
        t = np.zeros(1)
        x = np.zeros(1)
        f = np.zeros(1)
        assert_raises(ZeroDivisionError, lombscargle, t, x, f)


if __name__ == "__main__":
    run_module_suite()
