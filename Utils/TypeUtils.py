#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2024/9/10 17:35
# @Author : Carey
# @File : TypeUtils.py
# @Description
import re

class TypeUtils():
    """
    数据类型判定
    """


    def isNumStr( self, string ):
        return string.isdigit() if isinstance( string, str) else False


    def isIntStr( self, string ):
        try:
            int( string )
            return True
        except Exception as e:
            return False

    def isFloatStr( self, string):
        try:
            float(string)
            return True
        except Exception as e:
            return False

    def isTimeStr(self, string ):
        pattent = re.compile( r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}' )
        if pattent.match(string):
            return True
        else:
            return False


typeUtils = TypeUtils()