#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = "examination.py"
__author__ = "CLin"
__mtime__ = "2019/11/25"
"""
import os
import socket
import random


def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def is_open(ip, port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        s.connect((ip,int(port)))
        s.shutdown(2)
        #利用shutdown()函数使socket双向数据传输变为单向数据传输。shutdown()需要一个单独的参数，
        #该参数表示了如何关闭socket。具体为：0表示禁止将来读；1表示禁止将来写；2表示禁止将来读和写。
        return True
    except:
        print('{0}的{1}端口不可用'.format(ip, int(port)))
        return False

def getPort():
    pscmd = "netstat -ntl |grep -v Active| grep -v Proto|awk '{print $4}'|awk -F: '{print $NF}'"
    procs = os.popen(pscmd).read()
    procarr = procs.split("\n")
    tt= random.randint(15000,20000)
    if tt not in procarr:
        return tt
    else:
        getPort()

def examine_config(peer_info):
    print(get_host_ip())
    usable_port = getPort()
    print("one usable port is " + str(usable_port))

    # 端口可用性检查
    for i in range(0, 10):
        if not is_open(peer_info['ip_addr'], usable_port+i):
            pass
            # return False
    # 共享文件夹存在性检查
    if not os.path.exists(peer_info['share_dir']):
        print('共享文件夹%s不存在', peer_info['share_dir'])
        return False