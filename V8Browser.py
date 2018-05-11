import requests
from urllib import unquote, quote
from urlparse import urljoin, urlparse
import logging
import platform

if platform.system() == 'Windows':
    import PyV8
else:
    from pyv8 import PyV8
import w3c
from bs4 import BeautifulSoup


class Navigator(PyV8.JSClass):
    use_proxy = True
    proxy = None
    log = logging.getLogger("navigator.base")

    def __init__(self, win=None):
        self._win = win

    @property
    def window(self):
        return self._win

    @property
    def appCodeName(self):
        """the code name of the browser"""
        raise NotImplementedError()

    @property
    def appName(self):
        """the name of the browser"""
        raise NotImplementedError()

    @property
    def appVersion(self):
        """the version information of the browser"""
        raise NotImplementedError()

    @property
    def cookieEnabled(self):
        """whether cookies are enabled in the browser"""
        raise NotImplementedError()

    @property
    def platform(self):
        """which platform the browser is compiled"""
        raise NotImplementedError()

    @property
    def userAgent(self):
        """the user-agent header sent by the browser to the server"""
        raise NotImplementedError()

    def javaEnabled(self):
        """whether or not the browser has Java enabled"""
        raise NotImplementedError()

    def taintEnabled(self):
        """whether or not the browser has data tainting enabled"""
        raise NotImplementedError()

    def fetch(self, url):
        headers = {
            'User-Agent': self.userAgent,
            'Referer': self._win.url,
        }
        if self._win.doc.cookie:
            headers['Cookie'] = self._win.doc.cookie
        kwargs = {'url': url, 'headers': headers}
        # if self.use_proxy:
        #     proxy_config = get_proxy()
        #     while self.proxy != proxy_config['proxy']:
        #         proxy_config = get_proxy()
        #     kwargs['proxies'] = {'http': proxy_config['proxy'], 'https': proxy_config['proxy']}
        #     kwargs['timeout'] = proxy_config['timeout']
        #     if 'headers' in kwargs:
        #         kwargs['headers']['Proxy-Authentication'] = proxy_config['secret_key']
        #     else:
        #         kwargs['headers'] = {'Proxy-Authentication': proxy_config['secret_key']}
        response = requests.get(**kwargs)
        return response


class Location(PyV8.JSClass):
    def __init__(self, win):
        # print '&&'*20
        self.win = win

    @property
    def parts(self):
        return urlparse(self.win.url)

    @property
    def href(self):
        return self.win.url

    @href.setter
    def href(self, url):
        print '(' * 5, url
        # r = requests.get(url)
        # soup = BeautifulSoup(r.text, 'lxml')
        # script = soup.select('script')[0].text
        # window = HtmlWindow(url=url, dom_or_doc=soup)
        # self.win = window
        # self.win.evalScript(script)
        # print window.document
        self.win.open(url)
        pass

    @property
    def protocol(self):
        return self.parts.scheme

    @property
    def host(self):
        return self.parts.netloc

    @property
    def hostname(self):
        return self.parts.hostname

    @property
    def port(self):
        return self.parts.port

    @property
    def pathname(self):
        return self.parts.path

    @property
    def search(self):
        return self.parts.query

    @property
    def hash(self):
        return self.parts.fragment

    def assign(self, url):
        """Loads a new HTML document."""
        print 'assign234567890-' * 100
        self.win.open(url)

    def reload(self):
        """Reloads the current page."""
        self.win.open(self.win.url)

    def replace(self, url):
        print '234567890-' * 100
        """Replaces the current document by loading another document at the specified URL."""
        self.win.open(url)


class InternetExplorer(Navigator):
    @property
    def appCodeName(self):
        return "Mozilla"

    @property
    def appName(self):
        return "Firefox/52.0"

    @property
    def appVersion(self):
        return "52.0"

    @property
    def cookieEnabled(self):
        """whether cookies are enabled in the browser"""
        raise True

    @property
    def platform(self):
        return "Mac OS X"

    @property
    def userAgent(self):
        return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:52.0) Gecko/20100101 Firefox/52.0"

    def javaEnabled(self):
        return False

    def taintEnabled(self):
        return False

    @property
    def userLanguage(self):
        import locale

        return locale.getdefaultlocale()[0]


class HtmlWindow(PyV8.JSClass):
    cur_request_response = None
    timers = []
    request_func = None

    class Timer(object):
        def __init__(self, code, repeat, lang='JavaScript'):
            self.code = code
            self.repeat = repeat
            self.lang = lang

    def __init__(self, url, dom_or_doc,
                 navigator_or_class=InternetExplorer,
                 request_func=None,

                 # name="", target='_blank',
                 # parent=None, opener=None, replace=False,
                 # screen=None,
                 # width=800, height=600, left=0, top=0,
                 **kwds):
        self.url = url
        self.doc = w3c.getDOMImplementation(dom_or_doc, **kwds) if isinstance(dom_or_doc, BeautifulSoup) else dom_or_doc
        self.doc.window = self
        self._navigator = navigator_or_class(self) if type(navigator_or_class) == type else navigator_or_class
        self.request_func = request_func
        self._location = Location(self)
        # self._history = History(self)
        # self._history.update(url, replace)
        # self._target = target
        # self._parent = parent
        # self._opener = opener
        # self._screen = screen or Screen(width, height, 32)
        self._closed = False
        # self.name = name
        # self.defaultStatus = ""
        # self.status = ""
        # self._left = left
        # self._top = top
        # self.innerWidth = width
        # self.innerHeight = height
        # self.outerWidth = width
        # self.outerHeight = height

    @property
    def closed(self):
        """whether a window has been closed or not"""
        return self._closed

    def close(self):
        """Closes the current window"""
        self._closed = True

    @property
    def window(self):
        return self

    @property
    def document(self):
        return self.doc

    def _findAll(self, tags):
        return self.doc.doc.findAll(tags, recursive=True)

    @property
    def frames(self):
        """an array of all the frames (including iframes) in the current window"""
        return w3c.HTMLCollection(self.doc, [self.doc.createHTMLElement(self.doc, f) for f in self._findAll(['frame', 'iframe'])])

    @property
    def length(self):
        """the number of frames (including iframes) in a window"""
        return len(self._findAll(['frame', 'iframe']))

    # @property
    # def history(self):
    #     """the History object for the window"""
    #     return self._history

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, url):
        """the Location object for the window"""
        self.open(url)

    @property
    def navigator(self):
        """the Navigator object for the window"""
        return self._navigator

    @property
    def opener(self):
        """a reference to the window that created the window"""
        return self._opener

    @property
    def pageXOffset(self):
        return 0

    @property
    def pageYOffset(self):
        return 0

    @property
    def parent(self):
        return self._parent

    @property
    def screen(self):
        return self._screen

    @property
    def screenLeft(self):
        return self._left

    @property
    def screenTop(self):
        return self._top

    @property
    def screenX(self):
        return self._left

    @property
    def screenY(self):
        return self._top

    @property
    def self(self):
        return self

    @property
    def top(self):
        return self

    def alert(self, msg):
        """Displays an alert box with a message and an OK button"""
        print "ALERT: ", msg

    def confirm(self, msg):
        """Displays a dialog box with a message and an OK and a Cancel button"""
        ret = raw_input("CONFIRM: %s [Y/n] " % msg)

        return ret in ['', 'y', 'Y', 't', 'T']

    def focus(self):
        """Sets focus to the current window"""
        pass

    def blur(self):
        """Removes focus from the current window"""
        pass

    def moveBy(self, x, y):
        """Moves a window relative to its current position"""
        pass

    def moveTo(self, x, y):
        """Moves a window to the specified position"""
        pass

    def resizeBy(self, w, h):
        """Resizes the window by the specified pixels"""
        pass

    def resizeTo(self, w, h):
        """Resizes the window to the specified width and height"""
        pass

    def scrollBy(self, xnum, ynum):
        """Scrolls the content by the specified number of pixels"""
        pass

    def scrollTo(self, xpos, ypos):
        """Scrolls the content to the specified coordinates"""
        pass

    def setTimeout(self, code, interval, lang="JavaScript"):
        timer = HtmlWindow.Timer(code, False, lang)
        self.timers.append((interval, timer))

        return len(self.timers) - 1

    def clearTimeout(self, idx):
        self.timers[idx] = None

    def setInterval(self, code, interval, lang="JavaScript"):
        timer = HtmlWindow.Timer(code, True, lang)
        self.timers.append((interval, timer))

        return len(self.timers) - 1

    def clearInterval(self, idx):
        self.timers[idx] = None

    def createPopup(self):
        raise NotImplementedError()

    def open(self, url=None, name='_blank'):
        # self.log.info("window.open(url='%s', name='%s', specs='%s')", url, name, specs)
        new_url = urljoin(self.url, url)
        if self.request_func:
            headers = {
                'User-Agent': self.navigator.userAgent,
                'Referer': self.url,
            }
            if self.doc.cookie:
                headers['Cookie'] = self.doc.cookie
            kwargs = {'url': new_url, 'headers': headers}
            self.cur_request_response = self.request_func(**kwargs)
        else:
            self.cur_request_response = self._navigator.fetch(new_url)
        self.url = new_url

    def refresh_page(self, page_encoding=None):
        # print 'page_encoding ->', page_encoding
        if page_encoding:
            self.cur_request_response.encoding = page_encoding
        html = self.cur_request_response.text
        dom = BeautifulSoup(html, 'lxml')
        self.doc = w3c.getDOMImplementation(dom)

    @property
    def context(self):
        if not hasattr(self, "_context"):
            self._context = PyV8.JSContext(self)
            # print '*********************'*100
        # print 'type(self._context)', type(self._context)
        return self._context

    def evalScript(self, script, tag=None):
        if isinstance(script, unicode):
            script = script.encode('utf-8')
        if tag:
            self.doc.current = tag
        else:
            try:
                body = self.doc.body
                # body.tag <class 'bs4.element.Tag'>
                self.doc.current = body.tag.contents[-1] if body else self.doc.doc.contents[-1]
            except IndexError:
                head = self.doc.head
                self.doc.current = head.doc.contents[-1]
        # self.log.debug("executing script: %s", script)
        with self.context as ctxt:
            ctxt.eval(script)

    def eval(self, script):
        self.evalScript(script)

    def fireOnloadEvents(self):
        for tag in self._findAll('script'):
            self.evalScript(tag.string, tag=tag)

        body = self.doc.body


        if body and body.tag.has_key('onload'):
            self.evalScript(body.tag['onload'], tag=body.tag.contents[-1])

        if hasattr(self, 'onload'):
            self.evalScript(self.onload)

    def fireExpiredTimer(self):
        pass

    def Image(self):
        return self.doc.createElement('img')

    def encodeURIComponent(self, query):
        def quote_plus(s, safe=''):
            if ' ' in s:
                s = quote(s, safe + ' ')
                return s.replace(' ', '%20')
            return quote(s, safe)
        return quote_plus(query)

    def decodeURIComponent(self, encoded_component):
        return unquote(encoded_component)


