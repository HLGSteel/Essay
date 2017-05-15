# -*- coding: utf-8 -*-

"""
功能：哈工大语言云使用测试
时间：2016年4月12日 19:56:11
"""

import urllib2
import codecs
import json

global sen_dict
sen_dict = {}

class LTPProcess(object):
	def __init__(self):
		self.gen_sen_dict(r'data\Sentiment_word.csv')

	def gen_sen_dict(self, dict_path):
		for line in open(dict_path, 'r'):
			line_splits = line.strip().split(',')
			if len(line_splits) > 1:
				global sen_dict
				sen_dict[unicode(line_splits[0], 'utf-8')] = unicode(line_splits[1], 'utf-8')

	def ltp_cloud(self, par1):
		url_get_base = "http://api.ltp-cloud.com/analysis/?"
		api_key = 'g387O1F3GRuH6WJzGwgx7nJpiNfQhyMOrdrQzZIn'  # 用户注册语言云服务后获得的认证标识
		format0 = 'json'  # 结果格式，有xml、json、conll、plain（不可改成大写）
		pattern = 'srl'  # 指定分析模式，有ws、pos、ner、dp、sdp、sdp_graph、srl和all
		result1 = urllib2.urlopen("%sapi_key=%s&text=%s&format=%s&pattern=%s"
		                          % (url_get_base, api_key, par1, format0, pattern))
		return result1.read().strip()

	def get_sen_tag(self, cont):
		global sen_dict
		if cont in sen_dict.keys():
			return sen_dict[cont]
		return 'M0'

	def gen_train_data(self, ltp_str):
		"""生成训练数据"""
		if not ltp_str:
			return None
		return_str = ''
		ltp_json = json.loads(ltp_str)
		for json1 in ltp_json:
			for json2 in json1:
				for json3 in json2:
					if json3['pos'] != 'wp':
						return_str += json3['cont'] + '\t' + json3['semrelate'] + '\t' + self.get_sen_tag(
							json3['cont']) + '\n'
		return return_str

	def gen_test_data(self, ltp_str):
		"""生成训练数据"""
		if not ltp_str:
			return None
		return_str = ''
		ltp_json = json.loads(ltp_str)
		for json1 in ltp_json:
			for json2 in json1:
				for json3 in json2:
					if json3['pos'] != 'wp':
						return_str += json3['cont'] + '\t' + json3['semrelate'] + '\n'
		return return_str

	def request_ltp(self, in_path, out_path, isTrain=True):
		f = open(in_path, 'r')  # 待分析文本
		savef = codecs.open(out_path, 'w', 'utf-8')

		linenum = 0
		newline = ""
		for line in f:
			linenum += 1  # 记录处理行数
			newline += line.strip().replace("#", "")  # 删除行末空白符、干扰符号，以免影响URI

			if line[-1] != "\n":  # 如果处理到文本最后一行
				if " and " and " in " in newline:
					print u"需要更改单词in"
					newline = newline.replace(" in ", " i.n ")
				print u"已处理到文本最后一行：", linenum
				ltp_content = self.ltp_cloud(newline).decode("utf-8")
				savef.write(self.gen_train_data(ltp_content) if isTrain else self.gen_test_data(ltp_content))

			if len(newline) > 6000:  # 让文本足够长时再提交处理，最大值在8000左右
				if " and " and " in " in newline:  # 不能同时含有and和in两个词
					print u"需要更改单词in"
					newline = newline.replace(" in ", " i.n ")
				print u"处理到第" + str(linenum) + u"行"
				ltp_content = self.ltp_cloud(newline).decode("utf-8")
				savef.write(self.gen_train_data(ltp_content) if isTrain else self.gen_test_data(ltp_content))
				newline = ""

		savef.close()
		f.close()

if __name__ == '__main__':
	ltpPro = LTPProcess()
	# ltpPro.request_ltp(r"data\newSensitive.csv", r"data\train_crf\newSensitive.txt")
	ltpPro.request_ltp(r"data\test.txt", r"data\train_crf\text.out")
