#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2024/9/6 10:49
# @Author : Carey
# @File : Alibaba.py
# @Description
import json
import re
import requests
import time
import hashlib
from tkinter import messagebox
import io
from reverse.App.Soybean.Utils.TokenUtils import TokenUtils


class AliBaba( TokenUtils ):
    """
    阿里巴巴店铺商品数据获取
    """
    def __init__(self):
        super().__init__()
        self.ptCode = '1688'
        self.ptNum = 1
        self.cookies = {
            '_m_h5_tk': 'a28a0087eee298b92caab2f275brc285_1725596943332',
            '_m_h5_tk_enc': 'a9c2ef1d9b63a620a6ec63bae631ea4f',
            'mtop_partitioned_detect': '1',
        }
        self.headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,ja;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.1688.com',
            'Referer': 'https://www.1688.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        }
        self.gentETag()
        self.memId = None
        self.shopname = None
        self.take = 100
        self.initToken()
        self.proxy = False


    def getShopProductList( self, page = 1 ):
        """
        获取店铺商品列表
        """
        arg = {
            'appName': 'pcmodules',
            'resourceName': 'wpOfferColumn',
            'memberId': self.memId,
            'type': 'view',
            'version': '1.0.0',
            'appdata':  {
                'sortType': 'wangpu_score',
                'sellerRecommendFilter': 'false',
                'mixFilter': 'false',
                'tradenumFilter': 'false',
                'quantityBegin': 'null',
                'pageNum': page,
                'count': self.take,
            }
        }
        data = {
            'dataType': 'moduleData',
            'argString': json.dumps( arg, ensure_ascii=False).replace(' ', '')
        }
        postData = {
            "data": json.dumps( data,  ensure_ascii=False ).replace(' ', ''),
        }
        strTime = str( round( time.time()*1000 ) )
        params = {
            'jsv': '2.4.11',
            'appKey': '12574478',
            't': strTime,
            'api': 'mtop.1688.shop.data.get',
            'v': '1.0',
            'type': 'json',
            'valueType': 'string',
            'dataType': 'json',
            'timeout': '10000',
        }
        strEnc = self.cookies['_m_h5_tk'].split('_')[0] + "&" + strTime +  "&" +  params['appKey'] + "&" + postData['data']

        sign = hashlib.md5( strEnc.encode(encoding='UTF-8')).hexdigest()
        params[ 'sign' ] = sign

        self.headers[ 'Accept' ] = 'application/json'
        if 'Accept-Encoding' in self.headers:
            del self.headers[ 'Accept-Encoding' ]

        self.headers[ 'User-Agent' ] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'

        response = requests.post( 'https://h5api.m.1688.com/h5/mtop.1688.shop.data.get/1.0/', params=params, cookies=self.cookies, headers=self.headers, data=postData )
        if 200 != response.status_code:
            return messagebox.showwarning('消息提示', '请输入店铺链接进行检索')

        if 'data' not in response.json() or len( response.json()[ 'data' ] ) <= 0 :
            comp = messagebox.askyesnocancel( '消息提示', '获取数据令牌失效， 是否重新获取' )
            if True == comp:
                setCookie = response.cookies.get_dict()
                self.reSetCookie( setCookie )
            return messagebox.showwarning('消息提示', '初始化令牌已完成，请重新检索' )

        retResult = { 'total': self.take, 'plist':[] }
        try:
            retResult['total'] = int( response.json()['data']['content']['paginator']['itemsPerPage'] )
        except Exception as e:
            retResult['total'] = int( arg[ 'appdata' ][ 'count' ] )

        list = response.json()[ 'data' ][ 'content' ][ 'offerList' ]
        if list and len( list ) > 0:
            for item in list:
                info = {
                    'id': item['id'],
                    'subject': item['subject'],
                    'price': item['price'],
                    'gmtCreate': item['gmtCreate'],
                    'bookedCount': item['bookedCount'],
                    'ninetySaleQuantity': item['ninetySaleQuantity'],
                    'url': f"https://detail.1688.com/offer/{item['id']}.html",
                    'thumb': item['offerImages'][0]['imageURI'],
                    'memid': item['memberId']
                }
                if False == item[ 'offerImages' ][0][ 'imageURI' ].startswith( 'https' ) or False == item[ 'offerImages' ][0][ 'imageURI' ].startswith( 'http' ):
                    info['thumb'] = f"https://cbu01.alicdn.com/{item[ 'offerImages' ][0][ 'imageURI' ]}"

                retResult[ 'plist' ].append( info )
        else:
            retResult['plist'] = []

        yield retResult


    def getShopInfo(self):
        arg = {
            'componentKey': 'wpCompany',
            'params': json.dumps( {'memberId': self.memId }, ensure_ascii=False).replace(' ', ''),
        }
        postData = {
            "data": json.dumps( arg, ensure_ascii=False).replace(' ', ''),
        }
        strTime = str(round(time.time() * 1000))
        params = {
            'jsv': '2.5.8',
            'appKey': '12574478',
            't': strTime,
            'api': 'mtop.alibaba.alisite.cbu.server.ModuleAsyncService',
            'v': '1.0',
            'type': 'json',
            'valueType': 'string',
            'dataType': 'json',
            'timeout': '10000',
        }
        strEnc = self.cookies['_m_h5_tk'].split('_')[0] + "&" + strTime + "&" + params['appKey'] + "&" + postData[ 'data']

        sign = hashlib.md5(strEnc.encode(encoding='UTF-8')).hexdigest()
        params['sign'] = sign

        self.headers[ 'Accept' ] = 'application/json'
        response = requests.post('https://h5api.m.1688.com/h5/mtop.alibaba.alisite.cbu.server.moduleasyncservice/1.0/', params=params, cookies=self.cookies, headers=self.headers, data=postData)
        if 200 != response.status_code:
            return False

        if 'data' not in response.json() or len( response.json()['data'] ) <= 0:
            comp = messagebox.askyesnocancel('消息提示', '获取数据令牌失效， 是否重新获取')
            if True == comp:
                setCookie = response.cookies.get_dict()
                self.reSetCookie(setCookie)
                self.initToken()
                messagebox.showwarning('消息提示', '初始化令牌已完成，请重新检索')
                return False

        self.shopname = response.json()[ 'data' ][ 'companyName' ]
        if None == self.memId or len( self.memId ) <= 0:
            self.memId = response.json()[ 'data' ][ 'memberId' ]

        return True

    def initShopInfo(self, url):
        """
        获取店铺标识
        """
        headers = self.headers
        headers[ 'Accept' ] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        headers[ 'Accept-Encoding'] = 'gzip, deflate, br, zstd'
        headers[ 'Upgrade-Insecure-Requests' ] = '1'
        headers[ 'User-Agent' ] = 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36'

        response = requests.get( url.rstrip( '/' ) + '/page/index.html?no_cache=true', cookies=self.cookies, headers=headers)
        response.encoding = response.apparent_encoding
        if response.history:
            redirectUrl = re.findall( r'memberId=(.*?)$', response.history[-1].url, re.S )
            if redirectUrl[0] and len(redirectUrl[0])>0:
                self.memId = redirectUrl[0]

        if None == response.text.strip() or len( response.text.strip() ) <= 0:
            return self.getShopInfo()

        name = re.findall(r'<title>(.*?)<\/title>', response.text.strip(), re.S)
        if name[0] and len(name[0]):
            self.shopname = name[0].split( '_' )[0]
        else:
            name = re.findall(r'name="keywords"(?:\s+)content="(.*?)"(?:\s+)/>', response.text.strip(), re.S)
            if name[0] and len(name[0]):
                self.shopname = name[0].split( '，' )[0]
            else:
                name = re.findall(r'name="description"(?:\s+)content="(.*?)"(?:\s+)/>', response.text.strip(), re.S)
                if name[0] and len(name[0]):
                    self.shopname = name[0].split('，')[0]

        if None != self.memId and len( self.memId ) > 0:
            return True

        memid = re.findall(r'html5;url=(?:\s+)//m.1688.com/winport/(.*?).html">', response.text.strip(), re.S)
        if memid[0] and len(memid[0]):
            self.memId = memid[0]
            return True

        memid = re.findall(r'(?:\s+)member_id:(?:\s+)"(.*?)",', response.text.strip(), re.S)
        if memid[0] and len( memid[0] ):
            self.memId = memid[0]
            return True

        memid = re.findall(r'(?:\s+)adminMemberId:(?:\s+)"(.*?)",', response.text.strip(), re.S)
        if memid[0] and len( memid[0] ):
            self.memId = memid[0]
            return True

        memid = re.findall(r'id="feedbackUid"(?:\s+)value="(.*?)"(?:\s+)/>', response.text.strip(), re.S)
        if memid[0] and len(memid[0]):
            self.memId = memid[0]
            return True

    async def getShopProducts(self, url ):
        """
        提取商品列表数据
        """
        matchUrl = re.findall( r'http?s:\/\/(.*?)\.(1688)\.(com|cn|net|org)', url, re.S )
        if None == matchUrl or len( matchUrl ) <= 0:
            yield messagebox.showerror('消息提示', '请输入正确的店铺链接')

        res = self.initShopInfo( url )
        if False == res:
            yield messagebox.showerror('消息提示', '获取店铺编号失败，请重试')
            return

        iPage = 1
        while True:
            lists = self.getShopProductList( iPage )
            iLen = 0
            for item in lists:
                yield item
                iLen = len( item )
            iPage += 1
            if iLen < 30:
                break


    async def getShopPListByPage(self, url, page ):
        """
        根据分页获取店铺商品
        """
        matchUrl = re.findall(r'http?s:\/\/(.*?)\.(1688|taobao|tmall)\.(com|cn|net|org)', url, re.S)
        if None == matchUrl or len(matchUrl) <= 0:
            yield messagebox.showerror('消息提示', '请输入正确的店铺链接')

        if not self.memId or len( self.memId ) <= 0 :
            while True:
                res = self.initShopInfo(url)
                if True == res:
                    break

        lists = self.getShopProductList(page)
        for item in lists:
            yield item

        del lists


    def download(self, thumb):
        """
        下载图集
        """
        if False == thumb.startswith( 'http:' ) or False == thumb.startswith( 'https:' ):
            url = f'https://{thumb}'

        image_bytes = requests.get( thumb, headers=self.headers ).content
        data_stream = io.BytesIO(image_bytes)

        return data_stream
