# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.colors import ListedColormap# %

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import statsmodels.api as sm
# import statsmodels.formula.api as smf

# %%
DSTDIR = 'fig_pstats'

encoding = 'shift_JIS'
csvpath = DSTDIR + '/corr-temp-df3_200901-201812.csv'

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
x12 = df[[x1label, x2label]]


# %% 他のプログラムでの利用のために出力
label_dict = {  # 目的変数の候補
    '347 ゼリー【円/日】': 'e_jelly',
    '348 プリン【円/日】': 'e_pudding',
    '349 キャンデー【円/日】': 'e_candy',
    '352 チョコレート【円/日】': 'e_chocolate',
    '353 チョコレート菓子【円/日】': 'e_chocosweet',
    '356 アイスクリーム・シャーベット【円/日】': 'e_icecream',
    '日最高気温の平均(℃)': 'hitemp',
    '平均湿度(％)': 'humidity',
    'year': 'year',
    'month': 'month'
}
print("save df2 to csv... ", label_dict.keys())
df2 = df[label_dict.keys()]
df2.columns = label_dict.values()
df2.to_csv(DSTDIR + '/multreg.csv', encoding=encoding, index=False)

# %%
def print_result(model, x, y):
  """ sklearnで線形回帰した結果を表示 """
  print("coef= ", end='')
  for i in range(len(model.coef_[0])):
      print("{:.4f}, ".format(model.coef_[0][i]), end='')
  print(" intercept= {:.2f}, score= {:.3f}" \
        .format(model.intercept_[0], model.score(x, y)))


# sklearn で回帰
# 平均最高気温
model_lr1 = LinearRegression()
model_lr1.fit(x1, y)
print_result(model_lr1, x1, y)

# 年
model_lr2 = LinearRegression()
model_lr2.fit(x2, y)
print_result(model_lr2, x2, y)

# 両方利用
model_lr12 = LinearRegression()
model_lr12.fit(x12, y)
print_result(model_lr12, x12, y)


# % 散布図
def DarkPaired():
    """ 少し色を濃くしたPaired """
    darkers = [10]  # 濃くする index
    color_list = []
    cmap = cm.get_cmap('Paired')
    for i in range(12):
        color = list(cmap(i))
        if i in darkers:
            color = [x * 0.7 for x in color]
        color_list.append(color)
    return ListedColormap(color_list)

def ListedGradation(cmapname, num=10):
    """ LinearSegmentedColormap を ListedColormap へ """
    color_list = []
    cmap = cm.get_cmap(cmapname)
    for i in range(num):
        color = list(cmap(i/num))
        color_list.append(color)
    return ListedColormap(color_list)

# ListedGradation('jet', 10)

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
orig_ylim = ax.get_ylim()  # このときのylimを取得しておく

# 色なし，気温，回帰直線あり
ypred_x1 = model_lr1.predict(x1)
df['ypred_x1'] = ypred_x1
df['resid_x1'] = y - ypred_x1
ax.plot(x1, ypred_x1, linestyle='solid', color='r')
figpath = DSTDIR + '/chocosweet-temp_line.png'
set_label_others_and_savefig(x1label, ylabel, figpath)

# 色なし，気温の予測値のみ
ax = df.plot(kind='scatter', x=x1label, y='ypred_x1', figsize=(6,6))
ax.set_ylim(orig_ylim)  # ylimをオリジナルに合わせる
figpath = DSTDIR + '/chocosweet-temp_pred.png'
set_label_others_and_savefig(x1label, ylabel, figpath)

# 色なし，気温，残差
ax = df.plot(kind='scatter', x=x1label, y='resid_x1', figsize=(6,6))
ax.plot(x1, np.zeros(x1.shape[0]), linestyle='solid', color='r')
ax.set_ylim([-2, 2])
resid_ylim = ax.get_ylim()
figpath = DSTDIR + '/chocosweet-temp_residual.png'
set_label_others_and_savefig(x1label, '残差', figpath)

# 色なし，年
ax = df.plot(kind='scatter', x=x2label, y=ylabel, figsize=(6,6))
figpath = DSTDIR + '/chocosweet-year.png'
set_label_others_and_savefig(x2label, ylabel, figpath)

# 年の色あり
ax = df.plot(kind='scatter', x=x1label, y=ylabel, c=df['year'],
             cmap=ListedGradation('cividis', 11), figsize=(8,6))  # cool, winter, viridis
figpath = DSTDIR + '/chocosweet-temp_c-year.png'
set_label_others_and_savefig(x1label, ylabel, figpath)
# plt.scatter()

# 月の色あり
ax = df.plot(kind='scatter', x=x1label, y=ylabel, c=df['month'],
             cmap=DarkPaired(), figsize=(8,6))
figpath = DSTDIR + '/chocosweet-temp_c-month.png'
set_label_others_and_savefig(x1label, ylabel, figpath)
# plt.scatter()

plt.show()

# 重回帰での予測値
ypred_x12 = model_lr12.predict(x12)
df['ypred_x12'] = ypred_x12
df['resid_x12'] = y - ypred_x12

ax = df.plot(kind='scatter', x=x1label, y='ypred_x12', figsize=(6,6))
ax.set_ylim(orig_ylim)  # ylimをオリジナルに合わせる
figpath = DSTDIR + '/chocosweet-temp-year_pred.png'
set_label_others_and_savefig(x1label, ylabel, figpath)

# 重回帰での残差
ax = df.plot(kind='scatter', x=x1label, y='resid_x12', figsize=(6,6))
ax.plot(x1, np.zeros(x1.shape[0]), linestyle='solid', color='r')
ax.set_ylim(resid_ylim)
figpath = DSTDIR + '/chocosweet-temp-year_residual.png'
set_label_others_and_savefig(x1label, '残差', figpath)

plt.show()

#%% 各種分散 (numpy ではなく pandas なので ddof=1 は不要だが念のためつける)
print("Variance\ny_var= {:.3f}\ny_var(pred_x1)= {:.3f}\ny_var(pred_x12)= {:.3f}" \
    .format(df[ylabel].var(ddof=1), df['ypred_x1'].var(ddof=1), df['ypred_x12'].var(ddof=1)))
print("Variance\ne_var(pred_x1)= {:.3f}\ne_var(pred_x12)= {:.3f}" \
    .format(df['resid_x1'].var(ddof=1), df['resid_x12'].var(ddof=1)))
print("Coef. of Determination\nR2(pred_x1)= {:.3f}\nR2(pred_x1)= {:.3f}" \
    .format(df['ypred_x1'].var()/df[ylabel].var(),
            df['ypred_x12'].var()/df[ylabel].var()))

#%%

fig3d = plt.figure()
ax = Axes3D(fig3d)
ax.scatter(x1, x2, y)
ax.set_xlabel(x1label)
ax.set_ylabel(x2label)
ax.set_zlabel(ylabel)
plt.savefig(DSTDIR + "/3d_chocosweet-temp-year.png")
# plt.show()

mesh_x1 = np.arange(x1.min()[0], x1.max()[0], (x1.max()[0]-x1.min()[0])/20)
mesh_x2 = np.arange(x2.min()[0], x2.max()[0], (x2.max()[0]-x2.min()[0])/20)
mesh_x1, mesh_x2 = np.meshgrid(mesh_x1, mesh_x2)
mesh_y = model_lr12.coef_[0][0] * mesh_x1 + model_lr12.coef_[0][1] * mesh_x2 + model_lr12.intercept_[0]
ax.plot_wireframe(mesh_x1, mesh_x2, mesh_y, color='r')
plt.savefig(DSTDIR + "/3d_chocosweet-temp-year_plane.png")
plt.show()
# plt.scatter(x1, y)
# plt.scatter(x2, y)



#%% StatsModels
X = sm.add_constant(x12.values)
model = sm.OLS(y, X)
result = model.fit()
result.summary()

#%% 多重共線性があると言われるのは標準化していないためことが原因
"""
# print(X)
print(np.linalg.eig(np.dot(X.T, X)))
plt.scatter(X[:, 1], X[:, 2])
X2 = X[:, 1:]
ev, E = np.linalg.eig(np.dot(X2.T, X2))
print(max(ev)/min(ev))

import scipy as sp
X2z = sp.stats.zscore(X2, axis=0)
X3 = sm.add_constant(X2z)
print(np.linalg.eig(np.dot(X3.T, X3)))
model = sm.OLS(y, X3)
result = model.fit()
result.summary()
# ev, E = np.linalg.eig(np.dot(X2.T, X2))
# print(max(ev)/min(ev))

"""

# %% 多項式回帰
y_ice_label = '356 アイスクリーム・シャーベット【円/日】'

# sklearn で多項式回帰 (平均最高気温)
def poly_fit(ypf_label, degree=2):
    ypf = df[[ypf_label]]  # データ取得
    pf = PolynomialFeatures(degree=degree, include_bias=False)
    Xpf = pf.fit_transform(x1)

    model_pf = LinearRegression()
    model_pf.fit(Xpf, ypf)
    print_result(model_pf, Xpf, ypf)

    # 横軸:気温の散布図
    ax = df.plot(kind='scatter', x=x1label, y=ypf_label, figsize=(6,6))
    figpath = DSTDIR + '/icecream-temp.png'
    set_label_others_and_savefig(x1label, ypf_label, figpath)

    # 回帰曲線あり
    x1_lin = np.arange(x1.values.min(), x1.values.max(), 0.1).reshape(-1, 1)
    Xpf_lin = pf.fit_transform(x1_lin)
    ypf_pred = model_pf.predict(Xpf_lin)

    ax.plot(x1_lin, ypf_pred, color='r')
    figpath = DSTDIR + '/icecream-temp_poly{}.png'.format(degree)
    set_label_others_and_savefig(x1label, ypf_label, figpath)
    plt.show()

poly_fit(y_ice_label, 2)
poly_fit(y_ice_label, 3)
poly_fit(y_ice_label, 30)

# %% ダミー変数
y_choco_label = '352 チョコレート【円/日】'
y_jelly_label = '347 ゼリー【円/日】'

df['feb'] = df['month'].map(lambda x: '1feb' if x==2 else '0notfeb')
season_list = ['0spring', '1summer', '2fall', '3winter']  # 0-2, 3-5, ..
df['season'] = df['month'].map(lambda x: season_list[(x-3)//3])
# print(df['season'])

# Xdummy = pd.get_dummies(df[[x1label, 'feb']], drop_first=True)
Xdm = pd.get_dummies(df[[x1label, 'season']], drop_first=True)

add_interaction = False
if add_interaction:
    for i in range(3):
        colname = Xdm.columns[1+i]
        Xdm[colname + '_i'] = Xdm[Xdm.columns[0]] * Xdm[colname]
# %
# y_choco = df[[y_choco_label]]
ydm = df[[y_jelly_label]]
# print(Xdm)

model_dm = LinearRegression()
model_dm.fit(Xdm, ydm)
print_result(model_dm, Xdm, ydm)

ydm_pred = model_dm.predict(Xdm)

# 色なし，気温
ax = df.plot(kind='scatter', x=x1label, y=y_jelly_label, figsize=(6,6))
color_list = ['g', 'r', 'm', 'b']
for i in range(4):  # 各 seasonについて
    tf = df['season'] == season_list[i]
    # x1_tf = x1[tf]  # 季節に含まれる対象データ
    # print(type(x1_tf))
    ax.plot(x1[tf], ydm_pred[tf], linestyle='solid', color=color_list[i])

figpath = DSTDIR + '/jelly-temp_season{}.png' \
    .format('' if add_interaction else '-interceptonly')
set_label_others_and_savefig(x1label, y_jelly_label, figpath)
plt.show()
