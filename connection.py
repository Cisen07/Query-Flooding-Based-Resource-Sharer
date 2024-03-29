#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = "connection.py"
__author__ = "CLin"
__mtime__ = "2019/11/25"
"""
import socket
import threading
import os
import struct
import json
import zipfile
import time
import file_hash


class Connection:
	__ip_addr = None
	__server_port = None
	__client_port = None
	__peer_list = None
	__ips = None
	__ports = None
	__share_dir = None
	__query_res = dict()
	__path_list = dict()
	__state = 0 # 如果为1，表示正在发送或者是转发信息

	# 服务器端收到的命令
	__cmd = []

	__source_ip = '127.0.0.1'
	__source_port = None

	def set_ip(self, ip_addr):
		self.__ip_addr = ip_addr

	def set_server_port(self, server_port):
		self.__server_port = int(server_port)

	def set_client_port(self, client_port):
		self.__client_port = int(client_port)
	
	def set_ips(self, ips):
		self.__ips = ips

	def set_ports(self, ports):
		self.__ports = ports

	def set_share_dir(self, share_dir):
		self.__share_dir = share_dir

	def set_state(self, state):
		self.__state = state


	def query(self, root, filename):
		items = os.listdir(root)
		for item in items:
			path = os.path.join(root, item)
			if path.split('\\')[-1] == filename or path.split('/')[-1] == filename:
				self.__query_res[filename] = 1
				self.__path_list[filename] = path.replace('\\', '/')
			elif os.path.isdir(path):
				self.query(path.replace('\\', '/'), filename)


	def tcp_handler(self, conn, addr):
		while True:
			try:
				res = conn.recv(1024)
				# [[order_type], [filename], [ip], [port], [ttl]]
				if not res:
					continue
				else:
					self.__cmd = res.decode('utf-8').split()
					# print("\n收到请求报文：%s" % self.__cmd)
					# 收到请求的格式有get、found、request三种
					if self.__cmd[0] == 'get' and self.__state == 0: # 只有不在发送状态时才能处理get
						res = self.update_ttl(res) # ttl-1
						self.__source_ip = self.__cmd[2]
						self.__source_port = self.__cmd[3]
						self.__query_res[self.__cmd[1]] = 0 # 0标志本地未找到，1标志本地找到
						self.query(self.__share_dir, self.__cmd[1])
						# print("处理请求：在本地查找 %s " % self.__cmd[1])

						# 本地未找到，查询邻居节点
						if self.__query_res[self.__cmd[1]] == 0:
							if int(self.__cmd[-1]) >= 0:
								if int(self.__cmd[-1]) <= 1: # 达到跳数限制就不再执行请求了
									print("\n跳数达到上限")
									continue
								print("\n本地未找到，向邻居发送请求")
								self.__state = 1
								for i in range(0, len(self.__ips)):
									if self.__ips[i] == self.__source_ip and self.__ports[i] == self.__source_port: # 不能给请求方发送查找的请求
										continue
									else:
										# print("send one in connection.py")
										self.tcp_client_notice(self.__ips[i], self.__ports[i], res)
							else:
								# print("请求已达到最大跳数限制")
								pass

						else:
							# print("本地找到，向请求源server发送成功消息")
							msg = "found %s at %s %s" % (self.__cmd[1], self.__ip_addr, self.__server_port)
							self.tcp_client_notice(self.__source_ip, self.__source_port, msg)

						time.sleep(1.5) # 等待1.5秒
						self.__state = 0 # 退出发送状态

					elif self.__cmd[0] == 'get' and self.__state == 1: # 在发送状态，不处理get
						pass

					# 收到“found filename at [ip] [port]”，向请求的源server发送request请求
					elif self.__cmd[0] == 'found':
						self.__source_ip = self.__cmd[3]
						self.__source_port = self.__cmd[4]
						msg = 'request %s %s %s' % (self.__cmd[1], self.__ip_addr, self.__server_port)
						self.tcp_client_notice(self.__source_ip, self.__source_port, msg)

					# 收到“request filename [ip] [port]”消息，即向请求源发送文件
					elif self.__cmd[0] == 'request':
						self.__send(conn, self.__cmd[1])
						print("\n发送完成, 按回车继续操作")
					else:
						msg = "不合法的命令"
						conn.send(msg.encode())

			except ConnectionResetError:
				print("!!!连接断开")
				break
		conn.close()


	def tcp_server(self):
		tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		tcp_server.bind((self.__ip_addr, self.__server_port))
		tcp_server.listen(5)
		while True:
			try:
				conn, addr = tcp_server.accept()
			except ConnectionAbortedError:
				print("!!!服务器连接异常终止")
				continue
			t = threading.Thread(target=self.tcp_handler, args=(conn, addr))
			t.start()


	def __send(self, conn, filename):
		true_name = filename
		filepath = self.__path_list[filename]
		if filename.find('.') != -1:
			filename = filename[0:filename.find('.')] + ".zip"
		else:
			filename = filename + ".zip"
		z = zipfile.ZipFile(filename, 'w')
		if os.path.isdir(filepath):
			for d in os.listdir(filepath):
				z.write(filepath + os.sep + d, d)
		else:
			z.write(filepath, true_name)
		z.close()
		header_dic = {
			'filename': filename,
			'md5': file_hash.get_file_md5(filename),
			'file_size': z.infolist()[0].file_size
		}
		header_json = json.dumps(header_dic)
		header_bytes = header_json.encode('utf-8')
		# 打包文件头
		conn.send(struct.pack('i', len(header_bytes)))
		# 发送头
		conn.send(header_bytes)
		# 发送数据
		send_size = 0
		with open(filename, 'rb') as f:
			for b in f:
				conn.send(b)
				send_size += len(b)
		while True:
			try:
				os.remove(filename)
				break
			except:
				continue


	def __save(self, conn):
		obj = conn.recv(4)
		header_size = struct.unpack('i', obj)[0]
		# 接收头
		header_bytes = conn.recv(header_size)
		# 解包头
		header_json = header_bytes.decode('utf-8')
		header_dic = json.loads(header_json)
		total_size = header_dic['file_size']
		filename = header_dic['filename']
		cur_md5 = header_dic['md5']
		# 接收数据
		with open('%s%s' % (self.__share_dir, filename), 'wb') as f:
			recv_size = 0
			while recv_size < total_size:
				res = conn.recv(1024)
				f.write(res)
				recv_size += len(res)
			# print("文件总大小: %s, 已下载: %s" % (total_size, recv_size))
		if file_hash.compare_file_md5('%s%s' % (self.__share_dir, filename), cur_md5) == 1:
			z = zipfile.ZipFile("%s%s" % (self.__share_dir, filename), 'r')
			z.extractall("%s" % self.__share_dir)
			z.close()
			print("收到文件")
		else:
			print("文件在运输过程中被损坏")
		while True:
			try:
				os.remove("%s%s" % (self.__share_dir, filename))
				break
			except:
				continue


	def tcp_client_notice(self, ip, port, msg):
		tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try: # 如果对方未启动，则不会正常连接
			tcp_client.connect((ip, int(port)))
			tcp_client.send(msg.encode())
			if msg.split()[0] == 'request':
				self.__save(tcp_client)
			tcp_client.shutdown(2)
			tcp_client.close()
		except:
			pass


	def update_ttl(self, msg):
		msg = msg.decode().split()
		msg[-1] = str(int(msg[-1]) - 1)
		new_msg = " ".join(msg)
		return new_msg