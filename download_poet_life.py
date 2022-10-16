# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 13:42:41 2022

@author: bingo
"""

import requests
import urllib
import json
import re
import textwrap
import pandas as pd
import os


def get_json(poet):
    url = 'https://cnkgraph.com/Api/Biography?scope=&author={}&beginYear=0&endYear=0'
    res = requests.get(url.format(urllib.parse.quote(poet)))
    text = res.text
    text_dict = json.loads(text)
    try:
        os.mkdir('./{}'.format(poet))
    except:
        pass
    with open('./{}/{}.json'.format(poet, poet), 'w', encoding='utf8') as f:
        json.dump(text_dict, f, indent=4, ensure_ascii=False)
    
    return text_dict

def get_poet_life(poet, text_dict):
    lat_list = []
    lon_list = []
    title_list = []
    time_list = []
    event_list = []
    # 获取年份和事件
    for marker in text_dict['Traces'][0]['Markers']:
        try:
            lat = marker['Latitude']
            lon = marker['Longitude']
            title = marker['Title']
            s = re.sub("[\s+\(\)\'\"\/\\\\]", "", marker['Detail'])
            time_event = re.findall("([▪]+|[\-0-9年月日春夏秋冬]+)<[span]+>([，。？！《》：；、（）“”\-0-9\u4e00-\u9fa5]+)", s)
        except:
            break
        
        for (time, event) in time_event:
            lat_list.append(lat)
            lon_list.append(lon)
            title_list.append(title)
            time_list.append(time)
            event_list.append(event)
    
    df = pd.DataFrame({'lat': lat_list,
                      'lon': lon_list,
                      'title': title_list,
                      'time': time_list,
                      'event': event_list})
    df['lat'] = df['lat'].astype('float')
    df['lon'] = df['lon'].astype('float')
    df['time'] = df['time'].replace('▪', None)
    df['time'] = df['time'].fillna(method='pad')
    _ = list(df['time'].str.contains('\d+'))
    df = df.loc[_]
    df.reset_index(drop=True, inplace=True)
    df['title'] = df['title'].replace('\(出生地\)', '', 
                                      regex=True)
    df['group'] = None
    for i, e in enumerate(df['event']):
        if e[0]=='，':
            df['group'][i] = i
    df['group'] = df['group'].fillna(method='pad')
    df.sort_values(['title', 'group'], inplace=True)
    df['event'] = df['event'].apply(lambda x: textwrap.fill(x, 10))
    # 获取轨迹顺序，多列索引
    locus = re.findall(">([\u4e00-\u9fa5]+)<", text_dict['Traces'][0]['Detail'])
    df_locus = pd.DataFrame({'title': locus,
                             'rank': range(len(locus))})
    df_locus.sort_values(['title', 'rank'], inplace=True)
    df_locus = pd.concat([df_locus['rank'].reset_index(drop=True), 
                          df[['title', 'group']].drop_duplicates().reset_index(drop=True)],
                         axis=1)
    df_locus.sort_values('rank', inplace=True)
    mul_index = df_locus.set_index(['title', 'group']).index

    # 数据按时间排序
    df = df.set_index(['title', 'group']).loc[mul_index]
    df = df.loc[[e[0]!='，' for e in df['event']]]
    df.reset_index(drop=False, inplace=True)
    df['line'] = None
    for i in df.index:
        if i==0:
            df['line'][i] = df['title'][i] + ',' + df['title'][i]
        else:
            df['line'][i] = df['title'][i-1] + ',' + df['title'][i]
    df.to_excel('./{}/{}.xlsx'.format(poet, poet), index=False, encoding='utf8')        

    return df
        
    
def get_data(poet):
    try:
        text_dict = get_json(poet)
        data = get_poet_life(poet, text_dict)
    except:
        pass

    return data