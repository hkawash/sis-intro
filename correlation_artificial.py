# %%
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

plt.rc('text', usetex=True)
# plt.rc('text', usetex=False)

DSTDIR = 'fig_b'

index = [str(x) for x in range(1, 6)]
columns = ['Math', 'Physics']
# index = ['A', 'B', 'C', 'D', 'E']
df = pd.DataFrame([
    [80, 84],
    [46, 70],
    [30, 40],
    [47, 50],
    [72, 56]
    # [5, 5],
    # [2, 4],
    # [1, 1],
    # [3, 2],
    # [4, 3]
], columns=columns, index=index)

xm, ym = df.mean()
print(xm, ym)
corr = df.corr()
print(corr)
pearsonr = stats.pearsonr(df[columns[0]], df[columns[1]])
spearmanr = stats.spearmanr(df[columns[0]], df[columns[1]])
print("scipy.stats.pearsonr = {}".format(pearsonr))  # r, p-value
print("scipy.stats.spearmanr = {}".format(spearmanr))  # r, p-value

x_name = df.columns[0]
y_name = df.columns[1]
ax = df.plot(kind='scatter', color='r', x=x_name, y=y_name, figsize=(4.6, 4))
ax.set_xlim([0, 100])
ax.set_ylim([0, 100])

# 平均の線
ax.axvline(xm, linewidth=0.5, linestyle='dashed')
ax.axhline(ym, linewidth=0.5, linestyle='dashed')
# 各点のIDと座標
for i, row in df.iterrows():
    x = row[x_name]
    y = row[y_name]
    ax.annotate(r'\textbf {} ({}, {})'.format(i, x, y), xy=(x - 3, y - 7), size=12)
# 平均回りの第I-IV象限
ax.annotate(r'I', xy=(95, 95), size=16, color='#cc0000')
ax.annotate(r'II', xy=(5, 95), size=16, color='#0066cc')
ax.annotate(r'III', xy=(5, 5), size=16, color='#cc0000')
ax.annotate(r'IV', xy=(95, 5), size=16, color='#0066cc')
# 平均の線
ax.annotate(r'$\bar x = {:.0f}$'.format(xm), xy=(xm + 2, 5), size=12)
ax.annotate(r'$\bar y = {:.0f}$'.format(ym), xy=(5, ym - 5), size=12)
# 点Aの偏差を表す線
xA = df.iloc[0, 0]
yA = df.iloc[0, 1]
p = plt.Line2D(xdata=(xA, xm), ydata=(yA, yA), color='k', linewidth=0.5, linestyle='dotted')
ax.add_line(p)
p = plt.Line2D(xdata=(xA, xA), ydata=(yA, ym), color='k', linewidth=0.5, linestyle='dotted')
ax.add_line(p)
# 偏差の説明
ax.annotate(r'$x_1 - \bar x = {:.0f}-{:.0f} > 0$'.format(xA, xm), xy=((xm + xA)/2 - 8, yA + 2), size=12)
ax.annotate(r'$y_1 - \bar y = {:.0f}-{:.0f} > 0$'.format(yA, ym), xy=(xA + 2, (yA + ym)/2 - 6), size=12)

plt.gca().spines['right'].set_visible(False)
plt.gca().spines['top'].set_visible(False)
pdfpath = DSTDIR + '/corr-artificial.pdf'
plt.savefig(pdfpath, bbox_inches='tight')
plt.savefig(pdfpath.replace('pdf', 'png'), bbox_inches='tight')
plt.show()
