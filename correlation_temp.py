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
import re

plt.rcParams["font.size"] = 16

DSTDIR = 'fig_b'
coloredmonth = False  # 月の色別: False とすると月の数字そのものをマーカーにしてプロット
# remove_month = 2
remove_month = 0  # 0 とすると除去しない

# % 気象庁データ
DATADIR = '../../data/eStat-purchase_JMA-temperature'  # パス指定
# DATADIR = './data'
skiprows = [0, 1, 2, 4]
usecols = [0, 1, 4, 7, 11]  # 降水量だけ4列であとは3列ずつ
encoding = 'shift_JIS'
csvpath = DATADIR + '/jma-data_20200103.csv'
df1 = pd.read_csv(csvpath, skiprows=skiprows, usecols=usecols, encoding=encoding)
df1 = df1.rename(columns={'日最高気温の平均(℃)' : '日最高気温の月平均 (℃)'})
print(df1)


# % e-Stat の家計調査データ
#  CSVダウンロード時にヘッダやコードなどは外してあるが，さらに列を適宜スキップ
use_newdata = True
if use_newdata:  # 2020.3月執筆時
    csvpath = DATADIR + '/FEH_00200561_200308193711.csv' 
    beg_period = 201001
    end_period = 201912
else:  # 2019講義および2020.1月執筆時
    # csvpath = DATADIR + '/FEH_00200561_190526191958.csv'
    csvpath = DATADIR + '/FEH_00200561_200103114104.csv' 
    # 執筆 2019.1 用
    beg_period = 200911
    end_period = 201910
    # 講義 2019年度 確率・統計（相関・回帰）
    # beg_period = 200901
    # end_period = 201812

num_items = 16
# usecols = [7] + [2*x + 9 for x in range(num_items)]
usecols = [3] + [x + 6 for x in range(num_items)]
# print(usecols)
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
num_addedcols = 3  # year, month, days
for i in range(icol_beg, icol_beg + num_items):
    col = df3.columns[i]
    coltmp = col.replace('【円】', ' (円/日)')
    colnew = re.sub(r'^[0-9]+ ', '', coltmp)
    # df3[col] = df3[col].str.replace(',', '').astype(float)
    df3[colnew] = df3[col] / days
# 期間を指定
# df3 = df3.query('2010 <= year <= 2019')
# 10年分 (120カ月)
# beg_period: 開始月
# end_period: 終了月
# ファイルの始めの方で定義 (since 2020.3)
df3 = df3[df3['yyyymm'].astype(int) >= beg_period]
df3 = df3[df3['yyyymm'].astype(int) <= end_period]

# %% 教科書用にデータを整理して保存
# 抽出データの列番号
mid_added_cols = 3  # year, month, daysの追加分のずれを考慮
beg_col4book = icol_beg + num_items + mid_added_cols
end_col4book = beg_col4book + num_items
cols4book = [0] + list(range(beg_col4book, end_col4book))
# print(cols4book)
# 元の列名
colnames4book_orig = ['year', 'month'] + df3.columns[cols4book].to_list()
# 簡略化した列名 : まず単位を除去
colnames4book_new = [re.sub(r' \(.+?\)', '', c) for c in colnames4book_orig]
# 名前を簡略化
replacenames4book = {
    'year': '年',
    'month': '月',
    '日最高気温の月平均': '気温',
    'アイスクリーム・シャーベット': 'アイスクリーム'
    }
for k, v in replacenames4book.items():
    colnames4book_new[colnames4book_new.index(k)] = v
# print(colnames4book_new)
df4 = df3[colnames4book_orig]
df4.columns = colnames4book_new
df4 = df4.reset_index(drop=True)
df4.to_csv(DATADIR + '/sweets-temp.csv', encoding=encoding)


# %% 散布図
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

#%
target_itemlist = range(0, 15)
separate_pdf_mono = [1, 5, 11, 12, 13, 14]  # 月を色付けしない
separate_pdf_color = [4, 5, 12]  # 月を色付けする
separate_png = range(0, 15)
# target_itemlist = [5, 12, 13, 14]
icol_xaxis = 0
icol_beg2 = icol_beg + num_items + num_addedcols 
pearsonr_list = []
spearmanr_list = []

if remove_month > 0:
    df3 = df3.query('month != @remove_month')
    # 特定月を除く場合はファイル名を変える
    fname_prefix_base = 'corr_exmon-{}_temp'.format(remove_month)
else:
    fname_prefix_base = 'corr-temp'

# 別の解析用に保存しておく
df3.to_csv(DSTDIR + '/{}-df3.csv'.format(fname_prefix_base), encoding=encoding)

month = df3['month']

fname_sub = 'c' if coloredmonth else 'txt'
with PdfPages(DSTDIR + '/corr-temp-all-{}.pdf'.format(fname_sub)) as pdfall:
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
        if coloredmonth:
            ax = df3.plot(kind='scatter', x=x_name, y=y_name, c=month, cmap=DarkPaired(), figsize=(8,6))
        else:
            ax = df3.plot(kind='scatter', x=x_name, y=y_name, color=(0, 0, 1, 0.3), figsize=(8,6))
            for index, row in df3.iterrows():
                ax.annotate(row['month'], xy=(row[x_name], row[y_name]), size=14)

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
            plt.savefig(DSTDIR + '/{}-{}.pdf'.format(fname_prefix, fname_sub), bbox_inches='tight')

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

# %%

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
    print("spurious")
    print("scipy.stats.pearsonr = {}".format(pearsonr))  # r, p-value
    print("scipy.stats.spearmanr = {}".format(spearmanr))  # r, p-value
    ax = df3.plot(kind='scatter', x=x_name, y=y_name)
    # ax.set_title("Pearson's r = {:.2f}".format(pearsonr[0]))
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.savefig(DSTDIR + '/{}-spurious_{}-{}.pdf'.format(fname_prefix_base, pair[0], pair[1]), bbox_inches='tight')
    # plt.show()
    plt.pause(.01)

