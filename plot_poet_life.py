# -*- coding: utf-8 -*-
"""
Created on Sat Oct 15 00:20:59 2022

@author: bingo
"""

from pyecharts import options as opts
from pyecharts.charts import Geo, Map, BMap
from pyecharts.globals import ChartType, SymbolType
from pyecharts.datasets import COORDINATES as coord
from pyecharts.render import make_snapshot
from snapshot_phantomjs import snapshot

import cv2
import pandas as pd
import numpy as np


from download_poet_life import get_data
import os
import warnings

def plot_life(df, num, poet):

    line_data = [df['line'][i].split(',') for i in df.index[:num+1]]
    # print(line_data)
    coords = df[['title', 'lat', 'lon']].drop_duplicates()
    # 添加地点坐标
    locus = Geo(init_opts=opts.InitOpts(width='900px', 
                                        height='506px',
                                        bg_color='white'))
    
    for i in coords.index:
        locus.add_coordinate(name=coords.loc[i, 'title'], 
                             longitude=coords.loc[i, 'lon'], 
                             latitude=coords.loc[i, 'lat'])
    
    # 计算地图中心坐标
    lat = (df['lat'].max()+df['lat'].min())/2
    lon = (2*df['lon'].min()+df['lon'].max())/3
    lat_range = df['lat'].max()-df['lat'].min()
    lon_range = df['lon'].max()-df['lon'].min()
    zoom = min(85/lon_range, 38/lat_range)
    locus.add_schema(maptype="china",
                     is_roam=True, 
                     center=[lon, lat],
                     zoom=zoom)
    # 绘制轨迹
    locus.add("", 
              line_data[:-1], 
              type_="lines",
              symbol="circle",
              symbol_size=5,
              effect_opts=opts.EffectOpts(is_show=False),
              linestyle_opts=opts.LineStyleOpts(curve=0.2, opacity=0.8,
                                                color="#83cbac"),
              label_opts=opts.LabelOpts(is_show=False))    
    locus.add("", 
              line_data[-1:], 
              type_='lines', 
              symbol_size=5,
              effect_opts=opts.EffectOpts(is_show=False),
              linestyle_opts=opts.LineStyleOpts(curve=0.2, color="#ed556a"),
              label_opts=opts.LabelOpts(is_show=False))
    # 绘制点
    # locus.add("",
    #           scatter_data[:-2], 
    #           type_='scatter', color="dimgray", 
    #           symbol_size=4,
    #           label_opts=opts.LabelOpts(is_show=False, formatter='{b}', color="black", font_size=12))
    if num==0:
        locus.add("",
                  [(df.loc[num, 'title'], 1)], 
                  type_='scatter', 
                  color="#ed556a", 
                  symbol_size=4,
                  label_opts=opts.LabelOpts(is_show=True, 
                                            position="right",
                                            formatter="{b}", 
                                            color="black", 
                                            font_size=12))
    else:
        _ = df.loc[[num-1, num]].sort_values('lon').reset_index()
        locus.add("",
                  [(_.loc[1, 'title'], 1)],
                  type_='scatter', 
                  color="#ed556a", 
                  symbol_size=4,
                  label_opts=opts.LabelOpts(is_show=True, 
                                            position="right",
                                            formatter="{b}", 
                                            color="black", 
                                            font_size=12))  
        if _['title'].drop_duplicates().shape[0]==2:
            locus.add("",
                      [(_.loc[0, 'title'], 1)],
                      type_='scatter', 
                      color="#ed556a", 
                      symbol_size=4,
                      label_opts=opts.LabelOpts(is_show=True, 
                                                position="left",
                                                formatter="{b}", 
                                                color="black", 
                                                font_size=12))        
    locus.set_global_opts(
        title_opts=opts.TitleOpts(
            title="{}\n".format(poet) + df.loc[num, 'time'], 
            pos_left="3%",
            pos_top="5%",
            title_textstyle_opts=opts.TextStyleOpts(font_size=24, 
                                                    line_height=30),
            subtitle=df.loc[num, 'event'],
            subtitle_textstyle_opts=opts.TextStyleOpts(font_size=16, 
                                                       color="dimgray",
                                                       line_height=24)))
    
    return locus

def render_plot(poet):
    df = pd.read_excel('./{}/{}.xlsx'.format(poet, poet))
    # df = df.loc[:10]
    n = df.shape[0]
    for i in df.index:
        locus = plot_life(df, i, poet)
        make_snapshot(snapshot, 
                      locus.render(), 
                      './{}/{:0>lengthd}.jpeg'.replace('length', str(len(str(n)))).format(poet, i+1))
        print('绘图进度：{}/{}'.format(i+1, n))

def plot2video(poet):
    file_path = './{}/{}.mp4'.format(poet, poet)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 2
    size = (1800, 1012)
    path = './{}/'.format(poet)
    videoWriter = cv2.VideoWriter(file_path,
                                  fourcc,
                                  fps,
                                  size)
    
    
    for item in os.listdir(path):
        if item.endswith('.jpeg'):
            item = path + item
            image = cv2.imdecode(np.fromfile(file=item, 
                                             dtype=np.uint8), 
                                 cv2.IMREAD_COLOR)
            videoWriter.write(image)
            
    videoWriter.release()
    
if __name__=='__main__':
    print('.......')
    warnings.filterwarnings('ignore')
    try:
        poet = input("请输入诗人名字：")
        # poet = '白居易'
        print("开始下载数据...")
        data = get_data(poet)
        print("数据下载完毕！")
        print("开始绘图...")
        render_plot(poet)
        print("开始导出视频...")
        plot2video(poet)
        print("视频 {} 已导出！".format(poet))
        
    except Exception as e:
        print(str(e))
        input()