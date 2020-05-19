import oneflow as flow
import numpy as np
from collections import OrderedDict

from test_util import GenArgList
import test_global_storage

func_config = flow.FunctionConfig()
func_config.default_data_type(flow.float)
func_config.default_distribute_strategy(flow.distribute.consistent_strategy())


def _check(test_case, data, segment_ids, out_shape, out):
    test_case.assertEqual(out.shape, out_shape)
    ref = np.zeros_like(out)
    for idx, i in np.ndenumerate(segment_ids):
        out_idx = list(idx)
        out_idx[-1] = i
        out_idx=tuple(out_idx)
        ref[out_idx] += data[idx]
    test_case.assertTrue(np.allclose(ref, out, atol=1e-5, rtol=1e-5))

def _check_bw(test_case, params, indices, out_shape, out):
    ref = np.zeros_like(out)
    for idx, i in np.ndenumerate(indices):
        in_idx = list(idx)
        in_idx[-1] = i
        in_idx=tuple(in_idx)
        ref[idx] += params[in_idx]
    test_case.assertTrue(np.array_equal(ref, out))


def _gen_segment_ids(out_shape, num_segments, segment_ids_shape):
    axis = len(segment_ids_shape) - 1
    return np.random.randint(low=0, high=out_shape[axis], size=segment_ids_shape,
            dtype=np.int32)


def _gen_data(out_shape, num_segments, segment_ids_shape):
    axis = len(segment_ids_shape) - 1
    data_shape = out_shape[0:axis] + (segment_ids_shape[axis],) + out_shape[axis + 1:]
    return np.random.rand(*data_shape).astype(np.float32)

def _make_unsoted_segment_sum_fn(device, data, segment_ids, num_segments):
    flow.clear_default_session()
    func_config.train.primary_lr(1e-3)
    func_config.train.model_update_conf(dict(naive_conf={}))

    @flow.function(func_config)
    def unsorted_batch_segment_sum_job(
        data=flow.FixedTensorDef(data.shape, dtype=flow.float),
        segment_ids=flow.FixedTensorDef(segment_ids.shape, dtype=flow.int32)):
        with flow.fixed_placement(device, "0:0"):
            x = flow.get_variable(
                    "data",
                    shape=data.shape,
                    dtype=flow.float32,
                    initializer=flow.constant_initializer(0),
                    )
            data = x + data
            res = flow.math.unsorted_batch_segment_sum(data=data,
                    segment_ids=segment_ids,
                    num_segments=num_segments)
            flow.losses.add_loss(res)
            flow.watch_diff(x, test_global_storage.Setter("x_diff"))
            flow.watch_diff(res, test_global_storage.Setter("loss_diff"))
            return res

    return unsorted_batch_segment_sum_job(data, segment_ids)

def _run_test(test_case, device, out_shape, num_segments, segment_ids_shape):
    segment_ids = _gen_segment_ids(out_shape, num_segments, segment_ids_shape)
    data = _gen_data(out_shape, num_segments, segment_ids_shape)

    unsorted_batch_segment_sum_out = _make_unsoted_segment_sum_fn(device, data,
            segment_ids, num_segments).get()
    out_ndarray = unsorted_batch_segment_sum_out.ndarray()
    grad_in_ndarray = test_global_storage.Get("x_diff")
    grad_out_ndarray = test_global_storage.Get("loss_diff")
    check_point  = flow.train.CheckPoint()
    check_point.init()

    _check(test_case, data, segment_ids, out_shape, out_ndarray)
    _check_bw(test_case, grad_out_ndarray, segment_ids, grad_in_ndarray.shape, grad_in_ndarray)

def test_unsorted_batch_segment_sum(test_case):
    arg_dict = OrderedDict()
    arg_dict['device_type'] = ['cpu', 'gpu']
    arg_dict['out_shape'] = [(2, 4, 7, 6)]
    arg_dict['num_segments'] = [7]
    arg_dict['segment_ids_shape'] = [(2, 4, 5)]
    for arg in GenArgList(arg_dict):
        _run_test(test_case, *arg)