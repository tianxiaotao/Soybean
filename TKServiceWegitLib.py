#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2024/9/6 10:47
# @Author : Carey
# @File : TKServiceWegitLib.py
# @Description
import re
import time
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from reverse.App.Soybean.Libraries.Alibaba import AliBaba
from reverse.App.Soybean.Libraries.Vvic import Vvic
from reverse.App.Soybean.Libraries.Taobao import Tabao
from reverse.App.Soybean.Libraries.Tmall import Tmall
from reverse.App.Soybean.Utils.TypeUtils import typeUtils
from reverse.App.Soybean.Utils.MenuOptUtils import MenuOptUtils
import webbrowser


class TKServiceWegitLib( tk.Tk, MenuOptUtils ):
    """
    创建应用主体
    """
    def __init__( self, loopEvent ):
        super(TKServiceWegitLib, self).__init__()
        self.title( '毛豆选品工具' )
        self.geometry( '1260x850' )
        self.iconbitmap( './assets/images/favicon.ico' )
        self.resizable( 0,0 )
        self.style = ttk.Style()
        self.style.configure('Treeview', rowheight=60 )
        self.style.configure('.', font=("仿宋", 15))
        self.ptList = [ '1688', 'vvic', 'taobao', 'tmall' ]
        self.loop = loopEvent

    def initSeachWegit(self):
        search_frame = tk.Frame( self )
        search_frame.pack( pady=30 )

        # 创建一个字符串变量
        self.key = tk.StringVar()
        tk.Entry( search_frame, relief='flat', width=50, textvariable=self.key).pack(side=tk.LEFT, padx=5, fill='both' )
        tk.Button( search_frame, text='搜索一下', font=('黑体', 12), foreground='#fff', relief='flat', bg='#3385ff', command=self.getSearchList).pack(side=tk.LEFT, padx=5 )

        return True

    def initMenu(self):
        menus = tk.Menu(self)


        fm = tk.Menu(menus, tearoff=False)
        fm.add_command(label="Cookie", command=self.supply)
        menus.add_cascade(label="录入", menu=fm)


        sm = tk.Menu(menus, tearoff=False)
        sm.add_command(label="导出", command=self.export)
        sm.add_separator()
        sm.add_command(label="Quit")
        menus.add_cascade(label="文件", menu=sm)

        tm = tk.Menu(menus, tearoff=False)
        tm.add_command(label="退出", command=self.quiteSystem )
        menus.add_cascade(label="操作", menu=tm )

        self.config( menu=menus )
        return True

    def initTreeViwe(self):
        """
        初始化 Treeview
        """
        ttk.Style().configure('MyStyle1.Treeview', rowheight=45)
        self.trv = ttk.Treeview( self, selectmode='browse', style='MyStyle1.Treeview' )
        self.trv['columns'] = ( 'id', 'name', 'price', 'publish', 'collects', 'sales')
        self.trv['show'] = 'headings'
        self.trv[ 'displaycolumns' ] = '#all'

        # 设置列宽
        self.trv.column('id', width=150, anchor='center' )
        self.trv.column('name', width=300, anchor='center' )
        self.trv.column('price', width=100, anchor='center')
        self.trv.column('publish', width=200, anchor='center')
        self.trv.column('collects', width=120, anchor='center')
        self.trv.column('sales', width=120, anchor='center')

        # 设置列标题
        self.trv.heading('id', text='编号')
        self.trv.heading('name', text='商品名称')
        self.trv.heading('price', text='商品售价')
        self.trv.heading('publish', text='上架日期')
        self.trv.heading('collects', text='收藏数')
        self.trv.heading('sales', text='销量')

        scrollbar = tk.Scrollbar( self.trv, orient='vertical', command=self.trv.yview() )
        scrollbar.pack( side=tk.RIGHT, fill=tk.Y )
        self.trv.configure( yscrollcommand=scrollbar.set )
        self.scbar = scrollbar

        self.bindEvents( 'publish', False)
        self.bindEvents( 'collects', False )
        self.bindEvents( 'sales', False )
        self.bindEvents( 'price', False)
        self.trv.pack(fill=tk.BOTH, expand=True )

        return True

    def onScrollEvent(self, *args ):
        top, bottom = self.trv.yview()
        skey = self.key.get()
        if not skey or len( skey ) <= 0:
            return False

        try:
            if 0.0 == top or None == self.page or self.page <= 0:
                return False
        except Exception as e:
            return False

        if bottom >= 0.9:
            print( f'获取第：{self.page}页数据' )
            self.loop.run_until_complete( self.mian( skey ) )

    def bindEvents(self, col, reverse ):
        allList = []
        for k in self.trv.get_children():
            val  = self.trv.set( k, col)
            if typeUtils.isIntStr( val ):
                allList.append( (int( val ), int(k)) )
                continue

            if typeUtils.isFloatStr( val ):
                allList.append( ( float(val), int(k)) )
                continue

            if typeUtils.isTimeStr( val ):
                allList.append( ( time.strptime( val, '%Y-%m-%d %H:%M:%S' ), int(k)))
                continue

        allList.sort(reverse=reverse)
        for index, (val, k) in enumerate(allList):
            self.trv.move(k, '', index)
        del allList

        self.trv.heading(col, command=lambda: self.bindEvents( col, not reverse))

        self.trv.bind( '<ButtonRelease-1>',  self.oneClickBtnEvent )
        self.trv.bind( '<Double-Button-1>',  self.doubleClickBtnEvent )
        self.trv.bind( '<Configure>', self.onScrollEvent )
        self.trv.bind( '<MouseWheel>', self.onScrollEvent )
        return True

    def oneClickBtnEvent(self, event ):
        pass

    def doubleClickBtnEvent(self, event ):
        if not self.trv.selection() or len( self.trv.selection() ) <=0:
            return False

        item = self.trv.item( self.trv.selection()[-1] )
        if not item.get( 'text' ) or len( item.get( 'text' ) ) <= 0:
            return messagebox.showwarning('消息提示', '商品链接未检测到！')

        if not item.get( 'tags' )[0] or len( item.get( 'tags' )[0] ) <= 0:
            return messagebox.showwarning('消息提示', '商品链接平台未识别')

        sign = item.get( 'text' ).strip()
        webbrowser.open(self.driver.getDetailUrl(sign))
        return True

    async def mian(self, key, reset=False ):

        shopUrlDic = re.findall( r'^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n]+)(?:.com|.net|.org.|.cn)', key.strip(), re.S )
        if not shopUrlDic[0] or len( shopUrlDic[0] )<=0:
            self.trv.delete(*self.trv.get_children())
            return messagebox.showwarning('消息提示', '店铺链接未检测到！')

        platform = shopUrlDic[0]
        if -1 != shopUrlDic[0].find( '.' ):
            platform = shopUrlDic[0][(shopUrlDic[0].find( '.' )+1):len( shopUrlDic[0] )]

        if platform not in self.ptList:
            self.trv.delete(*self.trv.get_children())
            return messagebox.showwarning('消息提示', '当前输入店铺平台不支持')

        try:
            if self.driver.ptCode != platform or True == reset:
                if '1688' == platform:
                    self.driver = AliBaba()
                if 'vvic' == platform:
                    self.driver = Vvic()
                if 'taobao' == platform:
                    self.driver = Tabao()
                if 'tmall' == platform:
                    self.driver = Tmall()
        except Exception as e:
            if '1688' == platform:
                self.driver = AliBaba()
            if 'vvic' == platform:
                self.driver = Vvic()
            if 'taobao' == platform:
                self.driver = Tabao()
            if 'tmall' == platform:
                self.driver = Tmall()

        async for items in self.driver.getShopPListByPage( key, self.page ):
            if items['plist'] and len( items['plist'] ) > 0:
                totalList = self.trv.get_children()
                i = len(totalList)
                for item in items['plist']:
                    # img = self.getImageData(item['thumb'], i)
                    sign = item['id']
                    if 'vid' in item and item['vid'] and len( item[ 'vid' ] ):
                        sign = item[ 'vid' ]
                    self.trv.insert(parent='', index='end', iid=i, text=sign, open=False, values=( item['id'], item['subject'], item['price'], item['gmtCreate'], item['bookedCount'], item['ninetySaleQuantity']), tags=(self.driver.ptCode))
                    i = i + 1
                    del item

            if not items['plist'] or len( items['plist'] ) <= 0 or items['total'] != len( items['plist'] ):
                del self.page
                print( '获取数据列表为空，不再进行取值任务' )
                return True

            del items
            self.page += 1

    def getImageData(self, url, i ):
        """
        更新内容
        """
        #item = self.trv.item(i)
        ali = AliBaba()
        res = ali.download( url )

        # 加载图片
        image = Image.open( res )
        image = image.resize((100, 100), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        # print( photo )
        # self.trv.item( i, image=photo )
        return photo

    def getSearchList(self):
        """
        检索数据
        """
        strSearchKey = self.key.get()
        if strSearchKey == None or len( strSearchKey ) <= 0:
            self.trv.delete(*self.trv.get_children())
            return messagebox.showinfo( '消息提示', '请输入店铺链接进行检索' )

        self.trv.delete(*self.trv.get_children())

        self.page = 1
        self.loop.run_until_complete( self.mian( strSearchKey, True ) )
        return True

    def __del__(self):
        self.trv.delete(*self.trv.get_children())



import asyncio
loop = asyncio.get_event_loop()

if __name__ == '__main__':
    app = TKServiceWegitLib( loop )
    app.initMenu()
    app.initSeachWegit()
    app.initTreeViwe()
    app.mainloop()

    loop.run_forever()