# coding=utf-8
"""
本模块用于分类器准确性测试
"""
import numpy as np
from random import shuffle
import sklearn
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn import cross_validation

class ClassifyProcess(object):

	def load_data(self, file_path):
		f = open(file_path)
		f.readline()
		data = np.loadtxt(f)
		shuffle(data)       # 随机打乱数据
		return data

	def split_data(self, data, train_percent):
		train_lines = len(data)*train_percent
		development = data[:train_lines, :]     # 前面的数据为训练集
		test = data[train_lines:, :]        # 后续数据为测试集
		train = development[:, 1:]
		tag = development[:, 0]     # 第一列为标签

	def do_classify(self, trian, tag):
		svc = svm.SVC(gamma=0.001, C=100.)
		lr = LogisticRegression(penalty='l1', tol=0.01)
		gnb = GaussianNB()

		kfold =  cross_validation.KFold(len(x1), n_folds=10)
