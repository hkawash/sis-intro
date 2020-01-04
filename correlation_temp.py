# %%
# 菓子類 340-359
# 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import scipy as sp
from scipy import stats
import calendar
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import cm
from matplotlib.colors import ListedColormap# %
# import seaborn as sns
# import re

DSTDIR = 'fig_b'
colored = True
# remove_month = 2
remove_month = 0  # 0 とすると除去しない

# % 気象庁データ
DATADIR = '../../data/eStat-purchase_JMA-temperature'  # パス指定
# DATADIR = './data'
skiprows = [0, 1, 2, 4]
usecols = [0, 1, 4, 7, 11]  # 降水量だけ4列であとは3列ずつ
encoding = 'shift_JIS'
csvpath = DATADIR + '/jma-data.csv'
df1 = pd.read_csv(csvpath, skiprows=skiprows, usecols=usecols, encoding=encoding)
# print(df1)

# % e-Stat の家計調査データ
#  CSVダウンロード時にヘッダやコードなどは外してあるが，さらに列を適宜スキップ
num_items = 16
# usecols = [7] + [2*x + 9 for x in range(num_items)]
usecols = [3] + [x + 6 for x in range(num_items)]
# print(usecols)
# csvpath = DATADIR + '/FEH_00200561_190526191958.csv'
csvpath = DATADIR + '/FEH_00200561_200103114104.csv'
# df2 = pd.read_csv(csvpath, thousands=',', skiprows=skiprows, usecols=usecols, encoding=encoding)
df2 = pd.read_csv(csvpath, usecols=usecols, encoding=encoding)
# print(df2)

# % 年月のフォーマット変換
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

# % 二つのデータフレームを yyyymm にてマージ (merge or join)
df3 = pd.merge(df1, df2, on='yyyymm')
df3.replace('***', np.nan, inplace=True)
yyyymm = df3['yyyymm'].values
df3['year'] = (yyyymm.astype(int) / 100).astype(int)
df3['month'] = yyyymm.astype(int) % 100

# % 月の日数（うるう年考慮するためモジュール利用）
days = [calendar.monthrange(df3.loc[i, 'year'], df3.loc[i, 'month'])[1] for i in df3.index]
df3['days'] = days
print(df3.columns)

# 日数で割る
icol_beg = 5  # 開始列
num_itemcols = 16  # 処理対象列数
num_addedcols = 3  # year, month, days
for i in range(icol_beg, icol_beg + num_itemcols):
    col = df3.columns[i]
    colnew = col.replace('円', '円/日')
    # df3[col] = df3[col].str.replace(',', '').astype(float)
    df3[colnew] = df3[col] / days

# 期間を指定
# df3 = df3.query('2010 <= year <= 2019')
# 10年分 (120カ月)
beg_period = 200911
end_period = 201910
df3 = df3[df3['yyyymm'].astype(int) >= beg_period]
df3 = df3[df3['yyyymm'].astype(int) <= end_period]

# % 散布図
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

#%
target_itemlist = range(0, 15)
separate_pdf_mono = [1, 5, 11, 12, 13, 14]
separate_pdf_color = [4, 5, 12]
separate_png = range(0, 15)
# target_itemlist = [5, 12, 13, 14]
icol_xaxis = 0
icol_beg2 = icol_beg + num_itemcols + num_addedcols 
pearsonr_list = []
spearmanr_list = []

if remove_month > 0:
    df3 = df3.query('month != @remove_month')
    # 特定月を除く場合はファイル名を変える
    fname_prefix_base = 'corr_exmon-{}_temp'.format(remove_month)
else:
    fname_prefix_base = 'corr-temp'

month = df3['month']

with PdfPages(DSTDIR + '/corr-temp-all.pdf'.format(i)) as pdfall:
    for i in target_itemlist:
        icol_yaxis = icol_beg2 + i # %% 対象データ列の開始番号
        x_name = df3.columns[icol_xaxis]
        y_name = df3.columns[icol_yaxis]
        print("x-axis: ", x_name)
        print("y-axis: ", y_name)
        pearsonr = stats.pearsonr(df3[x_name], df3[y_name])
        spearmanr = stats.spearmanr(df3[x_name], df3[y_name])
        print("scipy.stats.pearsonr = {}".format(pearsonr))  # r, p-value
        print("scipy.stats.spearmanr = {}".format(spearmanr))  # r, p-value
        pearsonr_list.append(pearsonr)
        spearmanr_list.append(spearmanr)

        # sns.set_style('whitegrid')
        ax = df3.plot(kind='scatter', x=x_name, y=y_name, c=month, cmap=DarkPair(), figsize=(8,6))
        ax.set_title("Pearson's r = {:.2f}".format(pearsonr[0]))
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['top'].set_visible(False)
        pdfall.savefig(bbox_inches='tight')

        # ax = plt.gcf().get_axes()
        # ax[0].set_ylim(5, 50)
        fname_prefix = '{}-{:02d}'.format(fname_prefix_base, i)

        if i in separate_png:
            plt.savefig(DSTDIR + '/{}.png'.format(fname_prefix), bbox_inches='tight')

        if i in separate_pdf_color:
            plt.savefig(DSTDIR + '/{}-c.pdf'.format(fname_prefix), bbox_inches='tight')

        # plt.show()
        plt.pause(.01)

        # blue only
        if i in separate_pdf_mono:
            df3.plot(kind='scatter', x=x_name, y=y_name)
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['top'].set_visible(False)
            plt.savefig(DSTDIR + '/{}.pdf'.format(fname_prefix), bbox_inches='tight')
            # plt.show()
            plt.pause(.01)

#%% Save summary
df_summary = pd.DataFrame()
df_summary['item'] = [df3.columns[icol_beg2 + i] for i in target_itemlist]
df_summary['pearson'] = pearsonr_list
df_summary['spearman'] = spearmanr_list
df_summary.to_csv(DSTDIR + '/{}-summary.csv'.format(fname_prefix_base), encoding=encoding)

#%% みかけの相関
for pair in [(14, 11), (14, 13), (11, 13)]:
    icol_xy = [icol_beg2 + pair[i] for i in range(2)]
    x_name = df3.columns[icol_xy[0]]
    y_name = df3.columns[icol_xy[1]]
    print("x-axis: ", x_name)
    print("y-axis: ", y_name)
    pearsonr = stats.pearsonr(df3[x_name], df3[y_name])
    spearmanr = stats.spearmanr(df3[x_name], df3[y_name])

    ax = df3.plot(kind='scatter', x=x_name, y=y_name)
    # ax.set_title("Pearson's r = {:.2f}".format(pearsonr[0]))
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.savefig(DSTDIR + '/{}-spurious_{}-{}.pdf'.format(fname_prefix_base, pair[0], pair[1]), bbox_inches='tight')
    # plt.show()
    plt.pause(.01)

