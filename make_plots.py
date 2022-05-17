import sys

import dask
from dask import array
from dask.array import stats
from dask.diagnostics import ProgressBar
from matplotlib import pyplot as plt

n = int(sys.argv[1])

pbar = ProgressBar()
pbar.register()

unmasked_data1 = array.from_zarr(f'data/{n}_unmasked_fixed.zarr')
unmasked_data2 = array.from_zarr(f'data/{n}_unmasked_random.zarr')

masked_data1 = array.from_zarr(f'data/{n}_masked_fixed.zarr')
masked_data2 = array.from_zarr(f'data/{n}_masked_random.zarr')

unmasked_computation = stats.ttest_ind(unmasked_data1, unmasked_data2, equal_var=False)
masked_computation = stats.ttest_ind(masked_data1, masked_data2, equal_var=False)

(unmasked_statistic, _), (masked_statistic, _) = dask.compute(unmasked_computation, masked_computation)

plt.plot(unmasked_statistic)
plt.savefig(f"plots/{n}_unmasked.png")

plt.clf()

plt.plot(masked_statistic)
plt.savefig(f"plots/{n}_masked.png")
