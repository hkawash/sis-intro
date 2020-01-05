# %%
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

x = np.arange(-2, 3)
print(x)
y = x**2
print(y)

xy = np.array([x, y])
print(xy)


# %%
pearsonr = stats.pearsonr(x, y)
spearmanr = stats.spearmanr(x, y)
print("scipy.stats.pearsonr = {}".format(pearsonr))  # r, p-value
print("scipy.stats.spearmanr = {}".format(spearmanr))  # r, p-value

plt.plot(x, y, 'o')
plt.show()
