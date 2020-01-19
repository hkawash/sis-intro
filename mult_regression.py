# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.colors import ListedColormap# %

from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
import statsmodels.formula.api as smf

# %%
DSTDIR = 'fig_pstats'

encoding = 'shift_JIS'
csvpath = 'fig_b/corr-temp-df3.csv'

df = pd.read_csv(csvpath, encoding=encoding, index_col=0)

"""
icol_beg = 5  # 開始列
num_itemcols = 16  # 処理対象列数
num_addedcols = 3  # year, month, days
icol_beg2 = icol_beg + num_itemcols + num_addedcols 
target_itemlist = range(0, 15)

i = 13
icol_yaxis = icol_beg2 + i # %% 対象データ列の開始番号
colname = df.columns[icol_yaxis]
# print("column: " + colname)
# y = df.iloc[:, icol_yaxis]

y = df[colname]
# print(y)
"""
ylabel = '353 チョコレート菓子【円/日】'
x1label = '日最高気温の平均(℃)'
x2label = 'year'
y = df[[ylabel]]
x1 = df[[x1label]]
x2 = df[[x2label]]
x = df[[x1label, x2label]]

# %%
model_lr1 = LinearRegression()
model_lr1.fit(x1, y)
print(model_lr1.coef_)
print(model_lr1.intercept_)
print(model_lr1.score(x1, y))

model_lr2 = LinearRegression()
model_lr2.fit(x2, y)
print(model_lr2.coef_)
print(model_lr2.intercept_)
print(model_lr2.score(x2, y))

model_lr12 = LinearRegression()
model_lr12.fit(x, y)
print(model_lr12.coef_)
print(model_lr12.intercept_)
print(model_lr12.score(x, y))


# %% 散布図
def DarkPair():
    """ 少し色を濃くする """
    darkers = [10]  # 濃くする index
    color_list = []
    cmap = cm.get_cmap('Paired')
    for i in range(12):
        color = list(cmap(i))
        if i in darkers:
            color = [x * 0.7 for x in color]
        color_list.append(color)
    return ListedColormap(color_list)


def set_label_others_and_savefig(xlabel, ylabel, figpath):
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.savefig(figpath, bbox_inches='tight')

# fig2d = plt.figure()
# 色なし，気温
ax = df.plot(kind='scatter', x=x1label, y=ylabel, figsize=(6,6))
figpath = DSTDIR + '/chocosweet-temp.png'
set_label_others_and_savefig(x1label, ylabel, figpath)

# 色なし，気温，回帰直線あり
ypred_x1 = model_lr1.predict(x1)
df['ypred_x1'] = ypred_x1
df['resid_x1'] = y - ypred_x1
ax.plot(x1, ypred_x1, linestyle='solid', color='r')
figpath = DSTDIR + '/chocosweet-temp_line.png'
set_label_others_and_savefig(x1label, ylabel, figpath)

# 色なし，気温，残差
ax = df.plot(kind='scatter', x=x1label, y='resid_x1', figsize=(6,6))
ax.plot(x1, np.zeros(x1.shape[0]), linestyle='solid', color='r')
ax.set_ylim([-3, 3])
figpath = DSTDIR + '/chocosweet-temp_residual.png'
set_label_others_and_savefig(x1label, '残差', figpath)

# 色なし，年
ax = df.plot(kind='scatter', x=x2label, y=ylabel, figsize=(6,6))
figpath = DSTDIR + '/chocosweet-year.png'
set_label_others_and_savefig(x2label, ylabel, figpath)

# 年の色あり
ax = df.plot(kind='scatter', x=x1label, y=ylabel, c=df['year'], cmap=cm.Accent, figsize=(8,6))
figpath = DSTDIR + '/chocosweet-temp_c-year.png'
set_label_others_and_savefig(x1label, ylabel, figpath)
# plt.scatter()

# 月の色あり
ax = df.plot(kind='scatter', x=x1label, y=ylabel, c=df['month'], cmap=DarkPair(), figsize=(8,6))
figpath = DSTDIR + '/chocosweet-temp_c-month.png'
set_label_others_and_savefig(x1label, ylabel, figpath)
# plt.scatter()

plt.show()

#%%

fig3d = plt.figure()
ax = Axes3D(fig3d)
ax.scatter3D(x1, x2, y)
# plt.show()

mesh_x1 = np.arange(x1.min()[0], x1.max()[0], (x1.max()[0]-x1.min()[0])/20)
mesh_x2 = np.arange(x2.min()[0], x2.max()[0], (x2.max()[0]-x2.min()[0])/20)
mesh_x1, mesh_x2 = np.meshgrid(mesh_x1, mesh_x2)
mesh_y = model.coef_[0][0] * mesh_x1 + model.coef_[0][1] * mesh_x2 + model.intercept_[0]
ax.plot_wireframe(mesh_x1, mesh_x2, mesh_y)
plt.savefig(DSTDIR + "/3d_chocosweet-temp-year.png")
plt.show()
# plt.scatter(x1, y)
# plt.scatter(x2, y)


#%% StatsModels

X = sm.add_constant(x)
model = smf.OLS(y, X)
result = model.fit()
result.summary()
