# %%
# １回生概論「第８回 データと機械学習」 クラスタリングの例の図作成用
# e-Stat の家計調査データを使用
# 牛肉，豚肉，鶏肉の購入量 (g) によって日本の都市（政令指定都市，顕著所在市）をクラスタリング
# 都市の座標には，アマノ技研様のデータを使用 https://amano-tec.com/data/localgovernments.html
#
# (注) matplotlib は日本語表示できるように設定されているものとする
#   (Font追加やmatplotlibrc)
# 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from matplotlib.backends.backend_pdf import PdfPages
import folium
import itertools
import japanize_matplotlib
# import seaborn as sns
# import re

DATADIR = '../../data/eStat-purchase-year-city'
encoding = 'shift_JIS'

# % e-Stat の家計調査データ
skiprows = 0  # ヘッダ削除済み
num_items = 226  # まずは全ての列
usecols = [2, 3] + [x + 5 for x in range(num_items)]  # 地域区分，年，品目・・・
# print(usecols)
csvpath = DATADIR + '/FEH_0020056190604190707.csv'
df1 = pd.read_csv(csvpath, thousands=',', skiprows=skiprows, usecols=usecols, encoding=encoding)
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
df2 = df1.query('2014 <= year <= 2018')

rows_to_drop = df2.index[df2['city'] == '全国']  # 「全国」の除外
df2 = df2.drop(rows_to_drop)

df2['jiscode'] = df2['jiscode'].astype(int)  # あとで数値として比較する & groupby対策で intへ変換

groupby = df2.groupby('city')  # 複数年の平均
df2 = groupby.mean()

# df2 = (df2 - df2.mean()) / df2.std(ddof=0)  # 標準化


# %% 列を選択してクラスタリング
usecols = [48, 49, 50]  # ３列選ぶ
# collist = [16, 47]  # 魚 vs 肉
data_for_kmeans = df2.iloc[:, usecols].values
pred = KMeans(n_clusters=3).fit_predict(data_for_kmeans)
print(pred)
df2['cluster'] = pred

# % 散布図で確認
with PdfPages('clustering.pdf') as pdf_clustering:
    for colpair in itertools.combinations(usecols, 2):
        colname = [df2.columns[c] for c in colpair]

        ax = df2.plot(kind='scatter', x=colname[0], y=colname[1], c=pred, cmap='brg', colorbar=False)
        for index, row in df2.iterrows():
            # ax.annotate(row['city'], xy=(row[colname[0]], row[colname[1]]), size=6)
            ax.annotate(index, xy=(row[colname[0]], row[colname[1]]), size=5) 
            # ax.colorbar()       
        # ax.set_aspect('equal', 'datalim')
        ax.axis('scaled')

        pdf_clustering.savefig()


# %%
# 3次元散布図
from mpl_toolkits.mplot3d import Axes3D
colname = [df2.columns[c] for c in usecols]  # 3軸のデータの各列名

for color_flag in [False, True]:
    fig3d = plt.figure()
    ax3d = Axes3D(fig3d)
    ax3d.set_xlabel(colname[0])
    ax3d.set_ylabel(colname[1])
    ax3d.set_zlabel(colname[2])
    if color_flag:
        ax3d.scatter(df2[colname[0]], df2[colname[1]], df2[colname[2]], c=pred, cmap='brg')
        figname = 'plot3d_clustering'
    else:
        ax3d.scatter(df2[colname[0]], df2[colname[1]], df2[colname[2]])
        figname = 'plot3d_original'
    # plt.show()
    plt.savefig(figname + '.png')
    plt.savefig(figname + '.pdf')




# %% 地図上にプロット ------------------------------

csvpath = DATADIR + '/h3010puboffice_sjis.csv'  # 経度・緯度情報読み込み
gis_df = pd.read_table(csvpath, encoding=encoding)

# 地図作成
copyright_st = '&copy; ' \
            'Map tiles by <a href="http://stamen.com">Stamen Design</a>,' \
            ' under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>.' \
            'Data by <a href="http://openstreetmap.org">OpenStreetMap</a>,' \
            'under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.'

center_location = [35, 135]  # 明石市
m = folium.Map(location=center_location,
               attr=copyright_st,
               tiles='https://stamen-tiles-{s}.a.ssl.fastly.net/toner-lite/{z}/{x}/{y}.png',
               zoom_starts=4)

# %% マーカーを立てていく
colors = ['blue', 'red', 'green']

for index, row in df2.iterrows():
    # print(row['jiscode'])
    jcode = row['jiscode']
    if jcode == 13100:
        jcode = 13101  # 東京都特別区 -> 東京都千代田区
    tmp_df = gis_df.query('jiscode == @jcode')
    # print([index, tmp_df['name'].values[0]])
    latlon = [tmp_df['lat'].values[0], tmp_df['lon'].values[0]]
    vals = row.iloc[usecols].astype(str).tolist()  # データ
    names = ['牛', '豚', '鶏']
    name_and_vals = [n + ': ' + v for n, v in zip(names, vals)]
    popup = '<b>' + '<br />'.join([index] + name_and_vals) + '</b>'
    print(popup)
    # print(latlon)
    # print(row['cluster'])  # クラスタリング結果
    folium.Marker(latlon,
                  popup=popup,
                  icon=folium.Icon(color=colors[int(row['cluster'])], icon='info-sign')
                  ).add_to(m)


m.save(outfile='map-clustering.html')


