#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2024/9/6 11:21
# @Author : Carey
# @File : TokenUtils.py
# @Description
import os
import re
import time
import requests
import random
import reverse.App.Soybean.Config.filesystem as file
import reverse.App.Soybean.Config.system as system

class TokenUtils():

    def __init__(self):
        self.cookieFile = f'./Logs/{file.APP_FILE_NAME_TOKEN}'
        self.sessionFile = f'./Logs/{file.APP_FILE_NAME_SESSION}'


    def gentETag(self):
        """
        构建cookie字段 - cna
        """
        iTime = round(time.time() * 1000)
        response = requests.get(f'https://log.mmstat.com/eg.js?t={iTime}')
        ETag = re.findall(r'goldlog.Etag="(.*?)";', response.text.strip())[0]

        self.cookies['cna'] = ETag
        return ETag


    def getDetailUrl(self, id ):
        """
        详情页面链接
        """
        if '1688' == self.ptCode:
            return f'https://detail.1688.com/offer/{id}.html?offerId={id}'

        if 'tmall' == self.ptCode:
            return f'https://detail.tmall.com/item.htm?id={id}'

        if 'taobao' == self.ptCode:
            return f'https://item.taobao.com/item.htm?id={id}'

        if 'Vvic' == self.ptCode:
            return f'https://www.vvic.com/item/{id}'


    def initToken( self ):
        """
        初始化 cookie  设置cookie信息
        """
        if 'Vvic' == self.ptCode:
            user = random.choice( system.account.get( 'Vvic' ) )
            self.headers[ 'Cookie'] = f'source=m;userLoginAuto=1;vvic_token={user["token"]};uid=1846988;userName={user["name"]};umc=1;pn=0;'

            return True

        if '1688' == self.ptCode:
            arrToken = self.getToken()
            if arrToken and len(arrToken) > 0:
                self.cookies['_m_h5_tk'] = arrToken['_m_h5_tk']
                self.cookies['_m_h5_tk_enc'] = arrToken['_m_h5_tk_enc']

            return True

        if 'taobao' == self.ptCode or 'tmall' == self.ptCode:
            arrToken = self.getToken()
            if arrToken and len(arrToken) > 0:
                self.cookies['_m_h5_tk'] = arrToken['_m_h5_tk']
                self.cookies['_m_h5_tk_enc'] = arrToken['_m_h5_tk_enc']

            arrSession = self.getLoginMark()
            if arrSession and len( arrSession ) > 0:
                for key, val in arrSession.items():
                    self.cookies[key] = val

        return True


    def reSetCookie(self, cookie ):
        """
        更新
        """
        cookieDic = {}

        try:
            cookieDic[ '_m_h5_tk' ] = cookie.get( '_m_h5_tk' )
            cookieDic[ '_m_h5_tk_enc' ] = cookie.get('_m_h5_tk_enc')
        except Exception as e:
            cookieDic = cookie

        self.writeToken( cookieDic )
        self.initToken()
        del cookie,cookieDic

        return True


    def analysiCookie(self, strCookie ):
        """
        解析cookie
        """
        if not strCookie or len( strCookie ) <= 0:
            return False

        h5tk = re.findall( r'_m_h5_tk=(.*?);', strCookie, re.S )
        if h5tk and len( h5tk ) >0:
            self.cookies[ '_m_h5_tk' ] = h5tk[0]

        h5tken = re.findall(r'_m_h5_tk_enc=(.*?);', strCookie, re.S)
        if h5tken and len( h5tken ) > 0:
            self.cookies[ '_m_h5_tk_enc' ] = h5tken[0]

        if h5tk and h5tken:
            cookie = dict( _m_h5_tk = h5tk[0], _m_h5_tk_enc = h5tken[0]  )
            self.reSetCookie( cookie )

        coo2 = re.findall(r'wk_cookie2=(.*?);', strCookie, re.S)
        if coo2 and len( coo2 ) >0:
            self.cookies[ 'wk_cookie2' ] = coo2[0]

        wkcoo2 = re.findall(r'cookie2=(.*?);', strCookie, re.S)
        if wkcoo2 and len( wkcoo2 ) > 0:
            self.cookies[ 'cookie2' ] = wkcoo2[0]

        scgcoo = re.findall(r'sgcookie=(.*?);', strCookie, re.S)
        if scgcoo and len( scgcoo ) > 0:
            self.cookies['sgcookie'] = scgcoo[0]

        x5sec = re.findall(r'x5sec=(.*?);', strCookie, re.S)
        if x5sec and len( x5sec ) > 0:
            self.cookies['x5sec'] = x5sec[0]

        x5sectag = re.findall( r'x5sectag=(.*?);', strCookie, re.S )
        if x5sectag and len( x5sectag ) > 0:
            self.cookies['x5sectag'] = x5sectag[0]

        self.writeLoginMark(strCookie)

        return True


    def getLoginMark(self ):
        """
        获取登录信息
        """
        if False == os.path.exists( self.sessionFile ):
            return False

        with open( self.sessionFile, 'r', encoding='utf-8') as f:
            strContent = f.read()

        if not strContent and len( strContent ) <= 0:
            return False

        arrSession = strContent.split( ';' )

        session = {}
        for item in arrSession:
            arrItem = item.split( '=' )
            if not arrItem or len( arrItem ):
                break
            session.update({ arrItem[0]: arrItem[1] })

        return session


    def writeLoginMark(self, cookie, reSet = False ):
        """
        写入登录信息
        """
        h5tk = re.findall(r'_m_h5_tk=(.*?);', cookie, re.S)
        h5tken = re.findall(r'_m_h5_tk_enc=(.*?);', cookie, re.S)
        if h5tk and h5tken:
            cookieDic = {}
            cookieDic[ '_m_h5_tk' ] = h5tk[0]
            cookieDic[ '_m_h5_tk_enc' ] = h5tken[0]
            self.writeToken( cookieDic, reSet=reSet )
            del cookieDic

        arrLoginMark = {}
        coo2 = re.findall(r'wk_cookie2=(.*?);', cookie, re.S)
        if coo2 and len(coo2) > 0:
            arrLoginMark[ 'wk_cookie2' ] = coo2[0]

        wkcoo2 = re.findall(r'cookie2=(.*?);', cookie, re.S)
        if wkcoo2 and len(wkcoo2) > 0:
            arrLoginMark[ 'cookie2' ] = wkcoo2[0]

        scgcoo = re.findall(r'sgcookie=(.*?);', cookie, re.S)
        if scgcoo and len(scgcoo) > 0:
            arrLoginMark[ 'sgcookie' ] = scgcoo[0]

        x5sec = re.findall(r'x5sec=(.*?);', cookie, re.S)
        if x5sec and len(x5sec) > 0:
            arrLoginMark[ 'x5sec' ] = x5sec[0]

        x5sectag = re.findall(r'x5sectag=(.*?);', cookie, re.S)
        if x5sectag and len(x5sectag) > 0:
            arrLoginMark[ 'x5sectag' ] = x5sectag[0]

        if not arrLoginMark or len( arrLoginMark )<=0:
            return False

        strSession = '; ' . join([ str(f'{key}={arrLoginMark[key]}') for key in arrLoginMark ])

        if False == os.path.exists( self.sessionFile ):
            with open( self.sessionFile, 'w', encoding='utf-8') as file:
                file.write( strSession.strip() )

            return arrLoginMark

        with open( self.sessionFile, 'w', encoding='utf-8') as file:
            file.write( strSession.strip() )

        return arrLoginMark


    def getToken(self):
        """
        获取Token
        """
        with open( self.cookieFile, 'r', encoding='utf-8') as f:
            strContent = f.read()

        if not strContent and len( strContent ) <= 0:
            return False

        arrCookie = strContent.split(';')
        cookie = {}
        cookie['_m_h5_tk'] = arrCookie[0]
        cookie['_m_h5_tk_enc'] = arrCookie[1]

        return cookie


    def writeToken(self, cookie, reSet = False ):
        """
        写入cookie
        """
        if False == os.path.exists( self.cookieFile ):
            strCookie = f"{cookie['_m_h5_tk']};{cookie['_m_h5_tk_enc']}"
            with open( self.cookieFile, 'w', encoding='utf-8') as file:
                file.write(strCookie)

            if reSet and True == reSet:
                return cookie

            #self.reSetCookie( cookie )
            return cookie

        strCookie = f"{cookie['_m_h5_tk']};{cookie['_m_h5_tk_enc']}"
        with open( self.cookieFile, 'w', encoding='utf-8') as file:
            file.write(strCookie)

        if reSet and True == reSet:
            return True

        #self.reSetCookie(cookie)
        return cookie