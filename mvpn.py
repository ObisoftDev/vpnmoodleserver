import requests
import json
import re
import time

from bs4 import BeautifulSoup
from random import randrange

class MVPN (object):
    def __init__(self,host='',username='',password=''):
        self.host = host
        self.username = username
        self.password = password
        self.onmessage = None
        self.runing = False
        self.proxy = None
        self.session = requests.Session()
        self.sesskey = ''
        self.convid = ''
        self.baseheaders = headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0'}

    def create_rnd_id(self,size=12):
        map = "abcdefghijklmnopqrstuvwxyz0123456789"
        id = ''
        i = 0
        while i<size:
            rnd = randrange(len(map))
            id+=map[rnd]
            i+=1
        return id

    def get_sessionkey(self):
        fileurl = self.host + 'my/#'
        resp = self.session.get(fileurl,proxies=self.proxy,headers=self.baseheaders)
        soup = BeautifulSoup(resp.text,'html.parser')
        sesskey  =  soup.find('input',attrs={'name':'sesskey'})['value']
        return sesskey

    def login(self):
        try:
            login = self.host+'login/index.php'
            resp = self.session.get(login,proxies=self.proxy,headers=self.baseheaders)
            soup = BeautifulSoup(resp.text,'html.parser')
            anchor = ''
            try:
              anchor = soup.find('input',attrs={'name':'anchor'})['value']
            except:pass
            logintoken = ''
            try:
                logintoken = soup.find('input',attrs={'name':'logintoken'})['value']
            except:pass
            username = self.username
            password = self.password
            payload = {'anchor': '', 'logintoken': logintoken,'username': username, 'password': password, 'rememberusername': 1}
            loginurl = self.host+'login/index.php'
            resp2 = self.session.post(loginurl, data=payload,proxies=self.proxy,headers=self.baseheaders)
            soup = BeautifulSoup(resp2.text,'html.parser')
            counter = 0
            for i in resp2.text.splitlines():
                if "loginerrors" in i or (0 < counter <= 3):
                    counter += 1
                    print(i)
            if counter>0:
                print('No pude iniciar sesion')
                return False
            else:
                try:
                    self.userid = soup.find('div',{'id':'nav-notification-popover-container'})['data-userid']
                except:
                    try:
                        self.userid = soup.find('a',{'title':'Enviar un mensaje'})['data-userid']
                    except:pass
                print('E iniciado sesion con exito')
                try:
                    self.sesskey  =  self.get_sessionkey()
                except:pass
                try:
                    self.convid  =  self.get_conversation_id()
                except:pass
                return True
        except Exception as ex:
            pass
        return False

    def get_conversation_id(self):
        id = ''
        conversationidurl = self.host+'lib/ajax/service.php?sesskey='+self.sesskey+'&info=core_message_get_conversations'
        jsonreq = '[{"index":0,"methodname":"core_message_get_conversations","args":{"userid":"'+self.userid+'","type":null,"limitnum":51,"limitfrom":0,"favourites":true,"mergeself":true}}]'
        jsondata = json.loads(jsonreq)
        resp = self.session.post(conversationidurl,json=jsondata,headers=self.baseheaders)
        data = json.loads(resp.text)
        id = data[0]['data']['conversations'][0]['id']
        return id

    def get_messsages(self):
        messages = []
        try:
            messagesurl = self.host+'lib/ajax/service.php?sesskey='+self.sesskey+'&info=core_message_get_conversation_messages'
            usermessagesindex = self.host+'message/index.php'
            convid = self.convid
            timeform = int(time.time())
            jsonreq = '[{"index":0,"methodname":"core_message_get_conversation_messages","args":{"currentuserid":'+self.userid+',"convid":'+str(convid)+',"newest":true,"limitnum":101,"limitfrom":1, "newest":true}}]'
            jsondata = json.loads(jsonreq)
            resp = self.session.post(messagesurl,json=jsondata,headers=self.baseheaders)
            data = json.loads(resp.text)
            messages = data[0]['data']['messages']
        except:pass
        return messages

    def delete_message(self,message):
        if message:
            delmessageurl = self.host+'lib/ajax/service.php?sesskey='+self.sesskey+'&info=core_message_delete_message'
            jsonreq = '[{"index":0,"methodname":"core_message_delete_message","args":{"messageid":"'+str(message['id'])+'","userid":'+self.userid+'}}]'
            jsondata = json.loads(jsonreq)
            resp = self.session.post(delmessageurl,json=jsondata,headers=self.baseheaders)
            data = json.loads(resp.text)
            return data
        return None

    def delete_all_messages(self):
        list = self.get_messsages()
        for m in list:
            self.delete_message(m)

    def send_message(self,text):
        sendmessageurl = self.host+'lib/ajax/service.php?sesskey='+self.sesskey+'&info=core_message_send_messages_to_conversation'
        jsonreq = '[{"index":0,"methodname":"core_message_send_messages_to_conversation","args":{"conversationid":'+str(self.convid)+',"messages":[{"text":"'+text+'"}]}}]'
        jsondata = json.loads(jsonreq)
        resp = self.session.post(sendmessageurl,json=jsondata,headers=self.baseheaders)
        data = None
        try:
            data = json.loads(resp.text)
        except:pass
        return data

    def on(self,func):self.onmessage = func

    def run(self):
        self.runing = self.login()
        if self.runing:
            self.delete_all_messages()
        while self.runing:
            try:
                list = self.get_messsages()
                for message in list:
                    if self.onmessage:
                        self.onmessage(self,message)
            except Exception as ex:
                print(str(ex))
                self.runing = self.login()


#vpn = MVPN('https://aulavirtual.uij.edu.cu/','obysoft','Obysoft2001@')
#loged = vpn.login()
#if loged:
#    filepath = vpn.download_url('https://www.7-zip.org/a/7z2107.exe')
#    print(filepath)