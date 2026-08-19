#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2024/9/6 10:39
# @Author : Carey
# @File : __init__.py.py
# @Description

import TKServiceWegitLib as Soybean
import asyncio

loop = asyncio.get_event_loop()

if __name__ == '__main__':
    app = Soybean.TKServiceWegitLib( loop )
    app.initMenu()
    app.initSeachWegit()
    app.initTreeViwe()
    app.mainloop()

    loop.run_forever()