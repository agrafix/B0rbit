# -*- coding: utf-8 -*-

'''
Created on 03.06.2011

@author: alexander
'''

import re
import xml.etree.ElementTree as ElementTree
import urllib.request, urllib.parse

class HttpLogin:
    
    def __init__(self, username, password, server):
        self.username = username
        self.password = password
        self.server = server
        
        self.userAgent = 'Mozilla/5.0 (X11; U; Linux i686; de; rv:1.9) Gecko/2008060309 Firefox/3.0'
        self.basehost = 'darkorbit.bigpoint.com'
        
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
        urllib.request.install_opener(self.opener)
        self.opener.addheaders = [('User-agent', self.userAgent)]
        
        
    def makeLogin(self):
        # Local $sLogin = _POST("darkorbit.bigpoint.com", "/?locale=de&aid=0", "loginForm_default_username=" & $sUser & "&loginForm_default_password=" & $sPass & "&loginForm_default_login_submit=Login")
        
        source = self.request("http://" + self.basehost + "/?locale=de&aid=0", {"loginForm_default_username": self.username, "loginForm_default_password": self.password, "loginForm_default_login_submit": "Login"})

        if source.find('class="instanceSelectionHeadline">') != -1:            
            result = self.regex(source, "onclick=.redirect\('http://" + self.server + "\.darkorbit\.bigpoint\.com/([^']*)'\)")
            
            return self._selectServer("http://" + self.server + ".darkorbit.bigpoint.com/" + result[0])
            
    def _selectServer(self, url):
        
        source = self.request(url)
        
        if source.find('<div class="userInfo_left') != -1:
            sidSearch = self.regex(source, "var SID='([^']*)';")
            mapSearch = self.regex(source, 'onclick="openMiniMap\(([0-9]*),([0-9]*),([0-9]*)\);"')
            
            FlashUrl = "indexInternal.es?action=internalMapRevolution&" + sidSearch[0]
            
            if mapSearch[0][2] != "0":
                FlashUrl += "&factionID=" + mapSearch[0][2]
                
            return self._loadFlash("http://" + self.server + ".darkorbit.bigpoint.com/" + FlashUrl)
                
    def _loadFlash(self, url):
        
        source = self.request(url)
        
        print(source)
        
        FlashVars = {}
        
        if source.find('FlashVars') != -1:
            flashVarsSearch = self.regex(source, "'FlashVars', '([^']*)',")
            
            Pairs = flashVarsSearch[0].split("&")
            
            for KeyValuePair in Pairs:
                Parts = KeyValuePair.split("=")
                
                if Parts[0] != "" and Parts[1]  != "":
                    FlashVars[Parts[0]] = Parts[1]
                    
            # get server ip
            xmldoc = self.request("http://" + self.server + ".darkorbit.bigpoint.com/spacemap/xml/maps.php")
            
            f = open('tmp_darkorbit.xml', 'w')
            f.write(xmldoc)
            f.close()
            
            Tree = ElementTree.parse('tmp_darkorbit.xml')
            TreeRoot = Tree.getroot()
            for Entry in TreeRoot.getchildren(): 
                if Entry.get('id') == FlashVars["mapID"]:
                    ip = Entry.find('gameserverIP').text
            
            FlashVars["serverIP"] = ip
            
        return FlashVars
        
            
    def regex(self, source, expr):
        compiled = re.compile(expr)
        result = compiled.findall(source)
        return result
        
    def request(self, url, params={}):
        
        if len(params) != 0:
            req = urllib.parse.urlencode(params).encode('utf-8')
            sock = self.opener.open(url, req)
        else:
            sock = self.opener.open(url)
            
        data = sock.read().decode('utf-8')
        sock.close()
        
        return data
