#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2024/9/20 14:39
# @Author : Carey
# @File : Taobao.py
# @Description
import json
import re
import requests
import time
from tkinter import messagebox, simpledialog
from reverse.App.Soybean.Utils.TokenUtils import TokenUtils
from reverse.App.Soybean.Utils.SystemUtil import sysUtil
import webbrowser


class Tabao( TokenUtils ):

    def __init__(self):
        super().__init__()
        self.ptCode = 'taobao'
        self.ptNum = 3
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
            'sgcookie': 'E100uJXEq%2F7w1zsygUTmxC7L41FWpJoLAbMZyQTD4OaVdjQ0VBJSkG9MJMaZy9zs9PaO48ZH8c9LDKRgs86Y40MrW2O6VICPcKSk%2Fp3qd769pPO6ZIIAVwIPDhPm1116MslY; x5sec=7b22733b32223a2239306232323331636262343464343663222c22617365727665723b33223a22307c434d69746f725547454f4b742f736b42476773344e7a51314e5449794d7a49374e69494663324e6c626d55772b6265457867493d227d; sdkSilent=1722045144615; havana_lgc_exp=1753062738543; _hvn_lgc_=0; wk_unb=W875Pb56bzoW; havana_lgc2_0=eyJoaWQiOjg3NDU1MjIzMiwic2ciOiIzNWE2YmY2ZGYzZWYwYWI2ZDc1NDQwNGUwYjkwMGUyYyIsInNpdGUiOjAsInRva2VuIjoiMWpJUzBDRjdkcnJTUlRWbHdxVm0xLVEifQ; sgcookie=E100jnUwytFn7ISyrhGrkXPe9W7BmuYx4xDVotdlwZ6suZLDxGUNLG7iSlu3QRfRKdmngNhH0ZJ9RgB4bRhGuCLdqvSG5haFa9Wkd1JVIOitIeGCW%2FlOkZ4V8dQ%2FfmTsamTV'
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

        response = requests.get( url , headers=headers, cookies=self.cookies )
        response.encoding = response.apparent_encoding
        if 200  != response.status_code:
            return False

        shopName = re.findall(r'name="keywords"(?:\s+)content="(.*?)\/>', response.text.strip(), re.S)
        if not shopName or len( shopName ) <= 0:
            shopName = re.findall(r'property="og:title"(?:\s+)content="(.*?)>', response.text.strip(), re.S)
        if shopName and len( shopName[0] ) > 0:
            self.shopname = shopName[0]

        shopInfo = re.findall(r'content="pageId(?:.*?)shopId=(.*?);(?:.*?)userId=(.*?)"\/>', response.text.strip(), re.S)
        if shopInfo and len( shopInfo[0] ) > 0:
            self.memId = shopInfo[0][1]
            self.shopid = shopInfo[0][0]
            return True

        try:
            strShopContent = re.findall(r'window\.g_config(?:\s?)=(?:\s?)(.*?)if', response.text.strip(), re.S)
            shopDic = json.loads(strShopContent[0].strip())
        except Exception as e:
            strShopContent = re.findall(r'window\.shop_config(?:\s?)=(?:\s?)(.*?);', response.text.strip(), re.S)
            shopDic = json.loads(strShopContent[0].strip())

        try:
            self.memId = shopDic[ 'seller' ][ 'sellerId' ]
            self.shopid = shopDic['seller']['shopId']
            if shopDic['seller']['shopName'] and len(shopDic['seller']['shopName']) > 0:
                self.shopname = shopDic['seller']['shopName']
            elif shopDic['seller']['wangwang'] and len(shopDic['seller']['wangwang']) > 0:
                self.shopname = shopDic['seller']['wangwang']
        except Exception as e:
                try:
                    strShopContent = re.findall(r'window\.shop_config\.isvStat(?:\s?)=(?:\s?)(.*?);', response.text.strip(), re.S)
                    self.shopid = re.findall(r'shopId:(?:\s?)(.*?),', strShopContent[0].strip(), re.S)[0]
                    self.memId = re.findall(r'userId:(?:\s?)(.*?),', strShopContent[0].strip(), re.S)[0]

                    shopNames = re.findall(r'"slogo-shopname"(?:.*?)<strong>(.*?)<\/strong>', response.text.strip(), re.S)
                    self.shopname = shopNames[0]
                except Exception as e:
                    return False

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
        response = requests.get('https://h5api.m.taobao.com/h5/mtop.taobao.shop.simple.item.fetch/1.0/', params=params, headers=self.headers, cookies=self.cookies )
        if 200 != response.status_code:
            return messagebox.showwarning('消息提示', '请输入店铺链接进行检索')

        if 'data' not in response.json() or len( response.json()[ 'data' ] ) <= 0 :
            comp = messagebox.askyesnocancel( '消息提示', '获取数据令牌失效， 是否重新获取' )
            if True == comp:
                setCookie = response.cookies.get_dict()
                self.reSetCookie( setCookie )
            return messagebox.showwarning('消息提示', '初始化令牌已完成，请重新检索' )

        if 'url' in response.json()[ 'data' ]:
            return messagebox.showwarning('消息提示', '请重新录入cookie' )

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

        if not self.memId or len(self.memId) <= 0:
            res = self.initShopInfo(url)
            if False == res:
                return

        lists = self.getShopProductList(page)
        for item in lists:
            yield item

        del lists