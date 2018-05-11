from bs4 import BeautifulSoup
import PyV8
import re


def imitate_cookie(self, r_1):
    print '**********************************************imitate_cookie'
    ctxt = PyV8.JSContext()
    ctxt.enter()
    soup = BeautifulSoup(r_1.text, 'lxml')
    # print soup
    script1 = soup.select('script')[0].text
    # print script1
    script2 = ("(function(){" + script1.replace('eval(y', 'return (y') + "})").encode('utf-8')
    # print '-'*100
    # print script2
    func = ctxt.eval(script2)
    script3 = func()
    # print script3

    script4 = script3.replace("while(window._phantom||window.__phantomas){};", "") \
        .replace("if((function(){try{return !!window.addEventListener;}catch(e){return false;}})())"
                 "{document.addEventListener('DOMContentLoaded',l,false);}else{document.attachEvent('onreadystatechange',l);}", '') \
        .replace(r"var h=document.createElement('div');h.innerHTML='<a href=\'/\'>x</a>';h=h.firstChild.href;",
                 "var h='http://www.gsxt.gov.cn/';")
    script5 = re.sub("document.cookie=.+\\);", 'return dc;', re.sub("setTimeout[^;]+;", '', script4)) + "return l();"
    # print script5.replace('return return', 'return')
    script6 = "(function(){" + script5 + "})"
    func2 = ctxt.eval(script6)
    cookie = func2()
    self.session.cookies.set(*cookie.split('='))