# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import japanize_matplotlib
import seaborn as sns
import itertools
import re

plt.rcParams["font.size"] = 14

DATADIR = '../../data/eStat-purchase-year-city'
DSTDIR = 'fig_b'
encoding = 'shift_JIS'

# % e-Stat の家計調査データ
skiprows = 0  # ヘッダ削除済み

use_newdata = True  # どのデータを使うか
num_items = 226  # 全品目数 (H27版)
usecols = [48, 49, 50]  # ３列選ぶ（牛，豚，鶏）
if use_newdata:  # 2020.3月執筆時
    csvpath = DATADIR + '/FEH_00200561_200308203047.csv'
    q_year_range = '2015 <= year <= 2019'
else:  # 2019講義および2020.1月執筆時
    csvpath = DATADIR + '/FEH_00200561_190604190707.csv'
    q_year_range = '2014 <= year <= 2018'

allcols = [2, 3] + [x + 5 for x in range(num_items)]  # 地域区分，年，品目・・・
# print(allcols)
df1 = pd.read_csv(csvpath, thousands=',', skiprows=skiprows, usecols=allcols, encoding=encoding)
# print(df1)

# %%
# 列追加前にrawデータと列名を取得
city_raw = df1.iloc[:, 0]
orig_city_colname = df1.columns[0]
year_raw = df1.iloc[:, 1]
orig_year_colname = df1.columns[1]

# %% 都市名と年次を整形
# 都市名のコードを削除
# city_new = city_raw.str.extract('[0-9 ]*(.+)', expand=False)  # これもOK
# city_new = city_raw.replace('[0-9 ]*(.+)', r'\1', regex=True)  # これもOK
city_new = city_raw.str.replace('[0-9 ]*(.+)', r'\1')
jiscode = city_raw.str.replace('([0-9]*) *.+', r'\1')  # 0から始まるものもあるのでintにしてしまう
# %print(city_new)
# str アクセサを使わず直接 replaceすれば inplace で置換できるはずだが，いったん列を作る
df1['city'] = city_new
df1['jiscode'] = jiscode
df1.drop(orig_city_colname, axis=1, inplace=True)
# 年次の「年」を削除してintへ
# year_new = year_raw.replace('年', '')  # これはだめ
year_new = year_raw.str.replace('年', '').astype(int)
# print(year_new)
df1['year'] = year_new
df1.drop(orig_year_colname, axis=1, inplace=True)

# %% 年の抽出，集計
# df2 = df1[df1['year'] >= 2016]  # 年の抽出
df2 = df1.query(q_year_range)

rows_to_drop = df2.index[df2['city'] == '全国']  # 「全国」の除外
df2 = df2.drop(rows_to_drop)

df2['jiscode'] = df2['jiscode'].astype(int)  # あとで数値として比較する & groupby対策で intへ変換

groupby = df2.groupby('city')  # 複数年の平均
df2 = groupby.mean()

# df2 = (df2 - df2.mean()) / df2.std(ddof=0)  # 標準化

#%% 全アイテムを一応保存しておく
df2.to_csv(DATADIR + '/city-allitem.csv', encoding=encoding)

# %% 列を選択してクラスタリング
# usecols = [16, 47, 48]  # 肉をよく食べると牛肉をよく食べるは相関あり．魚とは相関なし
# collist = [16, 47]  # 魚 vs 肉
# df2.columns[usecols]
df3 = df2[df2.columns[usecols]]

print(df3.corr())

# fig, ax = plt.subplots(1, 1, figsize=(10, 8))
sns.pairplot(df3)
# plt.tight_layout()
plt.savefig('pairplot-meat.pdf', bbox_inches='tight')
plt.show()

# %% 教科書用にデータをさらに整理して保存
# JISコード順にしてから抽出
df4 = df2.sort_values('jiscode', ascending=True)[df2.columns[usecols]]
# df4.shape
df4.columns = ['牛肉', '豚肉', '鶏肉']
# df4
df4.to_csv(DATADIR + '/city-meat.csv', encoding=encoding)


# %%
# % 散布図で確認
for colpair in itertools.combinations(usecols, 2):
    pdfpath = DSTDIR + '/corr-meat{}-{}.pdf'.format(colpair[0], colpair[1])
    with PdfPages(pdfpath) as pdf:
        colname = [df2.columns[c] for c in colpair]
        # fig, ax = plt.subplots(1, 1, figsize=(8,8), aspect='equal')
        # plt.figure()
        # fig = plt.figure(figsize=(8,8))
        # fig.add_subplot(aspect='equal')
        # c=pred, cmap='brg', 
        # ax = df2.plot(kind='scatter', x=colname[0], y=colname[1], colorbar=False)
        ax = df2.plot(kind='scatter', x=colname[0], y=colname[1], colorbar=False, figsize=(6, 6))
        for index, row in df2.iterrows():
            # ax.annotate(row['city'], xy=(row[colname[0]], row[colname[1]]), size=6)
            ax.annotate(index, xy=(row[colname[0]], row[colname[1]]), size=8)
            # ax.colorbar()
        ax.set_xlabel(re.sub(r'^[0-9]+ ', '', colname[0]).replace('【1g】', ' (g)'))
        ax.set_ylabel(re.sub(r'^[0-9]+ ', '', colname[1]).replace('【1g】', ' (g)'))
        # ax.set_aspect('equal', 'datalim')
        # ax.set_aspect('equal')
        # ax.set_aspect(1)
        # plt.gca().set_aspect('equal', adjustable='box')
        # ax.axis('scaled')
        # plt.tight_layout()
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['top'].set_visible(False)
        pdf.savefig(bbox_inches='tight')
        plt.savefig(pdfpath.replace('pdf', 'png'), bbox_inches='tight')
        plt.show()


print(len(df3.index))
# %%
