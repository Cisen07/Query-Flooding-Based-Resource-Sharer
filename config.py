#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = "config.py"
__author__ = "CLin"
__mtime__ = "2019/11/25"
"""
import configparser


class Config:
    __cf = configparser.ConfigParser()
    __ttl = 0


    def get_attr(self):
        """
        :return: dict {'ip': ip, 'port': port, 'dir': share_dir, 'ttl': max pop, 'ips': peers' ip, 'ports': peers' port}
        """
        while True:
            try:
                peer = dict()
                peer['ip'] = self.__cf.get("config", "ip")
                peer['port'] = self.__cf.get("config", "port")
                peer['dir'] = self.__cf.get("config", "dir")
                peer['ttl'] = self.__cf.get("config", "ttl")
                peer_str = self.__cf.get("network", "ips")
                peer_str = peer_str[1 : len(peer_str)-1]
                peer_list = peer_str.split(', ')
                peer['ips'] = peer_list
                peer_str = self.__cf.get("network", "ports")
                peer_str = peer_str[1 : len(peer_str)-1]
                peer_list = peer_str.split(', ')
                if not peer_list:
                    for i in range(len(peer_list)):
                        peer_list[i] = int(peer_list[i])
                else:
                    peer_list = [int(i) for i in peer_list]
                peer['ports'] = peer_list
                break
            except:
                pass
        return peer

    
    def __init__(self):
        self.__cf.read("my_config.ini")