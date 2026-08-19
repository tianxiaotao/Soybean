#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2024/9/10 9:09
# @Author : Carey
# @File : Vvic.py
# @Description
import random
from tkinter import messagebox
import re
import requests
from reverse.App.Soybean.Utils.TokenUtils import TokenUtils
import time

class Vvic( TokenUtils ):
    """
    Vvic 店铺商品获取
    """
    def __init__(self):
        super(TokenUtils, self).__init__()
        self.ptCode = 'Vvic'
        self.ptNum = 2
        self.memId = None
        self.take = 80
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,ja;q=0.7',
            'Cookie': 'source=m;userLoginAuto=1;vvic_token=ac43051e-2d0e-43f7-978a-e89698461386;uid=1846988;userName=vvic8493953156;umc=1;pn=0;',
            'Referer': 'https://www.vvic.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'token': '',
        }
        self.shopname = None
        self.initToken()


    def getShopProductList(self, page = 1  ):
        params = {
            'id': self.memId,
            'currentPage': page,
            'sort': 'up_time-desc',
            'merge': '0',
        }
        response = requests.get( 'https://www.vvic.com/apif/shop/itemlist', params=params, headers=self.headers )
        if 200 != response.status_code:
            return messagebox.showwarning('消息提示', '请输入店铺链接进行检索')
        if 'data' not in response.json():
            return messagebox.showerror('消息提示', '数据异常')

        retResult = {'total': self.take, 'plist': []}
        try:
            retResult[ 'total' ] = int( response.json()['data'][ 'pageSize' ] )
        except Exception as e:
            retResult[ 'total' ] = 0

        if response.json()['data'][ 'recordList' ] and len( response.json()['data'][ 'recordList' ] ) > 0:
            for item in response.json()['data'][ 'recordList' ]:
                if None == self.shopname or len( self.shopname ) <= 0:
                    self.shopname = item[ 'shop_name' ]

                info = {
                    'id': item['id'],
                    'vid': item['vid'],
                    'subject': item['title'],
                    'price': item['price'],
                    'gmtCreate': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime( int( item['up_time'] / 1000 ) )),
                    'bookedCount': item['fav_item_num'],
                    'ninetySaleQuantity': item['sales'],
                    'url': f"https://www.vvic.com/item/{item['vid']}",
                    'thumb': item['index_img_url'],
                    'memid': item['shop_id']
                }
                if None == item['fav_item_num']:
                    info['bookedCount'] = 0
                if None == item['sales']:
                    info['ninetySaleQuantity'] = 0
                if False == item[ 'index_img_url' ].startswith( 'https' ) or False == item[ 'index_img_url' ].startswith( 'http' ):
                    info['thumb'] = f"https:{item[ 'index_img_url' ]}"

                retResult['plist'].append(info)
        else:
            retResult['plist'] = []

        yield retResult


    async def getShopPListByPage(self, url, page = 1 ):
        """
        根据分页获取店铺商品
        """
        matchUrl = re.findall(r'http?s:\/\/(.*?)\.(vvic)\.(com|cn|net|org)', url, re.S)
        if None == matchUrl or len(matchUrl) <= 0:
            yield messagebox.showerror('消息提示', '请输入正确的店铺链接')

        if not self.memId or len(self.memId) <= 0:
            res = re.findall( r'\/(\d+)', url, re.S )
            if not res[0] or len( res[0] ) <= 0 :
                yield messagebox.showerror('消息提示', '获取店铺编号失败，请检查输入链接是否为店铺链接')
                return
            self.memId = res[0]

        lists = self.getShopProductList( page )
        for item in lists:
            yield item

        del lists

    def __del__(self):
        pass