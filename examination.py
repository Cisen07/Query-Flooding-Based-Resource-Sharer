#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = "examination.py"
__author__ = "CLin"
__mtime__ = "2019/11/25"
"""
import os


def check_share_dir(dir):
    if not os.path.exists(dir):
        print('共享文件夹%s不存在' % dir)
        os.system("pause")
        exit()
        

def check_localfile(root, filename):
    items = os.listdir(root)
    for item in items:
        path = os.path.join(root, item)
        if path.split('\\')[-1] == filename or path.split('/')[-1] == filename:
            print("在本地找到文件")
            return True
        elif os.path.isdir(path):
            print("发现目录，进入目录内层查找")
            return check_localfile(path.replace('\\', '/'), filename)
    return False