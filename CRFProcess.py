# coding=utf-8
import codecs
import json
import os
import urllib
import urllib2

import time

from VectorProcess import VectorProcess


class CRFProcess(object):
    def ltp_cloud(self, par1):
        url_get_base = "http://api.ltp-cloud.com/analysis/"
        args = {
            "api_key": "g387O1F3GRuH6WJzGwgx7nJpiNfQhyMOrdrQzZIn",
            "text": par1,
            "pattern": "all",
            "format": "json"
        }
        # api_key = ''  # 用户注册语言云服务后获得的认证标识
        # format0 = 'json'  # 结果格式，有xml、json、conll、plain（不可改成大写）
        # pattern = 'all'  # 指定分析模式，有ws、pos、ner、dp、sdp、sdp_graph、srl和all
        # headers = {"User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1"}
        # req = urllib2.Request("%sapi_key=%s&text=%s&format=%s&pattern=%s"
        #                       % (url_get_base, api_key, par1, format0, pattern), headers=headers)
        count = 3
        while count > 0:
            count -= 1
            try:
                response = urllib.urlopen(url_get_base, urllib.urlencode(args))
                return response.read().strip()
            except urllib2.HTTPError, e:
                print e.code
                time.sleep(10)
        return None
        # result1 = urllib2.urlopen("%sapi_key=%s&text=%s&format=%s&pattern=%s"
        #                           % (url_get_base, api_key, par1, format0, pattern))

    def analysis_ltp(self, in_path):
        f = open(in_path, 'r')  # 待分析文本
        sem_vec = [0 for i in range(22)]

        linenum = 0
        newline = ""
        for line in f:
            linenum += 1  # 记录处理行数
            newline += line.strip()  # 删除行末空白符、干扰符号，以免影响URI

            if len(newline) > 6000:  # 让文本足够长时再提交处理，最大值在8000左右
                # print u"处理到第" + str(linenum) + u"行"
                count = 3
                while count > 0:
                    count -= 1
                    ltp_content = self.ltp_cloud(newline).decode("utf-8")
                    if ltp_content:
                        sem_vec = VectorProcess.merge_vector(sem_vec, vector_process.vector_analysis(ltp_content))
                        break
                    else:
                        print "http error, cannot get analysis data from ltp, try times %d" % (3-count)
                        time.sleep(10)
                time.sleep(3)
                newline = ""
        if newline != "":
            count = 3
            while count > 0:
                count -= 1
                ltp_content = self.ltp_cloud(newline).decode("utf-8")
                if ltp_content:
                    sem_vec = VectorProcess.merge_vector(sem_vec, vector_process.vector_analysis(ltp_content))
                    break
                else:
                    print "http error, cannot get analysis data from ltp, try times %d" % (3-count)
                    time.sleep(10)
            time.sleep(3)
        f.close()
        return sem_vec

    def generate_matrix(self, dir_path, out_path):
        savef = codecs.open(out_path, 'w', 'utf-8')
        count = 0
        for parent, dirnames, filenames in os.walk(dir_path):
            for dirname in dirnames:
                for sub_par, sub_dir, sub_files in os.walk(parent + os.sep + dirname):
                    for sub_file in sub_files:
                        count += 1
                        print "[%s]: process file %dth [%s%s%s]" % (
                            time.strftime('%Y-%m-%d %X', time.localtime(time.time())), count, dirname, os.sep, sub_file)
                        sem_vec = self.analysis_ltp(sub_par + os.sep + sub_file)
                        write_str = dirname[-1]
                        for sem in sem_vec:
                            write_str += ',' + str(round(sem, 6))
                        savef.write(write_str + "\n")
                        savef.flush()
                        # time.sleep(10)
        savef.close()


# noinspection PyArgumentList
vector_process = VectorProcess(r'data/Sentiment_word.csv')
crf_process = CRFProcess()
crf_process.generate_matrix(r"data/manualMarked", "out.txt")
