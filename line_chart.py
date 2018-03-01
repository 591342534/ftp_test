#!/usr/bin/env python
#coding=utf-8
from __future__ import print_function
import re
import matplotlib.pyplot as plt

def getSize(rate):
	if 'bit' in rate:
		return str(int(rate.split(' ')[0]) / 1024 / 1024)
	if 'Kb' in rate:
		return str(int(rate.split(' ')[0]) / 1024)
	if 'Mb' in rate:
		return rate.split(' ')[0]
	if 'Gb' in rate:
		return str(int(rate.split(' ')[0]) * 1024)
	

def getRate(line):
	dlrate = getSize(re.findall('DL Total Rate:(.*?),', line)[0])
	ulrate = getSize(re.findall('UL Total Rate:(.*)', line)[0])
	return [dlrate, ulrate]

def lineChart():
	dlrate = []
	ulrate = []
	x = 0
	with open('rate.txt', 'r') as r:
		while True:
			lines = r.readline()
			if not lines:
				break
				pass
			x += 1
			dlr, ulr = getRate(lines)
			dlrate.append(dlr)
			ulrate.append(ulr)
	x = range(0, x)
	plt.plot(x, dlrate, label='DL rate', linewidth=1, color='r',
	         markerfacecolor='blue')
	plt.plot(x, ulrate, label='UL rate', linewidth=1, color='b',
	         markerfacecolor='red')
	plt.xlabel('Time: s')
	plt.ylabel('Rate: Mb/s')
	plt.title('Rate Graph')
	plt.legend()
	plt.show()

if __name__ == "__main__":
	lineChart()
