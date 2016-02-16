#!/usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib
import os
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.encoders import encode_base64
import email.utils
import codecs


DEBUG_MODE = False
COMMASPACE = ', '
def printDebug(strval):
  if DEBUG_MODE:
     print(strval)

class ConfigureExcep(Exception):
  def __init__(self,value):
     self.value=value
  def __str__(self):
     return repr(self.value)

def getImageName(imagepath):
  return os.path.basename(imagepath)


class SettingConfig:
  mailhost=None
  mailuser=None
  mailpassword=None
  content_type="plain"
  mailto=None
  mailport=None
  mailbodycharset="utf-8"
  subject=""
  charset="utf-8"
  mailbody=""
  imagelist=[]
  filelist=[]
  def __init__(self,configurepath):
    if os.path.isfile(configurepath)!=True:
      raise ConfigureExcep("configure file is not filepath")
    else:
      file=open(configurepath)
      for sourline in file.readlines():
        line=sourline.strip()
        parts=line.split('=')
        if len(parts)!= 2:
          continue
        else:
          if hasattr(self,parts[0]):
            if getattr(self,parts[0]) == None:
               if parts[0] == "mailto" :
                  setattr(self,parts[0],[parts[1]])
               else:
                  setattr(self,parts[0],parts[1])
            elif parts[0] == "mailto" :
               self.mailto.append(parts[1])
            elif parts[0] == "imagelist" :
               self.imagelist.append(parts[1])
            elif parts[0] == "filelist" :
               self.filelist.append(parts[1])
            else:
               setattr(self,parts[0],parts[1])
          else:
            pass
  def getmailhost(self):
    return self.mailhost
  def setmailhost(self,value):
    self.mailhost=value
  def getmailuser(self):
    return self.mailuser
  def setmailuser(self,value):
    self.mailuser=value
  def setmailto(self,value):
    self.mailto=value
  def getmailto(self):
    return self.mailto
  def setmailport(self,value):
    self.mailport=value
  def getmailport(self):
    return self.mailport
  def setpassword(self,value):
    self.mailpassword=value
  def getpassword(self):
    return self.mailpassword
  def setsubject(self,value):
    self.subject=value
  def getsubject(self):
     return self.subject
  def setcontent_type(self,value):
    self.content_type=value
  def getcontent_type(self):
    return self.content_type
  def setmailbody(self,value):
    self.mailbody=value
  def getmailbody(self):
    return self.mailbody
  def setmailbodycharset(self,value):
    self.mailbodycharset=value
  def getmailbodycharset(self):
    return self.mailbodycharset
  def setfilelist(self,value):
    self.filelist=value
  def getfilelist(self):
    return self.filelist
  def setimagelist(self,value):
    self.imagelist=value
  def getimagelist(self):
    return self.imagelist
  def setcharset(self,value):
    self.charset=value
  def getcharset(self):
    return self.charset
  property(getmailhost,setmailhost,None,"mail host")
  property(getmailuser,setmailuser,None,"mail user")
  property(getpassword,setpassword,None,"mail password")
  property(getmailport,setmailport,None,"mail port")
  property(getmailto,setmailto,None,"mail to")
  property(getsubject,setsubject,None,"mail subject")
  property(getcharset,setcharset,None,"mail charset")
  property(getmailbodycharset,setmailbodycharset,None,"mail mailbodycharset")
  property(getmailbody,setmailbody,None,"mail mailbody")
  property(getimagelist,setimagelist,None,"mail Image")
  property(getfilelist,setfilelist,None,"mail File")
  property(getcontent_type,setcontent_type,None,"content_type")

class MailClient:
  configurefile=None
  mailServer=None
  def __init__(self,configurepath):
    try:
       self.configurefile=SettingConfig(configurepath)
    except ConfigureExcep:
       print("loading configure file has failed")

  def getconfigurefile(self):
     return self.configurefile

  def setconfigurefile(self,value):
     self.configurefile=value

  def login(self):
    print("Login Mail Server Start!")
    try:
       port = int(self.configurefile.mailport)
       self.mailServer = smtplib.SMTP(self.configurefile.mailhost,port)
       self.mailServer.ehlo()
       self.mailServer.starttls()
       self.mailServer.login(self.configurefile.mailuser,self.configurefile.mailpassword)
    except:
      print("Logining mail server has failed!")
      return
    print("Login Mail Server Success!")

  def getImageName(filepath):
     parts=filepath.split(os.sep)
     if len(parts) != 0:
       return parts[-1]
     else:
       return None

  def initMailList(self):
    msg = MIMEMultipart()
    msg['From']=self.configurefile.mailuser
    if len(self.configurefile.mailto) == 1:
      msg['To'] = self.configurefile.mailto[0]
    elif len(self.configurefile.mailto) > 1:
      msg['To'] = COMMASPACE.join(self.configurefile.mailto)
    msg['Subject']=self.configurefile.subject
    # Mail Body
    body=self.readMailbody(self.configurefile.mailbody)
    mailtext=MIMEText(body,self.configurefile.content_type,self.configurefile.charset)
    msg.attach(mailtext)
    for imagefile in self.configurefile.imagelist:
      imfile=open(imagefile,"rb")
      printDebug(imagefile)
      img = MIMEImage(imfile.read())
      imagename=getImageName(imagefile)
      if imagename != None:
         img.add_header('Content-Disposition','attachment',filename=imagename)
         msg.attach(img)
      else:
         pass
      imfile.close()
    # Mail attach File
    for listpath in self.configurefile.filelist:
      ctype,encoding=mimetypes.guess_type(listpath)
      if ctype is not None or encoding is not None:
         printDebug(listpath)
         data = open(listpath, 'rb')
         ctype = 'application/octet-stream'
         maintype,subtype = ctype.split('/', 1)
         file_msg = MIMEBase(maintype, subtype)
         file_msg.set_payload(data.read())
         encode_base64(file_msg)
         # Set the filename parameter
         file_msg.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(getImageName(listpath)))
         printDebug(file_msg)
         msg.attach(file_msg)
         data.close()
    msg['Date']=email.utils.formatdate()
    return msg

  def readMailbody(self,filepath):
     try:
        content_str = ""
        for line in codecs.open(filepath, 'r', self.configurefile.mailbodycharset):
          content_str = content_str + line
        printDebug(content_str)
        return content_str
     except:
        return ""

  def sendMail(self):
     print("Send mail to Mail server!")
     self.login()
     if self.mailServer != None:
        msg=self.initMailList()
        try:
           if DEBUG_MODE:
             self.mailServer.set_debuglevel(1)
           self.mailServer.send_message(msg)
           print("Send mail Success!")
           self.mailServer.close()
        except:
           print("Send mail Failed!")
           self.mailServer.close()

if __name__ == "__main__":
   client = MailClient(".\setting.conf")
   client.sendMail()
