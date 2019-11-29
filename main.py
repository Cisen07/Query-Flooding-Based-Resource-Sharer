#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = "main.py"
__author__ = "CLin"
__mtime__ = "2019/11/25"
"""
import os
import multiprocessing as mp
import time
import config
import socket
import threading
import sys
import connection
import examination

if __name__ == '__main__':
    mp.freeze_support() # Windows 平台要加上这句，避免 RuntimeError
    pool = mp.Pool() # 初始化进程池
    print("*********************************************")
    print("*                                           *")
    print("*                                           *")
    print("*         基于泛洪查找的资源共享            *")
    print("*                                           *")
    print("*                               CLin        *")
    print("*                          2017141471052    *")
    print("*********************************************")

    # 从my_config.ini中获得自己的：peer编号、ip地址、端口号、共享文件夹名称、最大跳数、直接邻居
    peer = config.Config()
    peer_info = peer.get_attr()
    print(peer_info)

    # 共享文件夹存在性检查
    examination.check_share_dir(peer_info['dir'])

    # 建立服务器并监听
    peer_server = connection.Connection()
    peer_server.set_ip(peer_info['ip'])
    peer_server.set_server_port(peer_info['port'])
    peer_server.set_share_dir(peer_info['dir'])
    peer_server.set_ips(peer_info['ips'])
    peer_server.set_ports(peer_info['ports'])
    p = mp.Process(target=peer_server.tcp_server) 
    p.start() # 启动服务器
    
    # 功能选择
    while True:
        print("\n使用说明：\n1. get filename\n2. exit")
        opt = input(">>>>>>>>>>>>>>>>>>>>>键入操作:")
        print()
        try: # 为了解决一个bug：客户端进程把服务端进程的输出视作输入的情况
            opt0 = opt.split()[0]
        except:
            continue
        if opt0 == 'get':
            # 检查文件是否已经在本地了
            if not examination.check_localfile(peer_info['dir'], opt.split()[1]):
                peer_client = connection.Connection()
                peer_client.set_ip(peer_info['ip'])
                peer_client.set_client_port(peer_info['port'])
                peer_client.set_share_dir(peer_info['dir'])
                p.terminate()
                peer_server.set_state(1) # 进入发送状态
                p = mp.Process(target=peer_server.tcp_server)
                p.start()
                # pool.apply_async(peer_server.tcp_server) # 再次启动服务器
                print("向所有邻居服务器发送get请求")
                for i in range(0, len(peer_info['ips'])):
                    # print("send one")
                    peer_client.tcp_client_notice(peer_info['ips'][i], peer_info['ports'][i], "get %s %s %s %s" % (opt.split()[1], peer_info['ip'], peer_info['port'], peer_info['ttl']))
                time.sleep(4) # 等待4秒
                p.terminate()
                peer_server.set_state(0) # 退出发送状态
                p = mp.Process(target=peer_server.tcp_server)
                p.start() # 再次启动服务器
            else:
                print("该文件已经存在本地！")
                continue
        elif opt0 == 'exit':
            p.terminate()
            sys.exit()
        else:
            print("不合法的输入，请重新输入请求")