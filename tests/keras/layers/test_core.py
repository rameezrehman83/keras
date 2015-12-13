import pytest
import numpy as np
from numpy.testing import assert_allclose

from keras import backend as K
from keras.layers import core


def test_input_output():
    nb_samples = 10
    input_dim = 5
    layer = core.Layer()

    # Once an input is provided, it should be reachable through the
    # appropriate getters
    input = np.ones((nb_samples, input_dim))
    layer.input = K.variable(input)
    for train in [True, False]:
        assert_allclose(K.eval(layer.get_input(train)), input)
        assert_allclose(K.eval(layer.get_output(train)), input)


def test_connections():
    nb_samples = 10
    input_dim = 5
    layer1 = core.Layer()
    layer2 = core.Layer()

    input = np.ones((nb_samples, input_dim))
    layer1.input = K.variable(input)

    # After connecting, input of layer1 should be passed through
    layer2.set_previous(layer1)
    for train in [True, False]:
        assert_allclose(K.eval(layer2.get_input(train)), input)
        assert_allclose(K.eval(layer2.get_output(train)), input)


def test_base():
    layer = core.Layer()
    _runner(layer)


def test_masked():
    layer = core.MaskedLayer()
    _runner(layer)


def test_merge():
    layer_1 = core.Layer()
    layer_2 = core.Layer()
    layer_1.set_input_shape((None,))
    layer_2.set_input_shape((None,))
    layer = core.Merge([layer_1, layer_2])
    _runner(layer)


def test_dropout():
    layer = core.Dropout(0.5)
    _runner(layer)


def test_activation():
    layer = core.Activation('linear')
    _runner(layer)


def test_reshape():
    layer = core.Reshape(dims=(10, 10))
    _runner(layer)


def test_flatten():
    layer = core.Flatten()
    _runner(layer)


def test_repeat_vector():
    layer = core.RepeatVector(10)
    _runner(layer)


def test_dense():
    layer = core.Dense(10, input_shape=(10,))
    _runner(layer)


def test_act_reg():
    layer = core.ActivityRegularization(0.5, 0.5)
    _runner(layer)


def test_time_dist_dense():
    layer = core.TimeDistributedDense(10, input_shape=(None, 10))
    _runner(layer)


def test_time_dist_merge():
    layer = core.TimeDistributedMerge()
    _runner(layer)


def test_autoencoder():
    layer_1 = core.Layer()
    layer_2 = core.Layer()

    layer = core.AutoEncoder(layer_1, layer_2)
    _runner(layer)


def test_maxout_dense():
    layer = core.MaxoutDense(10, 10, input_shape=(20,))
    _runner(layer)


@pytest.mark.skipif(K._BACKEND == 'tensorflow',
                    reason='currently not working with TensorFlow')
def test_sequences():
    '''Test masking sequences with zeroes as padding'''
    # integer inputs, one per timestep, like embeddings
    layer = core.Masking()
    func = K.function([layer.input], [layer.get_output_mask()])
    input_data = np.array([[[1], [2], [3], [0]],
                          [[0], [4], [5], [0]]], dtype=np.int32)

    # This is the expected output mask, one dimension less
    expected = np.array([[1, 1, 1, 0], [0, 1, 1, 0]])

    # get mask for this input
    output = func([input_data])[0]
    assert np.all(output == expected), 'Output not as expected'


@pytest.mark.skipif(K._BACKEND == 'tensorflow',
                    reason='currently not working with TensorFlow')
def test_non_zero():
    '''Test masking with non-zero mask value'''
    layer = core.Masking(5)
    func = K.function([layer.input], [layer.get_output_mask()])
    input_data = np.array([[[1, 1], [2, 1], [3, 1], [5, 5]],
                          [[1, 5], [5, 0], [0, 0], [0, 0]]],
                          dtype=np.int32)
    output = func([input_data])[0]
    expected = np.array([[1, 1, 1, 0], [1, 1, 1, 1]])
    assert np.all(output == expected), 'Output not as expected'


@pytest.mark.skipif(K._BACKEND == 'tensorflow',
                    reason='currently not working with TensorFlow')
def test_non_zero_output():
    '''Test output of masking layer with non-zero mask value'''
    layer = core.Masking(5)
    func = K.function([layer.input], [layer.get_output()])

    input_data = np.array([[[1, 1], [2, 1], [3, 1], [5, 5]],
                          [[1, 5], [5, 0], [0, 0], [0, 0]]],
                          dtype=np.int32)
    output = func([input_data])[0]
    expected = np.array([[[1, 1], [2, 1], [3, 1], [0, 0]],
                        [[1, 5], [5, 0], [0, 0], [0, 0]]])
    assert np.all(output == expected), 'Output not as expected'


def _runner(layer):
    assert isinstance(layer, core.Layer)
    layer.build()
    conf = layer.get_config()
    assert (type(conf) == dict)

    param = layer.get_params()
    # Typically a list or a tuple, but may be any iterable
    assert hasattr(param, '__iter__')

    # Test the setter for the trainable attribute
    layer.trainable = True
    layer.trainable = False

if __name__ == '__main__':
    pytest.main([__file__])

