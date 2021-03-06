#!usr/bin/python env
#_*_coding:utf-8_*_

import os, sys, threading, cmd, socket, Queue

portList = [21, 22, 23, 25, 80, 135, 137, 139, 445, 1433, 1502, 3306, 3389, 8080, 9015]
lock = threading.Lock()
threadCount = 20
openPort = []
timeout = 3
def GetQueue(list):
	portQueue = Queue.Queue(65535)
	for p in list:
		portQueue.put(p)
	return portQueue

class Scanner(threading.Thread):
	global openPort,timeout
	def __init__(self, ip):
		threading.Thread.__init__(self)
		self.ip = ip

	def Ping(self, port):
		addr = (self.ip, port)
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(timeout)
		try:
			sock.connect(addr)
		except:
			sock.close()
			return False
		sock.close()
		openPort.append(port)
		if lock.acquire():
			print "ip: %s   port:%s"%(self.ip, port)
			lock.release()
		return True
# use default port to scan
class ThreadScanSingle(Scanner):
	def __init__(self, scanIp, singleQueue):
		Scanner.__init__(self ,scanIp)
		self.singleQueue = singleQueue

	def run(self):
		while not self.singleQueue.empty():
			element = self.singleQueue.get()
			self.Ping(element)

#use the port you want to scan
class ThreadScanMult(Scanner):
	def __init__(self, scanIp, portList):
		Scanner.__init__(self, scanIp)
		self.list= portList[:]

	def run(self):
		for p in self.list:
			self.Ping(p)

class Shell(cmd.Cmd):
	def __init__(self):
		cmd.Cmd.__init__(self)
		reload(sys)
		sys.setdefaultencoding('utf-8')
		self.prompt = "Port Scan >>>"
		self.intro =  "hello, guy, welcome to the hack world"
	
	def do_EOF(self, line):
		return True

	#setting the port you want to know
	def do_port(self, line):
		global portList
		portList = []
		comPort = line.split(',')
		for item in comPort:
			if item.find('..')  >= 0:
				rangeLst = item.split('..')
				beginPort = rangeLst[0]
				endPort = rangeLst[1]
				if not beginPort.isdigit() and endPort.isdigit():
					raise ValueError
					exit()
				for p in range(int(beginPort), int(endPort)):
					portList.append(p)
			else:
				if not item.isdigit():
					print "error input"
					return False
				portList.append(int(item))

	def do_scan(self, line):
		global threadCount, portList
		threadList = []
		strIp = line

		SingleQueue = GetQueue(portList)
		for i in range(0, threadCount):
			t = ThreadScanSingle(strIp, SingleQueue)
			threadList.append(t)

		for t in threadList:
			t.start()

		for t in threadList:
			t.join()

	def do_search(self, line):
		global portList, threadCount
		threadList = []
		(beginIp, endIp) = line.split('-')
		try:
			socket.inet_aton(beginIp)
			socket.inet_aton(endIp)
		except:
			print "error input"
			return
		
		ipRange = beginIp[0:beginIp.rfind('.')]
		begin = beginIp[beginIp.rfind('.')+1:]
		end = endIp[endIp.rfind('.')+1:]
		#刚用过inet_aton(),此处可用print来验证
		
		for i in range(int(begin), int(end)):
			strIp = "%s.%s"%(ipRange, i)
			t = ThreadScanMult(strIp, portList)
			threadList.append(t)
			 
		for t in threadList:
			t.start()

		for t in threadList:
			t.join()
			
	def do_cls(self, line):
		os.system("cls")

if __name__ == '__main__':
	try:
		os.system("cls")
		shell = Shell()
		shell.cmdloop()
	except:
		exit()
