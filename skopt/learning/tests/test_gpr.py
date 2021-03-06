import numpy as np

from sklearn.gaussian_process.kernels import RBF
from sklearn.gaussian_process.kernels import Matern
from sklearn.gaussian_process.kernels import WhiteKernel
from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_false
from sklearn.utils.testing import assert_true
from sklearn.utils.testing import assert_array_equal

from skopt.learning import GaussianProcessRegressor
from skopt.learning.gpr import _param_for_white_kernel_in_Sum

rng = np.random.RandomState(0)
X = rng.randn(5, 5)
y = rng.randn(5)

rbf = RBF()
wk = WhiteKernel()
mat = Matern()
kernel1 = rbf
kernel2 = mat + rbf
kernel3 = mat * rbf
kernel4 = wk * rbf
kernel5 = mat + rbf * wk


def test_param_for_white_kernel_in_Sum():
    for kernel in [kernel1, kernel2, kernel3, kernel4]:
        kernel_with_noise = kernel + wk
        wk_present, wk_param = _param_for_white_kernel_in_Sum(kernel + wk)
        assert_true(wk_present)
        kernel_with_noise.set_params(
            **{wk_param: WhiteKernel(noise_level=0.0)})
        assert_array_equal(kernel_with_noise(X), kernel(X))

    assert_false(_param_for_white_kernel_in_Sum(kernel5)[0])


def test_noise_equals_gaussian():
    gpr1 = GaussianProcessRegressor(rbf + wk).fit(X, y)

    # gpr2 sets the noise component to zero at predict time.
    gpr2 = GaussianProcessRegressor(rbf, noise="gaussian").fit(X, y)
    assert_false(gpr1.noise_)
    assert_true(gpr2.noise_)
    assert_equal(gpr1.kernel_.k2.noise_level, gpr2.noise_)
    mean1, std1 = gpr1.predict(X, return_std=True)
    mean2, std2 = gpr2.predict(X, return_std=True)
    assert_array_equal(mean1, mean2)
    assert_false(np.any(std1 == std2))
