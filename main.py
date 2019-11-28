#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = "main.py"
__author__ = "CLin"
__mtime__ = "2019/11/25"
"""
import os
# import multiprocessing as mp
import process
import config
import examination
import socket

if __name__ == '__main__':
    # mp.freeze_support() # Windows 平台要加上这句，避免 RuntimeError
    attr_num = 7 # ?
    print("Query Flooding Basedd Resurece Sharer")

    # 从my_config.ini中获得自己的：peer编号、ip地址、端口号、共享文件夹名称、最大跳数、直接邻居
    peer = config.Config()
    peer_info = peer.get_attr()
    # print(peer_info)

    


    # 检查配置信息的有效性
    if not examination.examine_config(peer_info):
        os.system("pause")
        exit()

    # 功能选择
    while True:
        pass

    '''
    while True:
        print('**********************************')
        # role = input(">input peer num of your node:")
        role = 1
        opt = input(">input opt(input 'help' if not know):")
        print()
        if opt.split()[0] == 'get':
            # peer_num = config.Config().get_peer_num()
            print('Parent process %s.' % os.getpid())
            # p = mp.Pool(7) # 初始化进程池multiprocessing.pool，用于来自动管理进程任务
            for i in range(attr_num):
                p.apply_async(process.tcp_server, args=(i,))
            print('Waiting for all subprocesses done...')
            # q = mp.Process(target = process.tcp_client, args=(role, opt.split()[1]))
            q.start()
            q.join()
            q.close()
            p.terminate()
            p.join()
            print('All subprocesses done.')
        elif opt.split()[0] == 'config':
            with open("config.ini", 'r') as f:
                line_num = 0
                while True:
                    line = f.readline()
                    line_num += 1
                    if attr_num * int(role) <= line_num <= attr_num * int(role) + 6:
                        print(line, end="")
                    if line_num > attr_num * int(role) + 6:
                        break
        elif opt.split()[0] == 'modify':
            mod_conf = config.Config()
            attr_mod = mod_conf.get_attr(role)
            if opt.split()[1] == 'ip':
                attr_mod['ip_addr'] = opt.split()[2]
            elif opt.split()[1] == 'serverport':
                attr_mod["server_port"] = opt.split()[2]
            elif opt.split()[1] == 'clientport':
                attr_mod['client_port'] = opt.split()[2]
            elif opt.split()[1] == 'sharedir':
                attr_mod['share_dir'] = opt.split()[2]
            elif opt.split()[1] == 'peerlist':
                attr_mod['peer_list'] = opt.split()[2].split('/')
                print(attr_mod['peer_list'])
                attr_mod['peer_list'] = [int(i) for i in attr_mod['peer_list']]
            else:
                print("Input Error. Please check again.")
            print(mod_conf.set_attr(role, attr_mod))
        # elif opt.split()[0] == 'help':
        #     with open("help.txt", 'r', encoding='utf-8') as f:
        #         while True:
        #             line = f.readline()
        #             print(line, end="")
        #             if not line:
        #                 break
        elif opt.split()[0] == 'exit':
            exit()
        else:
            print("Invalid input. Please check your input again.")
    '''