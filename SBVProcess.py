# -*- coding: utf-8 -*-
"""
IPOM预警流程为SBV+依存句法分析
本实验直接对比人工标注和从数据库中读取的数据
"""

import os
import os.path

def collect_dir(filePath):
	"""
	统计filePath中各文本所属级别，目录格式为
	-filePath:
		-level0:
			file1
			file2
			...
		+level1
		+level2
		+level3
	:param filePath: 根目录
	:return: 各文本所属级别的dict
	"""
	manualDict = {}
	for parent, dirnames, filenames in os.walk(filePath):
		for dirname in dirnames:
			for ps, dirs, filens in os.walk(filePath + '/' + dirname):
				for filename in filens:
					manualDict[filename] = int(dirname[5])
	return manualDict

def compare(manualDict, filePath):
	"""
	统计filePath中各文本所属级别，并与manualDict对比，目录格式为
	-filePath:
		-level0:
			file1
			file2
			...
		+level1
		+level2
		+level3
	:param filePath: 根目录
	:return: 返回一个矩阵用于计算P,R,F值
	"""
	lists = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
	for parent, dirnames, filenames in os.walk(filePath):
		for dirname in dirnames:
			for ps, dirs, filens in os.walk(filePath + '/' + dirname):
				for filename in filens:
					if manualDict.has_key(filename):
						lists[manualDict[filename]][int(dirname[5])] += 1
	return lists

def countPRF(lists):
	pfr_list = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
	for i in range(4):
		pfr_list[i][0] = float(lists[i][i])/sum(lists[i])
		pfr_list[i][1] = float(lists[i][i])/reduce(lambda x,y:x+y, (lists[j][i] for j in range(4)))
		pfr_list[i][2] = 2*pfr_list[i][0]*pfr_list[i][1]/(pfr_list[i][0]+pfr_list[i][1])
	accu = float(reduce(lambda x,y:x+y, (lists[i][i] for i in range(4))))/reduce(lambda x,y:x+y, (sum(lists[i]) for i in range(4)))
	return pfr_list,accu

lists = compare(collect_dir('data/manualMarked'), 'data/dataset')
pfr_list, accu = countPRF(lists)
print accu
for i in range(4):
	for j in range(3):
		print round(pfr_list[i][j],3), ' ',
	print '\n'
