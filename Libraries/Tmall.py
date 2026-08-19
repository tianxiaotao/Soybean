#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2024/9/20 14:39
# @Author : Carey
# @File : Taobao.py
# @Description
import json
import re
import requests
import  time
from tkinter import messagebox, simpledialog
from reverse.App.Soybean.Utils.TokenUtils import TokenUtils
from reverse.App.Soybean.Utils.SystemUtil import sysUtil


class Tmall( TokenUtils ):

    def __init__(self):
        super().__init__()
        self.ptCode = 'tmall'
        self.ptNum = 4
        self.cookies = {
            'xlly_s': '1',
            '_l_g_': 'Ug%3D%3D',
            'login': 'true',
            'cancelledSubSites': 'empty',
            'sg': '423',
            'csg': '99a61954',
            'wk_unb': 'W875Pb56bzoW',
            'wk_cookie2': '120903c60f89269023c596350e09b831',
            'cookie2': '1ab69553e2e4d5d9e226bac79e6422b9',
            'mtop_partitioned_detect': '1',
            '_m_h5_tk': 'd0f303850bef340f24f52925dce1349c_1726837064194',
            '_m_h5_tk_enc': '7dd0ee5a2babc9e3e07b2bd3d2b4e29c',
            'x5sec': '7b22733b32223a2237626131303364336138363039326137222c22617365727665723b33223a22307c43494f6a74626347454f65676b356748476777344e7a51314e5449794d7a49374d7a676942584e6a5a57356c4d4d37596f746e392f2f2f2f2f77453d227d',
        }
        self.headers = {
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.taobao.com',
            'Referer': 'https://www.taobao.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        }
        self.gentETag()
        self.memId = None
        self.shopname = None
        self.shopid = None
        self.take = 100
        self.initToken()
        self.proxy = False


    def initShopInfo(self, url):
        """
        初始化店铺信息
        """
        headers = self.headers
        headers[ 'Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        try:
            del headers[ 'Content-Type' ]
        except Exception as e:
            pass

        response = requests.get( url + '/p/rd207699.htm?spm=a1z10.1-b.w5001-24113474523.12.49fc757cNx1J0u&scene=taobao_shop', headers=headers, cookies=self.cookies )
        response.encoding = response.apparent_encoding
        if 200  != response.status_code:
            return False

        try:
            shopName = re.findall(r'name="keywords"(?:\s+)content="(.*?)\/>', response.text.strip(), re.S)
            self.shopname = shopName[0]
        except Exception as e:
            shopName = re.findall(r'property="og:title"(?:\s+)content="(.*?)>', response.text.strip(), re.S)
            self.shopname = shopName[0]

        try:
            shopInfo = re.findall( r'content="pageId(?:.*?)shopId=(.*?);(?:.*?)userId=(.*?)"\/>', response.text.strip(), re.S )
            self.memId = shopInfo[0][1]
            self.shopid = shopInfo[0][0]

            return True
        except Exception as e:
            try:
                strShopContent = re.findall(r'window\.g_config(?:\s?)=(?:\s?)(.*?);', response.text.strip(), re.S)

                self.shopid  = re.findall( r'shopId:(?:\s?)(.*?),', strShopContent[0].strip(), re.S )[0]
                self.memId = re.findall(r'sellerId:(?:\s?)(.*?),', strShopContent[0].strip(), re.S)[0]
            except Exception as e:
                try:
                    strShopContent = re.findall(r'window\.shop_config\.isvStat(?:\s?)=(?:\s?)(.*?);', response.text.strip(), re.S)

                    self.shopid = re.findall(r'shopId:(?:\s?)(.*?),', strShopContent[0].strip(), re.S)[0]
                    self.memId = re.findall(r'userId:(?:\s?)(.*?),', strShopContent[0].strip(), re.S)[0]
                    #self.shopname = re.findall(r'nickName:(?:\s?)(.*?),', strShopContent[0].strip(), re.S)[0]
                except Exception as e:
                    strShopContent = re.findall(r'window\.shop_config(?:\s?)=(?:\s?)(.*?);', response.text.strip(), re.S)
                    shopDic = json.loads(strShopContent[0].strip())

        self.memId = shopDic[ 'userId' ]
        self.shopid = shopDic[ 'shopId' ]

        try:
            self.shopname = shopDic[ 'user_nick' ]
        except Exception as e:
            shopNames = re.findall(r'"slogo-shopname"(?:.*?)<strong>(.*?)<\/strong>', response.text.strip(), re.S)
            self.shopname = shopNames[0]

        return True


    def getShopProductList(self, page=1):
        """
        分页获取店铺数据
        """
        data = {
            'shopId': self.shopid,
            'sellerId': self.memId,
            'page': page,
            'orderType': 'first_new',  # first_new 时间； popular 综合； uvsum365 销量；  inshop_discount_price【asc/des】 价格正倒序
            'sortType': '',
            'catId': 0,
            'keyword': '',
            'filterType': ''
        }
        rtime = round(time.time() * 1000)
        c = json.dumps(data).replace(' ', '')

        self.headers[ 'Accept' ] = 'application/json'
        self.headers[ 'Content-Type' ] = 'application/x-www-form-urlencoded'

        token = re.findall(r'(.*?)_(?:.*?)', self.cookies['_m_h5_tk'] )
        jsDrive = sysUtil.execJsFile( './assets/js/detail.js' )
        sign = jsDrive.call('_getSign', token[0], rtime, c)
        params = {
            'jsv': '2.6.2',
            'appKey': '12574478',
            't': str(rtime),
            'sign': sign,
            'api': 'mtop.taobao.shop.simple.item.fetch',
            'type': 'originaljson',
            'v': '1.0',
            'timeout': '10000',
            'dataType': 'json',
            'sessionOption': 'AutoLoginAndManualLogin',
            'needLogin': 'true',
            'LoginRequest': 'true',
            'jsonpIncPrefix': f'_{str(rtime)}_',
            'data': json.dumps(data, ensure_ascii=False).replace(' ', ''),
        }
        self.headers[ 'Cookie' ] =  '; ' . join([ str(f'{key}={self.cookies[key]}') for key in self.cookies ])
        response = requests.get('https://h5api.m.taobao.com/h5/mtop.taobao.shop.simple.item.fetch/1.0/', params=params, headers=self.headers  )
        if 200 != response.status_code:
            return messagebox.showwarning('消息提示', '请输入店铺链接进行检索')

        if 'data' not in response.json() or len( response.json()[ 'data' ] ) <= 0 :
            setCookie = response.cookies.get_dict()
            if not setCookie or len( setCookie ) <= 0:
                return messagebox.showerror('消息提示',  response.json()['ret'][0] )

            comp = messagebox.askyesnocancel( '消息提示', '获取数据令牌失效， 是否重新获取' )
            if True == comp:
                setCookie = response.cookies.get_dict()
                self.reSetCookie( setCookie )
            return messagebox.showwarning('消息提示', '初始化令牌已完成，请重新检索' )

        if 'url' in response.json()[ 'data' ] and 'h5url' in response.json()[ 'data' ]:
            input = simpledialog.askstring('访问受限', '平台限制访问或出现滑块, 请登录操作滑块录入COOKIE：')
            if input and len(input) > 0:
                self.analysiCookie(input)
                return messagebox.showwarning('消息提示', '录入解析已完成，请重新检索' )
            else:
                return False

        retResult = {'total': self.take, 'plist': []}
        try:
            retResult['total'] = int(response.json()['data']['pageSize'])
        except Exception as e:
            retResult['total'] = 0

        if response.json()['data']['data'] and len(response.json()['data']['data']) > 0:
            for item in response.json()['data']['data']:
                info = {
                    'id': item['itemId'],
                    'subject': item['title'],
                    'price': item['discountPrice'],
                    'gmtCreate': 0,
                    'bookedCount': 0,
                    'ninetySaleQuantity': None,
                    'url': item['itemUrl'],
                    'thumb': item['itemUrl'],
                    'memid': self.memId
                }
                try:
                    info[ 'ninetySaleQuantity' ] = item[ 'vagueSold365' ].strip('+')
                except Exception as e:
                    info['ninetySaleQuantity'] = 0

                retResult['plist'].append(info)
        else:
            retResult['plist'] = []
        yield retResult


    async def getShopPListByPage(self, url, page):
        """
        根据分页获取店铺商品
        """
        matchUrl = re.findall(r'http?s:\/\/(.*?)\.(1688|taobao|tmall)\.(com|cn|net|org)', url, re.S)
        if None == matchUrl or len(matchUrl) <= 0:
            yield messagebox.showerror('消息提示', '请输入正确的店铺链接')

        if not self.memId or len( self.memId ) <= 0:
            res = self.initShopInfo(url)
            if False == res:
                return

        lists = self.getShopProductList(page)
        for item in lists:
            yield item

        del lists
