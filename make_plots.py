import sys

import dask
from dask import array
from dask.array import stats
from dask.diagnostics import ProgressBar
from matplotlib import pyplot as plt
import numpy as np

n = int(sys.argv[1])

pbar = ProgressBar()
pbar.register()

unmasked_data1 = array.from_zarr(f'data/{n}_unmasked_fixed.zarr')
unmasked_data2 = array.from_zarr(f'data/{n}_unmasked_random.zarr')

masked_data1 = array.from_zarr(f'data/{n}_masked_fixed.zarr')
masked_data2 = array.from_zarr(f'data/{n}_masked_random.zarr')

unmasked_computation = np.abs(stats.ttest_ind(unmasked_data1, unmasked_data2, equal_var=False)[0])
masked_computation = np.abs(stats.ttest_ind(masked_data1, masked_data2, equal_var=False)[0])

unmasked_statistic, masked_statistic = dask.compute(unmasked_computation, masked_computation)

biggest = max(unmasked_statistic.max(), masked_statistic.max())

plt.plot(unmasked_statistic)
plt.axis([0, len(unmasked_statistic), 0, biggest])
plt.savefig(f"plots/{n}_unmasked.png")

plt.clf()

plt.plot(masked_statistic)
plt.axis([0, len(masked_statistic), 0, biggest])
plt.savefig(f"plots/{n}_masked.png")
