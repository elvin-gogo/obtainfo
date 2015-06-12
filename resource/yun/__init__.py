#!/usr/bin/env python
#coding:utf-8
"""
部分函数／事件说明：
OnKey,接收键盘d事件，下载文件
getTaskId，获取所有的任务id,前后两个任务id，用%连起
ShowElement 显示出各种控件元素
OnSwit 将迅雷，快车，旋风地址解密
self.addUrl,self.delUrl,self.uid,self.bdstoken,self.space ,分别是添加任务地址，删除任务地址，用户名，百度网盘的token，容量
"""
import urllib,urllib2,cookielib,re,json,wx,thread,threading,time,webbrowser,base64,sys
Time=10000
loginPost={
        'staticpage':'http://fm.baidu.com/v3Jump.html',
        'charset':'utf8',
        'token':'',
        'tpl':'fm',
        'apiver':'v3',
        'safeflg':'0',
        'u':'http://fm.baidu.com',
        'isPhone':'false',
        'quick_user':'0',
        'logintype':'basicLogin',
        'username':'',
        'password':'',
        }
delPost={
        'filelist':''
        }
addPost={
        'method':'add_task',
        'app_id':'250528',
        'source_url':'',
        'save_path':'/downloads',
        }
hds={
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
        'Referer':'http://pan.baidu.com/disk/home',
        }
loginUrl='https://passport.baidu.com/v2/api/?login'
class downFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,-1,'疯狂的离线下载(q8886888@qq.com)',size=(700,600),style=wx.CAPTION|wx.CLOSE_BOX|wx.MINIMIZE_BOX)
        self.t_getPageData=threading.Thread(target=self.getPageData)
        self.t_getPageData.start()
        self.Center()
        self.panel=wx.Panel(self,-1)
        self.Show(True)
        self.ShowElement()
        self.t_showSpace=threading.Thread(target=self.showSpace)
        self.t_showSpace.start()
        self.showDown()
    def OnKey(self,event):
        if self.spaceList.GetSelection >=0 and event.GetKeyCode()==68:threading.Thread(target=self.downFile).start()
 
    def OnDelFile(self,event):
        Id=self.spaceList.GetSelection()
        if Id >=0:
            self.SetTitle('删除中....')
            threading.Thread(target=self.delFile,args=([self.spaceItem[Id],],)).start()
    def OnDelAllFile(self,event):
        self.SetTitle('删除中....')
        if self.spaceList.GetSelection >=0:threading.Thread(target=self.delFile,args=(self.spaceItem,)).start()
    
    def delFile(self,Item):
        fileNames=[]
        for data in Item:
            fileNames.append(str(data['path']))
 
        delPost['filelist']=fileNames
        data=urllib.urlencode(delPost)
        data=data.replace('%27','%22')
        req=urllib2.Request(self.delUrl,data,hds)
        result=json.loads(urllib2.urlopen(req).read())
        print result
        if result['errno'] ==0:
            self.SetTitle('删除成功')
            threading.Thread(target=self.showSpace).start()
        else:
            self.SetTitle('删除失败')
        
 
            
    def labelData(self):
        x=5
        return(
                ('用户:',(x,10)),
                ('容量:',(x,40)),
                ('添加下载:',(x,90)),
                ('地址转换:',(x,140)),
                ('下载列表:',(x,190)),
                ('离线空间:',(x,300)),
                ('',(x+40,10)),
                ('',(x+40,40)),
                )
    def createLabel(self):
        item=[]
        for data in self.labelData():
            item.append(wx.StaticText(self.panel,-1,label=data[0],pos=data[1]))
        self.userLabel=item[-2]
        self.spaceLabel=item[-1]
        
    def ShowElement(self):
        x=80
        width=500
        self.downText=wx.TextCtrl(self.panel,-1,"",pos=(x,80),size=(width,40))
        self.switText=wx.TextCtrl(self.panel,-1,"",pos=(x,130),size=(width,40))
        self.downList=wx.ListCtrl(self,-1,style=wx.LC_REPORT,pos=(x,190),size=(width,100))
        i=0
        for data in ('任务ID','文件名','下载进度','创建时间','源链接'):
            self.downList.InsertColumn(i,data)
            i+=1
        self.downList.SetColumnWidth(1,250)
        self.downList.SetColumnWidth(4,300)
        self.downList.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnLeftClick)
        self.downList.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.OnDclick)
        self.spaceList=wx.ListBox(self.panel,-1,pos=(x,300),size=(width,250))
        self.checkText=wx.TextCtrl(self.panel,-1,"",pos=(x+150,30),size=(-1,-1))
        self.checkLabel=wx.StaticText(self.panel,-1,"请输入验证码:",pos=(x+150,10))
        self.offShow()
        self.createButton()
        self.createLabel()
        self.Bind(wx.EVT_LISTBOX_DCLICK,self.OnSpaceList,self.spaceList)
        self.spaceList.Bind(wx.EVT_KEY_UP,self.OnKey,self.spaceList)
        self.timer=wx.Timer(self,-1)
        self.Bind(wx.EVT_TIMER,self.OnTime,self.timer)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.timer.Start(Time)
        self.showInfo()
    def OnLeftClick(self,event):
        pass
 
    def OnDclick(self,event):
        self.timer.Stop()
        self.delUrl='http://pan.baidu.com/rest/2.0/services/cloud_dl?bdstoken=%s&task_id=%s&method=cancel_task&app_id=250528&channel=chunlei&clienttype=0&web=1' %(self.bdstoken,event.GetText())
        self.cancelTask()
    def cancelTask(self):
        urllib2.urlopen(self.delUrl)
        self.showDown()
        if self.downList.GetItemCount() != 0:self.timer.Start(Time)
    def OnClose(self,event):
        sys.exit()
    def OnTime(self,event):
        threading.Thread(target=self.showDown()).start()
    def showDown(self):
        DownUrl='http://pan.baidu.com/rest/2.0/services/cloud_dl?bdstoken=%s&task_ids=%s&op_type=1&method=query_task&app_id=250528&channel=chunlei&clienttype=0&web=1' %(self.bdstoken,self.getTaskId())
        try:
            page=json.loads(urllib2.urlopen(DownUrl).read())['task_info']
        except urllib2.HTTPError,e:
            if self.downList.GetItemCount()==0:
                print 'empty'
                self.timer.Stop()
                self.showSpace()
                return False
        finally:
            self.downList.DeleteAllItems()
        line=0
        try:
            for data in page:
                item=page[data]
                self.downList.InsertStringItem(line,data)
                p=float(item['finished_size'])  / (float(item['file_size'])+1)
                self.downList.SetStringItem(line,1,item['task_name'])
                self.downList.SetStringItem(line,2,format(p,"0.2%"))
                self.downList.SetStringItem(line,3,self.strTime(float(item['create_time'])))
                self.downList.SetStringItem(line,4,str(item['source_url']))
                line+=1
        except:
                self.showDown()
        try:
            if self.lastTask>line:
                threading.Thread(target=self.lastTask()).start()
        except:
            pass
        self.lastTask=line
 
    def getTaskId(self):
        page=urllib2.urlopen(self.taskIdUrl).read()
        text=json.loads(page)['task_info']
        taskId=""
        for data in text:
            taskId=taskId+','+ data['task_id']
        return urllib.quote(taskId[1:])
    def createButton(self):
        self.buttonItem=[]
        for data in self.buttonData():
            item=wx.Button(self.panel,-1,data[0],pos=data[1],size=data[2])
            self.buttonItem.append(item)
            self.Bind(wx.EVT_BUTTON,data[3],item)
        self.buttonItem[0].SetDefault()
    def buttonData(self):
        x=600
        return (
                ("添加任务",(x,80),(-1,40),self.OnAdd),
                ("转换地址",(x,130),(-1,40),self.OnSwit),
                ("刷新内容",(x,300),(-1,40),self.OnRefresh),
                ("删除文件",(x,350),(-1,40),self.OnDelFile),
                ("删除所有",(x,400),(-1,40),self.OnDelAllFile),
                )
    def OnRefresh(self,event):
        self.showSpace()
 
    def OnSwit(self,event):
        url=self.switText.GetValue().encode('utf8')
        if url.lower().startswith('thunder://'):
            url=base64.decodestring(url[10:])
            url=url[2:-2]
        elif url.lower().startswith('flashget://'):
            url=base64.decodestring(url[11:url.find('&')])
            url=url[10:-10]
        elif url.lower().startswith('qqdl://'):
            url=base64.decodestring(url[7:])
        else:
            url=""
            self.SetTitle('需要转换的地址不是迅雷,快车,旋风中的一个,请检查!')
        self.downText.Clear()
        self.downText.SetValue(url)
    def OnAdd(self,event):
        url=self.downText.GetValue().encode('utf8')
        if url:
            self.addTask(url)
        event.Skip()
    
    def onShow(self):
        self.checkText.Show(True)
        self.checkText.SetFocus()
        self.checkLabel.Show(True)
    def offShow(self):
        self.checkText.Show(False)
        self.checkLabel.Show(False)
    def addTask(self,url):
        self.timer.Stop()
        self.switText.Clear()
        if self.checkText.IsShown():addPost['input']=self.checkText.GetValue()
        addPost['source_url']=url
        addData=urllib.urlencode(addPost)
        req=urllib2.Request(self.addUrl,addData,hds)
        try:
            page=json.loads(urllib2.urlopen(req).read())
            self.offShow()
            self.SetTitle('离线任务添加成功')
            self.showDown()
        except urllib2.HTTPError,e:
            page=json.loads(e.read())
            self.SetTitle(page['error_msg'])
            if e.code==403:
                self.checkText.Clear()
                addPost['vcode']=page['vcode']
                self.getCode(page['img'])
        self.timer.Start(Time)
    def getCode(self,url):
        urllib.urlretrieve(url,'/data/_baidu.gif')
        self.showCode()
    def showCode(self):
        img=wx.Image('/data/_baidu.gif',wx.BITMAP_TYPE_ANY)
        self.checkCodeImg=wx.StaticBitmap(self.panel,-1,wx.BitmapFromImage(img),pos=(320,30))
        self.onShow()
 
    def showInfo(self):
        self.t_getPageData.join()
        self.userLabel.SetLabel(self.uid)
        self.spaceLabel.SetLabel(self.space)
    def showSpace(self):
        
        self.buttonItem[1].Enable(False)
        self.spaceList.Clear()
        page=urllib2.urlopen(self.spaceUrl).read()
        text=json.loads(page)['list']
        text.reverse()
        self.spaceItem=text
        for data in self.spaceItem:
            self.spaceList.Append(data['server_filename'] + "--size:" + str(round(float(data['size'])/1024/1024.0,2)) + "MB,time:" +time.strftime("%Y-%m-%d %T",time.localtime(data['server_mtime'])))
        self.buttonItem[1].Enable(True)
    def OnSpaceList(self,event):
        Id=self.spaceList.GetSelection()
        data=self.spaceItem[Id]
        mess='文件名:%s\n大小:%s \n时间:%s \n文件被修改时间:%s\nmd5:%s'%(data['server_filename'].encode('utf8'),str(round(float(data['size'])/1024/1024.0,2))+'MB',self.strTime(data['server_mtime']),self.strTime(data['local_mtime']),data['md5'].encode('utf8'))
        wx.MessageDialog(self.panel,mess,'文件详情',style=(wx.OK)).ShowModal()
    def downFile(self): 
        Id=self.spaceList.GetSelection()
        data=self.spaceItem[Id]
        req=urllib2.Request(data['dlink'],None,hds)
        page=urllib2.urlopen(req)
        webbrowser.open_new_tab(page.geturl())
    def strTime(self,t):
        return time.strftime("%Y-%m-%d %T",time.localtime(t))
    def getPageData(self):
        page=urllib2.urlopen('http://pan.baidu.com').read()
        re_bdstoken=re.compile(r'FileUtils\.bdstoken=\"(.+?)\"')
        re_uid=re.compile(ur'FileUtils\.sysUID=\"(.*?)\"')
        re_space=re.compile(r'<span id=\"remainingSpace\">(.+?)</div>',re.S)
        self.uid=re_uid.findall(page)[0]
        self.bdstoken=re_bdstoken.findall(page)[0]
        self.space=re_space.findall(page)[0]
        self.space=re.sub(r'</?span>','',self.space)
        self.spaceUrl="http://pan.baidu.com/api/list?channel=chunlei&clienttype=0&web=1&num=100&page=1%&dir=%2Fdownloads%2F&order=time"+"&bdstoken=%s&channel=chunlei&clienttype=0&web=1" %(str(self.bdstoken))
        self.addUrl="http://pan.baidu.com/rest/2.0/services/cloud_dl?bdstoken=%s&channel=chunlei&clienttype=0&web=1" %(str(self.bdstoken))
        self.delUrl="http://pan.baidu.com/api/filemanager?channel=chunlei&clienttype=0&web=1&opera=delete&bdstoken=%s&channel=chunlei&clienttype=0&web=1" %(str(self.bdstoken))
        self.taskIdUrl="http://pan.baidu.com/rest/2.0/services/cloud_dl?bdstoken=%s&need_task_info=1&status=1&start=0&limit=10&method=list_task&app_id=250528&channel=chunlei&clienttype=0&web=1" %(str(self.bdstoken))
        self.myLock=threading.RLock()
class loginFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,-1,'请登录你的百度',size=(350,200),style=wx.CAPTION|wx.CLOSE_BOX)
        self.Center()
        self.panel=wx.Panel(self,-1)
        userLabel=wx.StaticText(self.panel,-1,'账号: ',pos=(10,30),size=(50,-1))
        pwdLabel=wx.StaticText(self.panel,-1,'密码: ',pos=(10,60),size=(50,-1))
        self.userText=wx.TextCtrl(self.panel,-1,'',pos=(userLabel.GetSize()[0],30),size=(150,-1))
        self.pwdText=wx.TextCtrl(self.panel,-1,'',pos=(userLabel.GetSize()[0],60),size=(150,-1),style=wx.TE_PASSWORD)
        self.userText.SetFocus()
        self.checkText=wx.TextCtrl(self.panel,-1,"",pos=(240,60))
        self.checkLabel=wx.StaticText(self.panel,-1,"↑验证码↑",pos=(240,90))
        self.checkText.Show(False)
        self.checkLabel.Show(False)
        self.messLabel=wx.StaticText(self.panel,-1,"",pos=(30,150))
        self.button=wx.Button(self.panel,-1,"登录",pos=(30,120))
        self.button.SetDefault()
        self.Bind(wx.EVT_BUTTON,self.OnClick,self.button)
        self.Show(True)
        self.bd=baidu()
        self.bd.initData()
    def OnClick(self,event):
        self.bd.t.join()
        if self.checkText.IsShown():self.setCode()
        user=self.userText.GetValue().encode('utf8')
        pwd=self.pwdText.GetValue().encode('utf8')
        loginPost['username']=user
        loginPost['password']=pwd
        if self.bd.sendPost():
            self.messLabel.SetLabel("登录成功")
            self.Show(False)
            downFrame()
        else:
            self.showCode()
            self.messLabel.SetLabel("登录失败，请检查！")
            self.checkText.SetFocus()
    def showCode(self):
        if self.bd.getCode():
            img=wx.Image('/data/_baidu.gif',wx.BITMAP_TYPE_ANY)
            self.checkText.Show(True)
            self.checkLabel.Show(True)
            self.checkCodeImg=wx.StaticBitmap(self.panel,-1,wx.BitmapFromImage(img),pos=(240,20))
    def setCode(self):
        loginPost['verifycode']=self.checkText.GetValue()
class baidu():
    def initData(self):
      self.t=threading.Thread(target=self.getToken,args=('http://www.baidu.com','http://passport.baidu.com/v2/api/?getapi&tpl=fm',))
      self.t.start()
    def getToken(self,url1,url2):
        urllib2.urlopen(url1)
        re_token=re.compile('_token=\'(.+?)\'')
        token=re_token.findall(urllib2.urlopen(url2).read())[0]
        print token
        loginPost['token']=token
 
    def getCode(self):
        try:
            loginPost['codestring']=self.codeStr
            imgUrl='https://passport.baidu.com/cgi-bin/genimage?' + self.codeStr
            urllib.urlretrieve(imgUrl,'/data/_baidu.gif')
            return True
        except Exception:
            pass
            return False
    def sendPost(self):
        data=urllib.urlencode(loginPost)
        result=urllib2.Request(loginUrl,data,hds)
        text=urllib2.urlopen(result).read()
        re_codeStr=re.compile(r'codeString=(.*?)&')
        re_no=re.compile(r'err_no=(.*?)&')
        self.codeStr=re_codeStr.findall(text)[0]
        if  int(re_no.findall(text)[0])==0:
            return True
        else:
            return False
        
if __name__=='__main__':
    cj=cookielib.LWPCookieJar()
    opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj),urllib2.HTTPHandler())
    urllib2.install_opener(opener)
    mutex=threading.Lock()
    app=wx.App()
    lFrame=loginFrame()
    app.MainLoop()
