# coding=utf-8
import PackageTool
from crawler.SpiderMan import SpiderMan
import platform
from bs4 import BeautifulSoup
import re
import requests
from crawler import MySQL
from crawler import TimeUtils
import traceback
from crawler import Logger
import json
from crawler import TimeUtils, LastFbsj
# if platform.system() == 'Windows':
#     import PyV8
# else:
#     from pyv8 import PyV8
from V8Browser import HtmlWindow


class ShangHaiCrawler(SpiderMan):

    log_name = u'上海开庭公告'
    keep_ip = True

    def __init__(self):
        super(ShangHaiCrawler, self).__init__(keep_session=False, keep_ip=True, max_try_times=5)

    def info(self, msg):
        Logger.write(msg, name=self.log_name, print_msg=True)

    def submit_search_request(self, ktrqks=TimeUtils.get_today(), ktrqjs=TimeUtils.date_add(TimeUtils.get_today(), 365)):
        # ktrqks = '2017-05-10'
        # ktrqjs = '2017-06-10'
        res = 0
        yzm = None
        # if not yzm:
        #     yzm = self.get_yzm()
        pagesnum = 1
        url = "http://www.hshfy.sh.cn/shfy/gweb/ktgg_search_content.jsp"
        while True:
            self.info(json.dumps({'ktrqks': ktrqks, 'ktrqjs': ktrqjs, 'pagesnum': pagesnum}))
            # print {'ktrqks': ktrqks, 'ktrqjs': ktrqjs, 'pagesnum': pagesnum}
            params = {
                'ah': '',
                'bg': '',
                'ft': '',
                'ktrqjs': ktrqjs,
                'ktrqks': ktrqks,
                'pagesnum': pagesnum,
                'spc': '',
                'yg': '',
                # 'yzm': yzm
            }
            try:
                r = self.post(url=url, data=params)
                r.encoding = 'gbk'
                if u'暂时没有最新内容' in r.text:
                    break
                soup = BeautifulSoup(r.text, 'html5lib')

                window = HtmlWindow(url=url, dom_or_doc=soup, request_func=self.post)
                # print type(soup)
                for i in range(3):
                    if len(window.document.doc.select('script')) == 0:
                        break
                    script1 = soup.select('script')[0].text
                    window.evalScript(script1)
                    window.refresh_page('gbk')
                    if i == 2:
                        raise Exception(u'JS解析失败！')
                        # print '<' * 2, type(window.document.doc), '>' * 2
                soup = window.document.doc
                tr_list = soup.select('table[border="1"] > tbody > tr')
                if len(tr_list) > 1:
                    res = 1
                    for tr in tr_list[1:]:
                        # print tr

                        td_list = tr.select('td')
                        fy = td_list[0].text.strip().replace("'", "\\'")
                        ft = td_list[1].text.strip().replace("'", "\\'")
                        ktrq = td_list[2].text.strip().replace("'", "\\'")
                        ah = td_list[3].text.strip().replace("'", "\\'")
                        ay = td_list[4].text.strip().replace("'", "\\'")
                        cbbm = td_list[5].text.strip().replace("'", "\\'")
                        spz = td_list[6].text.strip().replace("'", "\\'")
                        yg = td_list[7].text.strip().replace("'", "\\'")
                        bg = td_list[8].text.strip().replace("'", "\\'")
                        sql = "select kai_ting_ri_qi from ktgg.shang_hai where an_hao='%s'" % ah
                        res = MySQL.execute_query(sql)
                        if len(res) == 0:
                            self.info(ah + '[new]')
                            sql = "insert into ktgg.shang_hai(fa_yuan,fa_ting,kai_ting_ri_qi,an_hao,an_you," \
                                  "cheng_ban_bu_men,shen_pan_zhang,yuan_gao,bei_gao,add_date," \
                                  "last_update_time) values('%s','%s','%s','%s','%s','%s','%s','%s','%s',date(now()),now())" \
                                  % (fy, ft, ktrq, ah, ay, cbbm, spz, yg, bg)
                            MySQL.execute_update(sql)
                        else:
                            self.info(ah)
                pagesnum += 1

            except Exception, e:
                traceback.print_exc(e)
                continue

                # print r.text
                # if u'访问本页面，您的浏览器需要支持JavaScript' in r.text:
                #     print u'访问本页面，您的浏览器需要支持JavaScript'
                #     # self.proxy = None
                #     try:
                #         yzm = self.get_yzm(r)
                #         # print 'yzm', yzm
                #     except Exception, e:
                #         traceback.print_exc(e)
                #         pass
                # elif u'暂时没有最新内容' in r.text:
                #     break
                # else:
                #     soup = BeautifulSoup(r.text, 'html5lib')

        self.info(u'抓取完毕')
        return res

    # def get_yzm(self, r=None, url='http://www.hshfy.sh.cn/shfy/gweb/ktgg_search.jsp'):
    #     # url = 'http://www.hshfy.sh.cn/shfy/gweb/ktgg_search.jsp'
    #     while True:
    #         if not r:
    #             r = self.get(url)
    #             r.encoding = 'gb2312'
    #             # print r.text
    #         search_res = re.search('yzm="[^"]+"', r.text)
    #         if search_res:
    #             return search_res.group().split('"')[1]
    #         soup = BeautifulSoup(r.text, 'html5lib')
    #         script = soup.select('script')[0].text.encode('gb2312')
    #         # print script
    #         ctxt = PyV8.JSContext()
    #         ctxt.enter()
    #         try:
    #             ctxt.eval(script)
    #         except Exception, e:
    #             # print e
    #             msg = str(e)
    #             # print msg
    #             if 'window.location=' in msg:
    #                 url_path = msg.split('window.location=')[-1]
    #             elif 'window.open' in msg:
    #                 url_path = msg.split('window.open(')[-1].split(',')[0]
    #             # print url_path
    #             var_1, var_2 = url_path.split('+')[0], url_path.split('+')[2]
    #             # print var_1, var_2
    #             val_1 = re.search(var_1+'="[^"]+"', script).group().replace(var_1+'=', '')
    #             val_2 = re.search(var_2 + '="[^"]+"', script).group().replace(var_2+'=', '')
    #             # print val_1, val_2
    #             url_path = eval(val_1+url_path.split('+')[1]+val_2)
    #             # print url_path
    #             url = "http://www.hshfy.sh.cn"+url_path
    #             # print url
    #             r = self.get(url)
    #             r.encoding = 'gb2312'
    #             # print r.text
    #             search_res = re.search('yzm="[^"]"', r.text)
    #             if search_res:
    #                 return search_res.group().split('"')[1]
    #             else:
    #                 continue

    def run(self):
        dt = TimeUtils.get_today()
        ktrqks = LastFbsj.get_last_fbsj(self.log_name)
        self.submit_search_request(ktrqks=ktrqks)
        LastFbsj.update_last_fbsj(self.log_name, dt)


if __name__ == '__main__':
    crawler = ShangHaiCrawler()
    # print crawler.get_yzm()
    # crawler.submit_search_request()
    crawler.run()
