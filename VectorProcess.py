# coding=utf-8
"""
本模块用于处理LTP语义依存分析返回值，生成句子向量和文档向量
"""
import json


class VectorProcess(object):
	def __init__(self, dict_path):
		# 语义角色
		self._semantic_role_dict = {'A0': 0, 'A1': 1, 'A2': 2, 'A3': 3, 'A4': 4, 'A5': 5,
		                            'ADV': 6, 'BNE': 7, 'CND': 8, 'DIR': 9, 'DGR': 10,
		                            'EXT': 11, 'FRQ': 12, 'LOC': 13, 'MNR': 14, 'PRP': 15,
		                            'TMP': 16, 'TPC': 17, 'CDR': 18, 'PRD': 19, 'PSR': 20, 'PSE': 21}
		# 语义依附标记以m开头，事件关系以e开头或者在一下列表中，其余为语义角色
		self._semantic_dependency_list = ['Agt', 'Exp', 'Aft', 'Poss', 'Pat', 'Cont', 'Prod', 'Orig', 'Datv']
		# 词汇敏感性对照表
		self._sensitive_tag_dict = {'P2': 2.0, 'P1': 1.0, 'M0': 0.0, 'N1': -1.0, 'N2': -2.0}
		self._sen_dict = {}
		self.gen_sen_dict(dict_path)

	def gen_sen_dict(self, dict_path):
		for line in open(dict_path, 'r'):
			line_splits = line.strip().split(',')
			if len(line_splits) > 1:
				self._sen_dict[unicode(line_splits[0], 'utf-8')] = unicode(line_splits[1], 'utf-8')

	@staticmethod
	def merge_vector(vector1, vector2, length=22):
		digm1 = 0.0
		digm2 = 0.0
		digmcos = 0.0
		for i in range(length):
			digm1 += vector1[i] * vector1[i]
			digm2 += vector2[i] * vector2[i]
			digmcos += vector1[i] * vector2[i]
		if digm1 + digm2 - digmcos == 0:
			return [0 for i in range(length)]
		dcos1 = (digm1 - digmcos / 2) / (digm1 + digm2 - digmcos)
		dcos2 = (digm2 - digmcos / 2) / (digm1 + digm2 - digmcos)
		vector_merge = [0 for i in xrange(length)]
		for i in xrange(length):
			vector_merge[i] = dcos1 * vector1[i] + dcos2 * vector2[i]
		return vector_merge

	def add_sensitive_tag(self, doc_json):
		"""this module used to add sensitive tag to ltp json"""
		# todo: use crf predict words sensitive tag
		for paragraph in doc_json:
			for sentence in paragraph:
				for word in sentence:
					if type(word) != dict: continue
					if ('cont' in word) and (word['cont'] in self._sen_dict.keys()):
						sentence[int(word['id'])]['sen_tag'] = self._sen_dict[word['cont']]
					else:
						sentence[int(word['id'])]['sen_tag'] = 'M0'
		return doc_json

	def transform_sensitive(self, doc_json):
		# todo: use rules in paper transform sensitive to words
		for paragraph in doc_json:
			for sentence in paragraph:
				for word in sentence:
					if type(word) != dict: continue
					if 'sem' not in word: continue
					for sem in word['sem']:
						# 判断合法性
						if not (sentence[int(sem['id'])]
						        or sentence[int(sem['parent'])]
						        or sentence[int(sem['id'])]['sen_tag']
						        or sentence[int(sem['parent'])]['sen_tag']
						        or self._sensitive_tag_dict.has_key(sentence[int(sem['parent'])]['sen_tag'])):
							continue
						if sem['relate'].startswith('m'):
							# 语义依附标记，乘法原则
							if 'm_relate' not in sentence[int(sem['id'])]:
								sentence[int(sem['id'])]['m_relate'] = 0.0
							if 'sen_tag' in sentence[int(sem['parent'])]:
								sentence[int(sem['id'])]['m_relate'] += \
									self._sensitive_tag_dict[sentence[int(sem['parent'])]['sen_tag']]
						elif sem['relate'].startswith('e') or (sem['relate'] in self._semantic_dependency_list):
							# 事件关系，折半传递
							if 'e_relate' not in sentence[int(sem['id'])]:
								sentence[int(sem['id'])]['e_relate'] = 0.0
							if 'sen_tag' in sentence[int(sem['parent'])]:
								sentence[int(sem['id'])]['e_relate'] += \
									self._sensitive_tag_dict[sentence[int(sem['parent'])]['sen_tag']] / 2
						elif sem['relate'] != 'Root':
							# 语义角色，max(abs())
							if 'r_relate' not in sentence[int(sem['id'])]:
								sentence[int(sem['id'])]['r_relate'] = \
									self._sensitive_tag_dict[sentence[int(sem['id'])]['sen_tag']] \
									if 'sen_tag' in sentence[int(sem['id'])] else 0.0
							sem_parent = \
								self._sensitive_tag_dict[sentence[int(sem['parent'])]['sen_tag']] \
								if 'sen_tag' in sentence[int(sem['parent'])] else 0.0
							if abs(sem_parent) > abs(sentence[int(sem['id'])]['r_relate']):
								sentence[int(sem['id'])]['r_relate'] = sem_parent
		return doc_json

	def generate_vector(self, doc_json):
		"""
        核心语义角色有6种：A0~A5
        附加语义角色有16种
        生成的向量维度为22
        :param doc_json:  文本json串
        :return: 文本向量
        """
		semantic_vector = [0 for i in xrange(22)]
		for paragraph in doc_json:
			for sentence in paragraph:
				for word in sentence:
					if type(word) != dict: continue
					word['sensitive'] = 0.0
					if 'r_relate' in word:
						word['sensitive'] = word['r_relate']
					elif 'sen_tag' in word and (word['sen_tag'] in self._sensitive_tag_dict):
						word['sensitive'] = self._sensitive_tag_dict[word['sen_tag']]
					if 'e_relate' in word:
						word['sensitive'] += word['e_relate']
					if ('m_relate' in word) and word['m_relate'] != 0:
						word['sensitive'] *= word['m_relate']
				sentence_vector = [0 for i in xrange(22)]
				for word in sentence:
					if 'arg' not in word:
						continue
					for arg in word['arg']:
						if self._semantic_role_dict.has_key(arg['type']):
							for i in range(int(arg['beg']), int(arg['end'])):
								sentence_vector[self._semantic_role_dict[arg['type']]] += sentence[i]['sensitive']
				semantic_vector = self.merge_vector(semantic_vector, sentence_vector)
		return semantic_vector

	def vector_analysis(self, doc_json):
		try:
			doc_json = json.loads(doc_json)
		except ValueError:
			print "value error: %s" % doc_json[0:50] if len(doc_json) > 50 else doc_json
			return [0 for i in range(22)]
		doc_json = self.add_sensitive_tag(doc_json)
		doc_json = self.transform_sensitive(doc_json)
		return self.generate_vector(doc_json)
