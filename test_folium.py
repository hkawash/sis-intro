# https://www.monotalk.xyz/blog/python-folinum-%E3%82%92%E4%BD%BF%E3%81%84%E9%83%BD%E9%81%93%E5%BA%9C%E7%9C%8C%E3%81%AE%E5%A4%AB%E5%A9%A6%E5%B9%B4%E9%BD%A2%E5%B7%AE%E3%82%92%E3%83%97%E3%83%AD%E3%83%83%E3%83%88%E3%81%99%E3%82%8B/
# https://qiita.com/sasaki_K_sasaki/items/cbe6cd8b85c6a0e62ff3
# https://github.com/niiyz/JapanCityGeoJson
# https://github.com/dataofjapan/land  (japan.topojson)
# https://qiita.com/pork_steak/items/f551fa09794831100faa
# https://qiita.com/ran/items/d88c5126362576be3291 (topojsonの作り方)
# https://qiita.com/pma1013/items/20ac475d3c0d7a7778ac (アイコン情報)
# などを参考に

import folium
import json


copyright_st = '&copy; ' \
            'Map tiles by <a href="http://stamen.com">Stamen Design</a>,' \
            ' under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>.' \
            'Data by <a href="http://openstreetmap.org">OpenStreetMap</a>,' \
            'under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.'

japan_location = [35, 135]
m = folium.Map(location=japan_location,
               attr=copyright_st,
               tiles='https://stamen-tiles-{s}.a.ssl.fastly.net/toner-lite/{z}/{x}/{y}.png',
               zoom_starts=1)
# m = folium.Map(location=japan_location)
# geojson = json.load(open('./japan.geojson'))
# m.choropleth(geo_path=geojson)
# folium.Choropleth(geo_data=geojson).add_to(m)

folium.Marker([35.681167, 139.767052], popup='<i>東京駅</i>').add_to(m)
folium.Marker([35.697914, 139.413741], popup='<b>立川駅</b>').add_to(m)

# #データ
# data_path = './japan.topojson'

# #TopoJson読み込み
# #object_pathはTopoJson内の読み込み先を指定すること
# folium.TopoJson(
#     data=open(data_path, encoding='utf-8'),
#     object_path='objects.japan',
#     name="topojson"
# ).add_to(m)

# folium.LayerControl().add_to(m)

m.save(outfile='map.html')
