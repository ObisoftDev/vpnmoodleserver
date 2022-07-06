from mvpn import MVPN
from bs4 import BeautifulSoup
from utils import req_file_size,get_file_size,get_url_file_name,slugify,createID

import requests
import base64

def onmessage(server,message):
    try:
        text = str(message['text']).replace('<p>','').replace('</p>','')
        tokens = str(text).split('|')
        if len(tokens)>1:
           reqid = str(tokens[0]).split('-')[1]
           soup = BeautifulSoup(tokens[1],'html.parser')
           url = ''
           try:
               url = soup.find('a').next
           except:pass
           try:
               url = soup.find('img')['src']
           except:pass
           resp = requests.get(url,allow_redirects=True,stream=True)
           if resp.status_code == 200:
              file_size = req_file_size(resp)
              file_name = get_url_file_name(url,resp)
              exit = False
              server.delete_all_messages()
              respexit = False
              maxlist = 10
              for chunk in resp.iter_content(chunk_size = 1024 * 1):
                  chunkb64 = base64.b64encode(chunk).decode()
                  respsms = 'RESP-'+reqid+'|'+file_name+'|'+str(file_size)+'|'+chunkb64
                  server.send_message(respsms)
                  print('Wait for client Resp!')
                  wait = True
                  while wait:
                      list = server.get_messsages()
                      if len(list)<maxlist:break
                      else:
                          server.send_message('END RESP')
                          waittime = 100
                          time = 0
                          while time<waittime:
                               time+=1
                               list = server.get_messsages()
                               if 'END RESP LIST' in list[0]['text'] :
                                       wait = False
                                       server.delete_all_messages()
                                       break
                          if time>=waittime:
                              respexit = True
                              break
                      pass
                  if respexit:
                      print('Client Req Timeout!')
                      break
              endfileresp = 'END FILE RESP-'+reqid
              server.send_message(endfileresp)
              server.send_message(endfileresp)
                 
    except:pass
    pass

def main():
    try:
        vpn = MVPN('https://aulacened.uci.cu/','obiiii','Obysoft2001@')
        vpn.on(onmessage)
        print('MVPN SERVER RUNING!')
        vpn.run()
    except Exception as ex:
        print(str(ex))
        main()

if __name__ == '__main__':
    main()