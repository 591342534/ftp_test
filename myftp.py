#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
import sys
import os
import os.path
import time
import getopt
import threading
import logging
from ftplib import FTP
from config import Parsing_XML

is_running = True
is_connected = True

class MyFTP(threading.Thread):
	'''''
	conncet to FTP Server
	'''
	def __init__(self, configs, dir='DL', remotePath='', localPath='', remotepath='', localpath=''):
		threading.Thread.__init__(self)
		self.configs = configs
		self.direction=dir
		self.remoteHost = self.configs['ftp_host']
		self.remotePort = 21
		self.loginname = self.configs['ftp_user']
		self.loginpassword = self.configs['ftp_pw']
		self.remotePath = remotePath
		self.localPath = localPath
		self.remotepath = remotepath
		self.localpath = localpath
		self.datarate = 0
		self.logger = setloger()

	def run(self):
		if(self.direction=='DL'):
			self.download()
		else:
			self.upload()

	def ConnectFTP(self):
		ftp = FTP()
		try:
			ftp.connect(self.remoteHost, self.remotePort, 5)
		except Exception, e:
			return (0, '{} conncet failed'.format(self.remoteHost))
		else:
			try:
				ftp.login(self.loginname, self.loginpassword)
			except Exception, e:
				return (0, '{} login failed'.format(self.remoteHost))
			else:
				return (1, ftp)
	
	def download(self):
		global is_running
		global is_connected
		while True:
			if os.path.exists(self.localPath):
				os.remove(self.localPath)
			try:
				is_connected = True
				# connect to the FTP Server and check the return
				res = self.ConnectFTP()
				if (res[0] != 1):
					self.logger.warning(res[1])
					sys.exit()
			except:
				self.datarate = 0
				is_connected = False
				time.sleep(60)
				continue
			# change the remote directory and get the remote file size
			ftp = res[1]
			ftp.set_pasv(0)
			dires = self.splitpath(self.remotePath)
			if dires[0]:
				try:
					ftp.cwd(dires[0])  # change remote work dir
				except:
					self.logger.error('remote work dir does not exist...')
					is_running = False
					sys.exit(1)
			remotefile = dires[1]  # remote file name
			# print(('{} {}').format(dires[0], dires[1]))
			try:
				fsize = ftp.size(remotefile)
			except:
				self.logger.error('remotefile does not exist...')
				is_running = False
				sys.exit(1)
			# check local file isn't exists and get the local file size
			lsize = 0L
			if os.path.exists(self.localPath):
				lsize = os.stat(self.localPath).st_size
			if lsize >= fsize:
				os.remove(self.localPath)
				lsize = 0L
			blocksize = 1024 * 1024
			cmpsize = lsize
			ftp.voidcmd('TYPE I')
			conn = ftp.transfercmd('RETR ' + remotefile, lsize)
			# lwrite = open(self.localPath, 'ab')
			while True:
				exit_flag = False
				d = 0L
				stime = time.time()
				while True:
					try:
						data = conn.recv(blocksize)
					except:
						exit_flag = True
						break
					if not data:
						exit_flag = True
						break
					# lwrite.write(data)
					cmpsize += len(data)
					d += len(data)
					dtime = time.time()
					if float(dtime - stime) > 0.95:
						break
				if exit_flag:
					break
				# print('\n', '{} download process:{:.2f}%'.format(remotefile, float(cmpsize) / fsize * 100))
				# print('\n', 'download speed:{:.2f}'.format(float(d) / float(time.time() - stime) / 1024 / 1024))
				self.datarate = (float(d) / float(time.time() - stime))
			# lwrite.close()
			try:
				ftp.voidcmd('NOOP')
				ftp.voidresp()
				conn.close()
				ftp.quit()
			except Exception as msg:
				print(msg)

	def upload(self, callback=None):
		global is_running
		global is_connected
		while True:
			if not os.path.exists(self.localpath):
				self.logger.error("{} doesn't exists".format(self.localpath))
				is_running = False
				sys.exit(1)
			try:
				is_connected = True
				res = self.ConnectFTP()
				if res[0] != 1:
					self.logger.warning(res[1])
					sys.exit()
			except:
				self.datarate = 0
				is_connected = False
				time.sleep(60)
				continue
			ftp = res[1]
			try:
				ftp.delete(self.remotepath)
			except:
				pass
			remote = self.splitpath(self.remotepath)
			try:
				ftp.cwd(remote[0])
			except:
				self.logger.error('remote work dir does not exist...')
				is_running = False
				sys.exit(1)
			rsize = 0L
			try:
				rsize = ftp.size(remote[1])
			except:
				pass
			if (rsize == None):
				rsize = 0L
			lsize = os.stat(self.localpath).st_size
			if (rsize >= lsize):
				ftp.delete(self.remotepath)
				rsize = 0L
			# print('rsize : {:d}, lsize : {:d}'.format(rsize, lsize))
			if (rsize < lsize):
				localf = open(self.localpath, 'rb')
				localf.seek(rsize)
				ftp.voidcmd('TYPE I')
				datasock = ''
				esize = ''
				try:
					datasock, esize = ftp.ntransfercmd("STOR " + remote[1], rsize)
				except Exception, e:
					print('----------ftp.ntransfercmd-------- : {}'.format(e))
					return
				cmpsize = rsize
				while True:
					exit_flag = False
					d = 0L
					stime = time.time()
					while True:
						buf = localf.read(1024 * 1024)
						if not len(buf):
							exit_flag = True
							break
						try:
							datasock.sendall(buf)
						except:
							exit_flag = True
							break
						if callback:
							callback(buf)
						cmpsize += len(buf)
						d += len(buf)
						if float(time.time() - stime) > 0.95:
							break
					if exit_flag:
						break
					# print('\n', '{} uploading {:.2f}%'.format(remote[1], float(cmpsize) / lsize * 100))
					# print('\n', 'upload speed:{:.2f}'.format(float(d) / float(time.time() - stime) / 1024 / 1024))
					self.datarate = (float(d) / float(time.time() - stime))
					if cmpsize == lsize:
						ftp.delete(self.remotepath)
				try:
					datasock.close()
					localf.close()
					ftp.voidcmd('NOOP')
					ftp.voidresp()
					ftp.quit()
				except Exception as msg:
					self.logger.error('ftp quit error:%s'%msg)
	
	def splitpath(self, remotepath):
		position = remotepath.rfind('/')
		return (remotepath[:position + 1], remotepath[position + 1:])

class MyThread:
	def __init__(self,configs):
		self.configs = configs
		self.dlthreadnum = self.configs['ftp_dlthreadnum']
		self.ulthreadnum = self.configs['ftp_ulthreadnum']
		self.servicetime = self.configs['ftp_servicetime']
		self.remotePath = self.configs['ftp_dlremotepath']
		self.localPath = self.configs['ftp_dllocalpath']
		self.remotepath = self.configs['ftp_ulremotepath']
		self.localpath = self.configs['ftp_ullocalpath']
		self.loadthreads = []
		self.ratelogger = setrateloger()

	def dotest(self):
		global is_running
		# create test thread
		for i in range(int(self.dlthreadnum)):
			downthread =MyFTP(self.configs, dir='DL',remotePath=self.remotePath+str(i), localPath=self.localPath+str(i))
			self.loadthreads.append(downthread)
		for i in range(int(self.ulthreadnum)):
			upthread = MyFTP(self.configs, dir='UL',remotepath=self.remotepath+str(i), localpath=self.localpath+str(i))
			self.loadthreads.append(upthread)
		for thread in self.loadthreads:
			thread.setDaemon(True)
			thread.start()
		starttime = time.time()
		rate = []
		time.sleep(2)
		while time.time()-starttime < int(self.servicetime):
			if is_connected:
				if is_running:
					dlsum=0
					ulsum=0
					for thread in self.loadthreads:
						if thread.direction=='DL':
							dlsum+=thread.datarate
						else:
							ulsum+=thread.datarate
						thread.datarate = 0
					dlrate = beautifySize(dlsum)
					ulrate = beautifySize(ulsum)
					self.ratelogger.info('DL Total Rate:{}, UL Total Rate:{}'.format(dlrate, ulrate))
					time.sleep(1)
				else:
					sys.exit(1)
			else:
				pass
		self.ratelogger.info('Ftp test finish...')
		
def beautifySize(size):
	if size / 1073741824 > 1:
		return ("%(size)0.2f Gb/s") %{ 'size' : (float(size) / 1073741824.0 * 8) }
	elif size / 1048576 > 1:
		return ("%(size)0.2f Mb/s") %{ 'size' : (float(size) / 1048576.0 * 8) }
	elif size / 1024 > 1:
		return ("%(size)0.2f Kb/s") %{ 'size' : (float(size) / 1024.0 * 8) }
	else:
		return ("%(size)s bit/s") %{ 'size' : size * 8}

def setloger():
	logger = logging.getLogger('ftp_test')
	logger.setLevel(logging.DEBUG)
	fh = logging.FileHandler('debug.txt')
	fh.setLevel(logging.WARNING)
	ch = logging.StreamHandler(sys.stdout)
	ch.setLevel(logging.WARNING)
	formatter = logging.Formatter('%(asctime)s - %(name)s -%(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	ch.setFormatter(formatter)
	logger.addHandler(fh)
	logger.addHandler(ch)
	return logger

def setrateloger():
	logger = logging.getLogger('rate')
	logger.setLevel(logging.DEBUG)
	fh = logging.FileHandler('rate.txt')
	fh.setLevel(logging.INFO)
	ch = logging.StreamHandler(sys.stdout)
	ch.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s - %(name)s -%(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	ch.setFormatter(formatter)
	logger.addHandler(fh)
	logger.addHandler(ch)
	return logger

def argumentcheck():
	configs = Parsing_XML().get_ftp_config()
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hD:U:H:u:p:t:l:r:L:R")
	except:
		usage()
	check = map(lambda x : x[0] ,opts)
	if '-D' not in check and '-U' in check:
		configs['ftp_dlthreadnum'] = 0
	if '-U' not in check and '-D' in check:
		configs['ftp_ulthreadnum'] = 0
	for op, value in opts:
		if op == "-D":
			configs['ftp_dlthreadnum'] = value
		elif op == "-U":
			configs['ftp_ulthreadnum'] = value
		elif op == "-H":
			configs['ftp_host'] = value
		elif op == "-u":
			configs['ftp_user'] = value
		elif op == "-p":
			configs['ftp_pw'] = value
		elif op == "-t":
			configs['ftp_servicetime'] = value
		elif op == "-l":
			configs['ftp_dllocalpath'] = value
		elif op == "-r":
			configs['ftp_dlremotepath'] = value
		elif op == "-L":
			configs['ftp_ullocalpath'] = value
		elif op == "-R":
			configs['ftp_ulremotepath'] = value
		elif op == "-h":
			usage()
	return configs

def usage():
	print('Usage: -D [dlthreadnum] -U[ulthreadnum] -H [ftphost] -u [username] -p [password] -t [servicetime] -l [dllocalpath] -r [dlremotepath] '
	      '-L [ullocalpath] -R [ulremotepath] -h')
	print('\t-D option: dl thread num')
	print('\t-U option: ul thread num')
	print('\t-H option: ftp host')
	print('\t-u option: username')
	print('\t-p option: password')
	print('\t-t option: service time')
	print('\t-l option: dl local file path')
	print('\t-r option: dl remote file path')
	print('\t-L option: ul local file path')
	print('\t-R option: ul remote file path')
	print('\t-h option: print this help information')
	sys.exit(10)
	
if __name__ == "__main__":
	configs = argumentcheck()
	if os.path.exists('debug.txt'): os.remove('debug.txt')
	if os.path.exists('rate.txt'): os.remove('rate.txt')
	MyThread(configs).dotest()
