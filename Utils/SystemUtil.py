#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2024/9/24 16:29
# @Author : Carey
# @File : SystemUtil.py
# @Description
import subprocess
from functools import partial
startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
subprocess.Popen = partial(subprocess.Popen, startupinfo=startupinfo, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL, stderr=subprocess.STDOUT, encoding="utf-8")

import execjs

class SystemUtil():


    def execJsFile( self, file='./assets/js/detail.js' ):
        """
        执行JS预编译
        """
        with open(file, "r", encoding='utf-8') as f:
            js_tamp = f.read()
        jsDrive = execjs.compile(js_tamp)

        return jsDrive



sysUtil = SystemUtil()
