# coding=utf-8

from V8Browser import HtmlWindow
from bs4 import BeautifulSoup
import requests
import time
import json
import re

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

    def get_gt_challenge(self, url):
        r2 = self.get_request(url)
        json_r2 = json.loads(r2.text)
        gt = json_r2['gt']
        challenge = json_r2['challenge']
        return gt, challenge


if __name__ == '__main__':
    kero = KeroSpider()
    url_1 = "http://www.gsxt.gov.cn/index.html"
    url_2 = 'http://www.gsxt.gov.cn/SearchItemCaptcha?v=' + kero.get_time_stamp()
    r = kero.get_request(url_1)
    kero.set_cookie_from_script(r.text)
    kero.get_gt_challenge(url_2)
    url_3 = 'http://api.geetest.com/gettype.php?gt={}&callback=geetest_{}'.format(kero.gt, kero.get_time_stamp())
    kero.get_request(url_3)
    url_4 = "http://api.geetest.com/ajax.php"
    print(kero.session.cookies)



