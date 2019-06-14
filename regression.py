# %%
# １回生概論「第８回 データと機械学習」 回帰の例の図作成用
# アイスクリームの購買金額と気象庁の気温データの回帰 (1次，2次)
#
# (注) matplotlib は日本語表示できるように設定されているものとする
#   (Font追加やmatplotlibrc)
# 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import calendar
from matplotlib.backends.backend_pdf import PdfPages
# import seaborn as sns
# import re

order = 1  # 線形モデルの次数を指定 (1 or 2)

# %% 気象庁データ
# DATADIR = '../../data/eStat-purchase_JMA-temperature'  # パス指定
DATADIR = './'  # このスクリプトと同じ場所に置く場合はこちら
skiprows = [0, 1, 2, 4]
usecols = [0, 1, 4, 7, 11]  # 降水量だけ4列であとは3列ずつ
encoding = 'shift_JIS'
csvpath = DATADIR + '/jma-data.csv'
df1 = pd.read_csv(csvpath, skiprows=skiprows, usecols=usecols, encoding=encoding)
# print(df1)

# %% e-Stat の家計調査データ
#  CSVダウンロード時にヘッダやコードなどを外し忘れたので適宜行や列をスキップ
skiprows = range(11)
num_items = 7
usecols = [7] + [2*x + 9 for x in range(num_items)]
# print(usecols)
csvpath = DATADIR + '/FEH_00200561_190526191958.csv'
df2 = pd.read_csv(csvpath, thousands=',', skiprows=skiprows, usecols=usecols, encoding=encoding)
# print(df2)

# %% 年月のフォーマット変換
# df1の'yyyy/m' を 'yyyymm' へ変換して新たな列へ
date_raw = df1.iloc[:, 0].values
orig_colname = df1.columns[0]
# date_ja = ['{0[0]}年{0[1]}月'.format(x.split('/')) for x in date_raw]
yyyymm = ['{0[0]}{0[1]:02}'.format(np.array(x.split('/'), dtype='int')) for x in date_raw]
df1['yyyymm'] = yyyymm
df1.drop(orig_colname, axis=1, inplace=True)

# df2の'yyyy年m月' を 'yyyymm' へ変換して新たな列へ
date_raw = df2.iloc[:, 0].values
orig_colname = df2.columns[0]
yyyymm = ['{0[0]}{0[1]:02}'.format(np.array(x.replace('月', '').split('年'), dtype='int')) for x in date_raw]
df2['yyyymm'] = yyyymm
df2.drop(orig_colname, axis=1, inplace=True)

# %% 二つのデータフレームを yyyymm にてマージ (merge or join)
df3 = pd.merge(df1, df2, on='yyyymm')
df3.replace('***', np.nan, inplace=True)
yyyymm = df3['yyyymm'].values
df3['year'] = (yyyymm.astype(int) / 100).astype(int)
df3['month'] = yyyymm.astype(int) % 100

# %% 月の日数（うるう年考慮するためモジュール利用）
days = [calendar.monthrange(df3.loc[i, 'year'], df3.loc[i, 'month'])[1] for i in df3.index]
df3['days'] = days
print(df3.columns)

# %% なぜか thousands=',' が効かないのでここで削除．ついでに日数で割る
icol_beg = 5  # 開始列
num_itemcols = 7  # 処理対象列数
num_addedcols = 3  # year, month, days
for i in range(icol_beg, icol_beg + num_itemcols):
    col = df3.columns[i]
    colnew = col.replace('円', '円/日')
    df3[col] = df3[col].str.replace(',', '').astype(float)
    df3[colnew] = df3[col] / days
# col = df3.columns[5]

# %%
icol_beg2 = icol_beg + num_itemcols + num_addedcols

# %% df3.plot()
icol_xaxis = 0
x_name = df3.columns[icol_xaxis]
y_name = df3.columns[icol_beg2]
print("x-axis: ", x_name)
print("y-axis: ", y_name)
x = df3[x_name]
y = df3[y_name]
xdata = np.linspace(x.min(), x.max(), 100)
if order == 1:
    a, b = np.polyfit(x, y, order)
    print('y = {} x + {}'.format(a, b))
    ypred = a * xdata + b
else:
    a1, a2, b = np.polyfit(x, y, order)
    print('y = {} x^2 + {} x + {}'.format(a1, a2, b))
    ypred = a1 * xdata**2 + a2 * xdata + b

# df3.plot(kind='scatter', x='u{}'.format(df3.columns[1]), y='u{}'.format(df3.columns[7]))
# %%
with PdfPages('regression.pdf') as pdf_regression:
    # sns.set_style('whitegrid')
    p = df3.plot(kind='scatter', x=x_name, y=y_name)
    ax = plt.gcf().get_axes()
    ax[0].set_ylim(5, 50)
    pdf_regression.savefig()
    plt.plot(xdata, ypred, color='r', LineWidth=2)
    pdf_regression.savefig()
    plt.show()

#%%
