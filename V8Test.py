# coding=utf-8
# env: python2.7
from V8Browser import HtmlWindow
from bs4 import BeautifulSoup
import requests
import time
import json
import re


"""
暂时不支持任何EventListener
"""
class KeroSpider(object):
    def __init__(self):
        self.max_try_times = 4
        self.url = None
        self.window = None
        self.script = None
        self.session = requests.Session()
        self.gt = None
        self.challenge = None

    @staticmethod
    def get_time_stamp():
        return str(int(time.time() * 1000))

    def post_request(self, url, **kwargs):
        for t in range(self.max_try_times):
            # proxy_config = self.get_proxy()
            # # print 'proxy_config',proxy_config
            # kwargs['proxies'] = {'http': 'http://%(user)d:%(pwd)s@%(proxy)s' % proxy_config,
            #                      'https': 'https://%(user)d:%(pwd)s@%(proxy)s' % proxy_config}
            # kwargs['timeout'] = proxy_config['timeout']
            kwargs.setdefault('headers', {})
            kwargs['headers']['Connection'] = 'close'
            kwargs['headers']['User-Agent'] = \
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0'
            try:
                if self.session:
                    r = self.session.post(url=url, **kwargs)
                else:
                    r = requests.post(url=url, **kwargs)
                if 'The cache was not able to resolve the hostname presented in the URL' in r.text:
                    raise requests.exceptions.RequestException()
                else:
                    self.url = url
                    return r
            except (requests.exceptions.RequestException, IOError), e:
                if t == self.max_try_times - 1:
                    raise e

    def get_request(self, url, **kwargs):
        for t in range(self.max_try_times):
            kwargs.setdefault('headers', {})
            kwargs['headers']['User-Agent'] = \
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0'
            try:
                if self.session:
                    r = self.session.get(url=url, **kwargs)
                else:
                    r = requests.get(url=url, **kwargs)
                if 'The cache was not able to resolve the hostname presented in the URL' in r.text:
                    raise requests.exceptions.RequestException()
                else:
                    self.url = url
                    return r
            except (requests.exceptions.RequestException, IOError), e:
                if t == self.max_try_times - 1:
                    raise e

    def init_window(self, r_text):
        """
        初始化window对象
        :param r_text:
        :return:
        """
        soup = BeautifulSoup(r_text, 'lxml')
        self.script = soup.select('script')[0].text
        self.window = HtmlWindow(url=self.url, dom_or_doc=soup)

    def eval_script(self, script):
        self.window.evalScript(script)

    def set_cookie_from_script(self, r_text):
        self.init_window(r_text)
        self.eval_script(self.script)
        cookies = self.window.document.cookie
        l = [x for x in cookies.split(';') if x]
        _l = l[0].split('=')
        self.session.cookies.set(_l[0], _l[1])


if __name__ == '__main__':
    kero = KeroSpider()



