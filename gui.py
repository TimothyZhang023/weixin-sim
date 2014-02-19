#  -*-  coding: utf-8  -*-

import time
import random
import urllib2
import hashlib
import xml.etree.cElementTree as ET
import os
import Tkinter as tk
import ScrolledText as st


settings = {
    # `ToUserName` & `FromUserName` will be placed in the XML data posted to
    # the given URL.
    "ToUserName": "gh_bea8cf2a04fd",
    "FromUserName": "oLXjgjiWeAS1gfe4ECchYewwoyTc",

    # URL of your Wexin handler.
    #"url": "http://127.0.0.1/bookshare/weixin/index/index",
    "url": "http://127.0.0.1/green2014/weixin/index/index",


    # These will be displayed in GUI.
    "mp_display_name": "Z的博客",
    "me_display_name": "ZTS",

    # The token you submitted to Weixin MP. Used to generate signature.
    "token": "zts147258369"
}

TPL_TEXT = '''
<xml>
    <ToUserName><![CDATA[%(to)s]]></ToUserName>
    <FromUserName><![CDATA[%(from)s]]></FromUserName>
    <CreateTime>%(time)d</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[%(content)s]]></Content>
    <MsgId><![CDATA[%(id)s]]></MsgId>
</xml>
'''

TPL_EVENT = '''
<xml>
    <ToUserName><![CDATA[%(to)s]]></ToUserName>
    <FromUserName><![CDATA[%(from)s]]></FromUserName>
    <CreateTime>%(time)d</CreateTime>
    <MsgType><![CDATA[event]]></MsgType>
    <Event><![CDATA[%(event)s]]></Event>
    <EventKey><![CDATA[%(key)s]]></EventKey>
</xml>'''


def post(url, data):
    request = urllib2.Request(url, data)
    print 'request_url:' + url + '&request_data:'
    print data
    request.add_header("Content-Type", "text/xml")
    response = urllib2.urlopen(request)
    return response.read()


def str_os(str):
    if os.name == 'nt':
        return str.decode('utf-8').encode('gb2312')
    if os.name == '':
        return str


def send():
    s = text_input.get().encode('utf-8')     # Fix Chinese input.

    if s:
        text_output.insert(tk.END, settings["me_display_name"] + "\n", "send_name")
        text_output.insert(tk.END, s + "\n", "send_content")

        msg = {
            "to": settings["ToUserName"],
            "from": settings["FromUserName"],
            "time": time.time(),
            "content": s,
            "id": str(random.random())[-10:]
        }

        qs = "?signature=%s&timestamp=%s&nonce=%s" % \
             mix(int(msg["time"]), msg["id"])
        string2 = post(settings["url"] + qs, TPL_TEXT % msg)
        print 'raw:' + str_os(string2)
        receive(msg["time"], string2)
    else:
        text_output.insert(tk.END, settings["mp_display_name"] + "\n", "receive_name")
        text_output.insert(tk.END, u'请输入回复的内容' + "\n", "receive_content")
        return


def receive(start, response):
    if time.time() - start > 4.95:
        return
    print "Received:\n%s\n" % str_os(response)

    try:
        et = ET.fromstring(response)
        #print et.findall(".//ArticleCount").text

        if unicode(et.find("MsgType").text) == u'text':
            res_str = unicode(et.find("Content").text)
        elif unicode(et.find("MsgType").text) == u'image':
            res_str = response
        elif unicode(et.find("MsgType").text) == u'voice':
            res_str = response
        elif unicode(et.find("MsgType").text) == u'video':
            res_str = response
        elif unicode(et.find("MsgType").text) == u'music':
            res_str = response

        elif unicode(et.find("MsgType").text) == u'news':
            res_str = response

    except:
        print u'服务器返回异常'

        #res_str = u'服务器返回异常，详情请看debug窗口:'

    text_output.insert(tk.END, settings["mp_display_name"] + "\n", "receive_name")
    text_output.insert(tk.END, res_str + "\n", "receive_content")


def mix(time, salt):
    timestamp = str(time)

    # I don'text_output know how Weixin generate nonce, so I turn to random.
    nonce = str(time + int(salt[-6:]))

    l = [timestamp, nonce, settings["token"]]
    l.sort()
    signature = hashlib.sha1("".join(l)).hexdigest()

    return (signature, timestamp, nonce)


def follow():
    msg = {
        "to": settings["ToUserName"],
        "from": settings["FromUserName"],
        "time": time.time(),
        "event": "subscribe",
        "key": ""       # `EventKey` in `subscribe` event is empty.
    }
    qs = "?signature=%s&timestamp=%s&nonce=%s" % \
         mix(int(msg["time"]), str(random.random())[-10:])
    receive(msg["time"], post(settings["url"] + qs, TPL_EVENT % msg))


def event():
    key = text_input.get().encode('utf-8')
    if key == '':
        text_output.insert(tk.END, settings["mp_display_name"] + "\n", "receive_name")
        text_output.insert(tk.END, u'请输入按键的值' + "\n", "receive_content")
        return
    msg = {
        "to": settings["ToUserName"],
        "from": settings["FromUserName"],
        "time": time.time(),
        "event": "CLICK",
        "key": key       # `EventKey` in `subscribe` event is empty.
    }
    qs = "?signature=%s&timestamp=%s&nonce=%s" % \
         mix(int(msg["time"]), str(random.random())[-10:])
    receive(msg["time"], post(settings["url"] + qs, TPL_EVENT % msg))


top = tk.Tk()
top.title("微信模拟器增强版")

text_output = st.ScrolledText(top, width=40)
text_output.pack()

text_output.tag_add("send_name", "1.0", "1.end")
text_output.tag_config("send_name", font=("Arial", "10", "bold"), justify=tk.RIGHT, rmargin=6)
text_output.tag_add("send_content", "2.0", "2.end")
text_output.tag_config("send_content", spacing3=10, justify=tk.RIGHT, rmargin=6)

text_output.tag_add("receive_name", "1.0", "1.end")
text_output.tag_config("receive_name", font=("Arial", "10", "bold"), lmargin1=2)
text_output.tag_add("receive_content", "2.0", "2.end")
text_output.tag_config("receive_content", spacing3=10, lmargin1=2)

text_input = tk.Entry(top)
text_input.pack(side=tk.LEFT)

btn_send = tk.Button(top, text="发送", command=send)
btn_send.pack(side=tk.LEFT)

btn_event = tk.Button(top, text="发送按键模拟", command=event)
btn_event.pack(side=tk.RIGHT)

btn_follow = tk.Button(top, text="关注公众帐号", command=follow)
btn_follow.pack(side=tk.RIGHT)

if __name__ == "__main__":
    top.mainloop()
