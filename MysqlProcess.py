#coding=utf-8
import MySQLdb
import codecs

conn= MySQLdb.connect(
        host='10.3.255.99',
        port=3306,
        user='ipom_website',
        passwd='EoZo#6#dW2zT',
        db='ipom_spider_byr',
        # db='ipom_analysis_realtimeAnalysis_sensitive',
        charset='utf8',
        )
cur = conn.cursor()

# aa=cur.execute("SELECT `site_name`,`bid`,`aid`,`title`,`content`,`level` FROM `newSensitive` WHERE `find_time` BETWEEN '2017-01-12' AND '2017-02-12' AND level=2")
# aa=cur.execute("SELECT `site_name`,`bid`,`aid`,`title`,`content`,`level` FROM `newSensitive` WHERE `find_time` BETWEEN '2017-01-13' AND '2017-01-19' AND level=1")
# 补充level0数据，700条
aa=cur.execute("SELECT `extra1`,`bid`,`aid`,`title`,`content` FROM article WHERE ((aid,bid) not IN(SELECT aid, bid from ipom_analysis_realtimeAnalysis_sensitive.newSensitive)) AND length(content)>200 AND bid IN('Picture','Friends','FamilyLife','Beauty') ORDER BY post_time DESC LIMIT 0,500")

info = cur.fetchmany(aa)
for ii in info:
    file_path = 'data\\appendix\\level%d\\%s_%s_%s' %(0, ii[0], ii[1], ii[2])
    # file_path = 'data\\appendix\\level%d\\%s_%s_%s' %(int(ii[5]), ii[0], ii[1], ii[2])
    savef = codecs.open(file_path, 'w', 'utf-8')
    savef.write(ii[3].replace(' ', '') +"\n"+ii[4].replace(' ', '') +"\n")
    savef.close()
cur.close()
conn.commit()
conn.close()