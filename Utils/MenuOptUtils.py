#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2024/9/24 15:40
# @Author : Carey
# @File : MenuOptUtils.py
# @Description

from tkinter import ttk, messagebox, filedialog, simpledialog
from reverse.App.Soybean.Utils.TokenUtils import TokenUtils
from reverse.App.Soybean.Utils.StorageUtils import storageUtils


class MenuOptUtils():


    def supply( self ):
        """
        补充cookie
        """
        input = simpledialog.askstring('访问受限', '平台限制访问, 请登录操作后录入COOKIE：')
        if input and len( input ) > 0:
            tokenUtil = TokenUtils()
            tokenUtil.writeLoginMark( input, True )
            return messagebox.showinfo('消息提示', '录入已完成，开始搜索把')
        else:
            return messagebox.showerror('消息提示', '录入失败')


    def quiteSystem( self ):
        """
        退出系统
        """
        self.trv.delete(*self.trv.get_children())
        self.destroy()
        return True


    def export( self ):
        """
        数据导出
        """
        datas = self.trv.get_children()
        if not datas or len( datas ) <= 0:
            return messagebox.showwarning('消息提示', '请先搜索后再进行导出操作')

        finfo = {
            'ptid': self.driver.ptNum,
            'code': self.driver.ptCode,
            'memid': self.driver.memId,
        }
        if None != self.driver.shopname and len( self.driver.shopname ) > 0:
            finfo[ 'shopname' ] = self.driver.shopname

        storageUtils.initFile( finfo )
        del finfo

        file = filedialog.asksaveasfilename( initialdir=storageUtils.folder, initialfile=storageUtils.fname, defaultextension='.xlsx', title='数据导出保存' )
        if not file:
            return False

        if not file.endswith('.xlsx'):
            file += '.xlsx'

        listItems = self.trv.get_children()
        if not listItems or len( listItems ) <= 0:
            return False

        storageUtils.writToExcel( driver=self.trv, filePath=file, datas=listItems )
        return True


