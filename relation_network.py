# %%
import pygraphviz as pgv
import networkx as nx

DSTDIR = 'fig_b'

G = nx.DiGraph()

# 小文字の label にすれば Graphviz 側でラベルとして認識される
# Gephi 側では大文字・小文字どちらでもOK
G.add_edges_from([('キャンデー', 'チョコレート菓子', {'label': '0.69'})])
G.add_edges_from([('気温', 'キャンデー', {'label': '-0.79'})])
G.add_edges_from([('気温', 'チョコレート菓子', {'label': '-0.73   '})])
# print(list(G.nodes))

# 属性を追加することも可能
# G.node['ノード1']['style'] = 'solid,filled'
# G.node['ノード1']['fillcolor'] = '#ccccff'
# G.node['ノード1']['shape'] = 'egg'

# G.node['ノード2']['color'] = '#ff9999'
# G.node['ノード2']['fontcolor'] = 'red'

G.edges['キャンデー', 'チョコレート菓子']['style'] = 'dotted'
G.edges['キャンデー', 'チョコレート菓子']['dir'] = 'none'

# G.edges['気温', 'チョコレート菓子']['labeldistance'] = 5
# G.edges['ノード1', 'ノード2']['fontsize'] = 10
# G.edges['ノード1', 'ノード2']['fontcolor'] = '#00cc66'

# nx.write_graphml(G, "test.graphml")  # Gephi 用に GraphML ファイルを出力

# GraphViz用にAGraphへ変換して描画
ag = nx.nx_agraph.to_agraph(G)
ag.node_attr.update(fontname="MS Gothic")  # Windowsで MS Gothic を使う場合
ag.edge_attr.update(fontname="MS Gothic")
print(ag)  # dot言語で確認できる
layout = 'circo'  # 'twopi'  # 
ag.draw(DSTDIR + '/corr-spurious-network.pdf', prog=layout)  #fdp


