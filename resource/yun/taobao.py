#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -*- coding:

# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib
import re
#登录地址
tbLoginUrl = "https://login.taobao.com/member/login.jhtml"
checkCodeUrl = ''
#post请求头部
headers = {
    'x-requestted-with': 'XMLHttpRequest',
    'Accept-Language': 'zh-cn',
    'Accept-Encoding': 'gzip, deflate',
    'ContentType': 'application/x-www-form-urlencoded; chartset=UTF-8',
    'Host':    'login.taobao.com',
    'DNT': 1,
    'Cache-Control': 'no-cache',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1',  
    'Referer' : 'https://login.taobao.com/member/login.jhtml?redirectURL=http%3A%2F%2Fwww.taobao.com%2F',
    'Connection' : 'Keep-Alive'
}
#用户名，密码
username = '1172585668@qq.com'
password = 'zhy@1991223'

#请求数据包
postData = {   
    'TPL_username':username, 
    'TPL_password':password, 
    "need_check_code" : "false",
    "loginsite": 0,
    "newlogin":1,
    'TPL_redirect_url':'',
    'from':'tbTop',  
    'fc':"default",   
    'style':'default',  
    'css_style':'', 
    'tid':'',
    'support':'000001', 
    'CtrlVersion':'1,0,0,7',  
    'loginType':3, 
    'minititle':'', 
    'minipara' :'', 
    "umto":"NAN",
    'pstrong':2,
    'llnick':'', 
    'sign':'',
    'need_sign':'',  
    "isIgnore":'',
    "full_redirect":'',
    'popid':'',
    'callback':'1',  
    'guf':'', 
    'not_duplite_str':'',  
    'need_user_id':'', 
    'poy':'', 
    'gvfdcname':10,
    'from_encoding':'',
    "sub":'',
    "allp":'',      
    'action':'Authenticator',   
    'event_submit_do_login':'anything',        
    'longLogin':0               
}

cookieJar = cookielib.LWPCookieJar()#LWPCookieJar提供可读写操作的cookie文件,存储cookie对象
cookieSupport= urllib2.HTTPCookieProcessor(cookieJar)
opener = urllib2.build_opener(cookieSupport, urllib2.HTTPHandler)
urllib2.install_opener(opener)

#登录主函数
def loginToTaobao():
    #cookie 自动处理器
    global checkCodeUrl
    #打开登陆页面
    taobao = urllib2.urlopen(tbLoginUrl)
    resp = taobao.read().decode("gbk")

    displayCookies(cookieJar)
    
    #提取验证码地址
    pattern = r'img id="J_StandardCode_m" src="https://s.tbcdn.cn/apps/login/static/img/blank.gif" data-src="(\S*)"'
    checkCodeUrlList = re.findall(pattern, resp)
    checkCodeUrl = checkCodeUrlList[0]
    print "checkCodeUrl:", checkCodeUrl
    #此时直接发送post数据包登录
    result = sendPostData(tbLoginUrl, postData, headers)#此时默认不需要输入验证码    
    print "result: ", result
    
    while(not result["state"]):
        print "failed to login in, error message: ",result["message"]
        if result["code"] == "3425" or result["code"] == "1000":                 
            getCheckCode(checkCodeUrl)
        result=sendPostData(tbLoginUrl, postData, headers)
        print "result: ", result

    print "successfully login in!"
    #获取st值
    url="https://passport.alipay.com/mini_apply_st.js?site=0"
    url=url+"&token="+result["token"]+"&callback=vstCallback519"
    
    text=urllib2.urlopen(url).read()
    print text
    displayCookies(cookieJar)
    st=re.search(r'"st":"(\S*)"( |})',text).group(1)
    print st
    #获取重定向地址
    myTaobaoUrl="http://login.taobao.com/member/vst.htm?"
    myTaobaoUrl=myTaobaoUrl+"st="+st+"&"+"TPL_uesrname=sunecho307"
    myTaobao = urllib2.urlopen(myTaobaoUrl)
    
    print myTaobao.read()
    displayCookies(cookieJar)

def displayCookies(cookiejar):
    print "+"*20+"displayCookies"+"+"*20
    for cookie in cookiejar:
        print cookie
   
def sendPostData(url, data, header):
    print "+"*20+"sendPostData"+"+"*20
    data = urllib.urlencode(data)      
    request = urllib2.Request(url, data, header)
    response = urllib2.urlopen(request)
    #url = response.geturl()
    text = response.read().decode("gbk")
    info = response.info()
    status = response.getcode()
    response.close()
    print status
    print info
    print "Response:", text
    result = handleResponseText(text)
    return result

def handleResponseText(text):
    """处理登录返回结果"""   
    print "+"*20+"handleResponseText"+"+"*20  
    text = text.replace(',', ' ')   
    responseData = {"state": False,
                    "message" : "",
                    "code" : "",
                    "token" : ""}
    
    m1 = re.match(r'\{?"state":(\w*)\ ', text)
    if m1 is not None:
        s = m1.group(1)
        if s == "true":
            responseData["state"] = True
            #提取token
            m4 = re.search(r'"token":"(\w*)"( |})', text)
            if m4 is not None:
               responseData["token"] = m4.group(1) 
        else:
            m2 = re.search(r'"message":"(\S*)"( |})', text)
            if m2 is not None:
                msg = m2.group(1)
                responseData["message"] = msg  
            else:
                print "failed to get the error message"
            m3 = re.match(r'.+\"code":(\w*)\ ', text)
            if m3 is not None:
                code = m3.group(1)
                responseData["code"] = code
            else:
                print "failed to get the error code"
    return responseData

def getCheckCode(url):
    print "+"*20+"getCheckCode"+"+"*20
    response = urllib2.urlopen(url)
    status = response.getcode()
    picData = response.read()
    
    path = "checkcode.jepg"
    if status == 200:
        localPic = open(path, "wb")
        localPic.write(picData)
        localPic.close() 
        print "请到%s,打开验证码图片"%path  
        checkCode = raw_input("请输入验证码：")
        print checkCode, type(checkCode)
        postData["TPL_checkcode"] = checkCode
        postData["need_check_code"] = "true"
    else:
        print "failed to get Check Code, status:",status

if __name__ == "__main__":   
    loginToTaobao()