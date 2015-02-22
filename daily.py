#@PydevCodeAnalysisIgnore
# -*- coding: utf-8 -*-
    #@@@
    #        _                __
    #    ___(_) _____   _____| |_ ___ _ __
    #   / __| |/ _ \ \ / / __| __/ _ \ '__|
    #   \__ \ |  __/\ V /\__ \ ||  __/ |
    #   |___/_|\___| \_/ |___/\__\___|_|
    #@@@@@@ This software is property of Final Notice Recovery
    #@@@@@@ Author: Higinio Ochoa
    #@@@@@@ Version: 3.0

#Imports
import MySQLdb
import getopt
import sys
import re
import time
import mechanize
import urllib
import socket
import fcntl
import os
import lxml.html
import json
import requests
import traceback
import urllib2
import threading
import logging
from datetime import datetime
from mailer import Mailer
from datetime import datetime
from mailer import Message
from logging import handlers

#Global Constraints
dbsrvr = "localhost"                                                           #Server DB address
dbuser = "webapp"                                                              #User with privlages
dbpw = "brodyochoa12345"
wdb = "information"                                                            #Working DB
table_src = "queue"                                                    			#Source Table
#lt = time.asctime(time.localtime(time.time()))                                 #Local time
mylogfile = 'daily.log'                                                        #log name
count = 0

#Python logger 
logger = logging.getLogger('daily')
hdlr = logging.FileHandler(mylogfile)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh=logging.handlers.RotatingFileHandler(mylogfile,maxBytes=1000000,backupCount=20)
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.addHandler(fh) 
logger.setLevel(logging.DEBUG)

#compare and see if it contain date
def containDate(word):
    regexp = re.compile(r'(\d+/\d+/\d+)')
    if regexp.search(word) is not None:
        return True
    else:
        return False

#Definitions
def monkeypatch_mechanize():
 #Work-around for a mechanize 0.2.5 bug. See: https://github.com/jjlee/mechanize/pull/58
 if mechanize.__version__ < (0, 2, 6):
    from mechanize._form import SubmitControl, ScalarControl

    def __init__(self, type, name, attrs, index=None):
        ScalarControl.__init__(self, type, name, attrs, index)
        #IE5 defaults SUBMIT value to "Submit Query"; Firebird 0.6 leaves it"""
        #blank, Konqueror 3.1 defaults to "Submit".  HTML spec. doesn't seem"""
        #to define this."""

        if self.value is None:
           if self.disabled:
            self.disabled = False
            self.value = ""
            self.disabled = True
        else:
            self.value = ""
            self.readonly = True

            SubmitControl.__init__ = __init__


def sendnotice (vin,data,who,where,theplate):
        try:
            #  Sends an email to the appropriate account after updating DB"""
            #  accnt = account number"""
            #  vin = Vinnumber"""
            #  data = the found data"""
            #  who = who to email"""
            #  where = Searchengine where found"""
             whom = who
             if where == 'mdcourt':
                whereat = '<a href="http://casesearch.courts.state.md.us/inquiry/inquiry-index.jsp">MD Judiciary Case Search</a>'
             elif where == 'mdcityservices':
                whereat = '<a href="http://cityservices.baltimorecity.gov/parkingfines/default.aspx">Baltimore Parking, Red Light and Speed Camera Citations</a>'
             elif where == 'dcdmvmd':
                whereat = '<a href="https://prodpci.etimspayments.com/pbw/include/dc_parking/input.jsp?ticketType=P">MD Online Ticket Pay</a>'
             elif where == 'dcdmvdc':
                whereat = '<a href="https://prodpci.etimspayments.com/pbw/include/dc_parking/input.jsp?ticketType=P">DC OnlineTicket Pay</a>'
             elif where == 'autreturn':
               whereat = '<a href="http://www.Autoreturn.com">Autoreturn.com Lookup</a>'
             elif where == 'baltimoreimpound':
               whereat = '<a href="www.baltimorecitytowing.net ">Baltimore City Towing</a>'
             elif where == 'princeg':
               whereat = '<a href="http://towinquiry.princegeorgescountymd.gov/towinquiry.aspx">Prince Georges County</a>'
             elif where == 'bge':
               whereat = '<a href="https://secure.bge.com">BGE Outage Report</a>'
             else:
                whereat = '<a href="http://10digits.us">10digit Perssonal Lookup</a>'
            
             message = Message(From="donotreply@alexissecuritysolutions.com",To='swilbanks@greycoatlabs.com, jitu3@yahoo.com')
             message.Subject = "New HIT on Sievster!"
             message.Html = """<p><b>Sievster Report on Plate# %s Vin# %s</b><br>
                            <b><i>Search Engine:%s</b></i><br>
                            <i>New Data Found:</i><br>
                            %s</p>""" % (theplate,vin,whereat,data)
            
             sender = Mailer('localhost')
             sender.send(message)
        except Exception as e:
            logger.error("There was error inside the sendnotice method "+str(e))
            logger.error('Information are vin -> %s, data -> %s, who -> %s, where -> %s, theplate -> %s', vin, data, who, where, theplate)
        return



def addhotlist(data,sengine,vin,email,theplate):
     """Adds data to DB on HIT"""
     """ Data = data to add/update"""
     """ seng = website polled"""
     """ vin = VIN"""
     """ notify = email to send notice of hit to """
     try:
             dbtble = "queue"
             db1 = MySQLdb.connect(dbsrvr,dbuser,dbpw, wdb )
             cursor1 = db1.cursor()
             
             olddata =""
            
             if sengine == "mdcourt":
                #datas = '%' + data + '%'
                cursor1.execute ("SELECT * FROM queue WHERE  mdcourt = %s and vin = %s", (data, vin))
                
                results = cursor1.fetchone()
                if results != None:
                    olddata = results[19]
                else:
                    olddata = "nothing"
            
                if olddata != data:
                    #mdcourt = data
                    cursor1.execute ("UPDATE queue SET mdcourt=%s WHERE vin = %s ",(data,vin))
                    db1.commit()
                    sendnotice(vin,mdcourt,email,sengine,theplate)

            
             elif sengine == "mdcityservices":
                #datas = '%' + data + '%'
                cursor1.execute ("SELECT * FROM queue WHERE  mdcityservices = %s and vin = %s", (data, vin))
                
                results = cursor1.fetchone()
                if results != None:
                    olddata = results[20]
                else:
                    olddata = "nothing"
            
                if olddata != data:
                    #mdcityservices = data
                    cursor1.execute ("UPDATE queue SET mdcityservices=%s WHERE vin = %s",(data,vin))
                    db1.commit()
                    sendnotice(vin,mdcityservices,email,sengine,theplate)
            
             elif sengine == "dcdmvmd":
                #datas = '%' + data + '%'
                cursor1.execute ("SELECT * FROM queue WHERE  dcdmvmd = %s and vin = %s", (data, vin))
                #db.commit()
                results = cursor1.fetchone()
                if results != None:
                    olddata = results[21]
                else:
                    olddata = "nothing"
            
                if olddata != data:
                    #dcdmvmd = data
                    cursor1.execute ("UPDATE queue SET dcdmvmd=%s WHERE vin = %s ",(data,vin))
                    db1.commit()
                    sendnotice(vin,dcdmvmd,email,sengine,theplate)
            
             elif sengine == "dcdmvdc":
                #datas = '%' + data + '%'
                cursor1.execute ("SELECT * FROM queue WHERE dcdmvdc = %s and vin = %s", (data, vin))
                #db.commit()
                results = cursor1.fetchone()
                if results != None:
                    olddata = results[22]
                else:
                    olddata = "nothing"
            
                if olddata != data:
                    #dcdmvdc = data
                    cursor1.execute ("UPDATE queue SET dcdmvdc=%s WHERE vin = %s",(data,vin))
                    db1.commit()
                    sendnotice(vin,dcdmvdc,email,sengine,theplate)
            
             elif sengine == "autreturn":
                #datas = '%' + data + '%'
                cursor1.execute ("SELECT * FROM queue WHERE  autreturn = %s and vin = %s", (data, vin))
                #db.commit()
                results = cursor1.fetchone()
                if results != None:
                    olddata = results[23]
                else:
                    olddata = "nothing"
            
                if olddata != data:
                    #autreturn = data
                    cursor1.execute ("UPDATE queue SET autreturn=%s WHERE vin = %s",(data,vin))
                    db1.commit()
                    sendnotice(vin,autreturn,email,sengine,theplate)
            
             elif sengine == "bge":
                #datas = '%' + data + '%' 
                cursor1.execute ("SELECT * FROM queue WHERE  bge = %s and vin = %s", (data, vin))
                
                #db.commit()
                results = cursor1.fetchone()
                if results != None:
                    olddata = results[25]
                else:
                    olddata = "nothing"
                
                if olddata != data:
                    logger.info('')
                    logger.info('OLD DATA IS --> :'+olddata)
                    logger.info('NEW DATA IS --> :'+data)
                    logger.info('you should get this email of new data of previous')
                    #bge = data
                    cursor1.execute ("UPDATE queue SET bge=%s WHERE vin = %s",(data,vin))
                    db1.commit()
                    sendnotice(vin,bge,email,sengine,theplate)
            
             elif sengine =="baltimoreimpound":
                #datas = '%' + data + '%'
                cursor1.execute ("SELECT * FROM queue WHERE  baltimoreimpound = %s and vin = %s", (data, vin))
                #db.commit()
                results = cursor1.fetchone()
                if results != None:
                    olddata = results[26]
                else:
                    olddata = "nothing"
            
                if olddata != data:
                    #baltimoreimpound = data
                    cursor1.execute ("UPDATE queue SET baltimoreimpound=%s WHERE vin = %s",(data,vin))
                    db1.commit()
                    sendnotice(vin,baltimoreimpound,email,sengine,theplate)
            
             elif sengine =="princeg":
                #datas = '%' + data + '%'
                cursor1.execute ("SELECT * FROM queue WHERE  princeg = %s and vin = %s", (data, vin))
                #db.commit()
                results = cursor1.fetchone()
                if results != None:
                    olddata = results[27]
                else:
                    olddata = "nothing"
            
                if olddata != data:
                    #princeg = data
                    cursor1.execute ("UPDATE queue SET princeg=%s WHERE vin = %s",(data,vin))
                    db1.commit()
                    sendnotice(vin,princeg,email,sengine,theplate)
            
             else:
                #datas = '%' + data + '%'
                cursor1.execute ("SELECT * FROM information.queue WHERE  tendigit = %s and vin = %s", (data, vin))
                #db.commit()
                results = cursor1.fetchone()
                if results != None:
                    olddata = results[24]
                else:
                    olddata = "nothing"
            
                if olddata != data:
                    #tendigit = data
                    cursor1.execute ("UPDATE queue SET tendigit=%s WHERE vin = %s",(data,vin))
                    db1.commit()
                    sendnotice(vin,tendigit,email,sengine,theplate)
					
     except Exception as e:
            logger.error("There was error inside the addhotlist method "+str(e))
            logger.error('Information are data -> %s, seng -> %s, vin -> %s, notify -> %s, theplate -> %s', data,seng,vin,notify,theplate)
            cursor1.close()
            db1.close()

     cursor1.close()
     db1.close()
     results = None

     return



def region2(lname,fname,car_tag_full,vin,notify,phnumber):
    """Region 2 Search DB"""
    fandm = firname = fname.split(' ')
    cartag = car_tag_full.strip()

    if len(fandm) < 2:
        firname = fandm[0]
        midname = "None"
    else:
        firname = fandm[0]
        midname = fandm[1]

    if len(cartag) != 0:
        theplate = cartag
    else:
        theplate = 'NotAvail'

    if len(phnumber) != 0:
        t1 = threading.Thread(target=baltimoreimpound, args= (vin,notify,theplate))
        t1.start()

        t2 = threading.Thread(target=pgeorge, args= (vin,notify,theplate))
        t2.start()

        t3 = threading.Thread(target=dcdmvDC, args= (theplate,vin,notify))
        t3.start()

        t4 = threading.Thread(target=mdcourt, args= (firname,midname,lname,vin,notify,theplate))
        t4.start()

        t5 = threading.Thread(target=dcdmvMD, args= (theplate,vin,notify))
        t5.start()

        t6 = threading.Thread(target=autoreturn, args= (vin,notify,theplate))
        t6.start()

        t7 = threading.Thread(target=bge, args= (phnumber,vin,notify,theplate))
        t7.start()

        t8 = threading.Thread(target=mdcityservices, args= (theplate,vin,notify))
        t8.start()
        
        t1.join()
        t2.join()
        t3.join()
        t4.join()
        t5.join()
        t6.join()
        t7.join()
        t8.join()

        return



def baltimoreimpound (vin,notify,theplate):
    try:
        br = mechanize.Browser(mechanize.RobustFactory())
        br.set_handle_robots(False)
        br.set_handle_refresh(False)
        br.addheaders = [('User-Agent', 'Mozilla/5.0 (Linux; U; Android 2.3.4; en-us; T-Mobile myTouch 3G Slide Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'),
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
        ('Accept-Language', 'en-gb,en;q=0.5'),
        ('Accept-Encoding', 'gzip,deflate'),
        ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
        ('Keep-Alive', '115'),
        ('Connection', 'keep-alive'),
        ('Cache-Control', 'max-age=0')]
        
        """Baltimore Impound Search"""
        seng = "baltimoreimpound"
        res = br.open('http://edtweb24dev253.edthosting.com/IVIC_WebSearch/IVICWebFindVehicle.aspx')
        resp = br.response().read()
        br.form = list(br.forms())[0]
        last6 = vin[-6:]
        br.form['MD_Tags_YN'] = ['MD_Yes']
        br.form['VIN_Num'] = last6
        resp = br.submit(name='ImageButton2').read()
        tree = lxml.html.fromstring(resp)
        a = tree.xpath('//*[@id="Prop_Number"]/b/font')
        b = tree.xpath('//*[@id="Impound_Lot"]/font')
        c = tree.xpath('//*[@id="Received"]/font')
        d = tree.xpath('//*[@id="License_Tag"]/font')
        e = tree.xpath('//*[@id="State"]/font')
        f = tree.xpath('//*[@id="VIN"]/font')
        g = tree.xpath('//*[@id="Description"]/font')
        h = tree.xpath('//*[@id="Property_Type"]/font')
        i = tree.xpath('//*[@id="Release_Data"]/font')
    
        if len(a) == 0:
            br.close
        else:
            curdate = str(time.strftime("%m/%d/%Y"))
            rec = c[0].text
            sentence = rec.split(" ")
            tom = sentence[0]
            start_date = datetime.strptime(curdate, "%m/%d/%Y")
            end_date = datetime.strptime(tom, "%m/%d/%Y")
            since = abs((end_date-start_date).days)
            if since <= 14:
                propnnumber = a[0].text
                lot = b[0].text
                lic = d[0].text
                st = e[0].text
                thevin = f[0].text
                descr = g[0].text
                type = h[0].text
                release_data = i[0].text
                data = "Recvd:" + rec + " Property#" + propnnumber + " Vin:" + thevin  +" Plate:" + lic + " Lot:"+lot
                addhotlist(data,seng,vin,notify,theplate);
    except Exception as e:
        logger.error("There was error inside the baltimoreimpound method "+str(e))
        logger.error('Information are vin -> %s, notify -> %s, theplate -> %s', vin,notify,theplate)
    return



def pgeorge (vin,notify,theplate):
    try:
        br = mechanize.Browser(mechanize.RobustFactory())
        br.set_handle_robots(False)
        br.set_handle_refresh(False)
        br.addheaders = [('User-Agent', 'Mozilla/5.0 (Linux; U; Android 2.3.4; en-us; T-Mobile myTouch 3G Slide Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'),
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
        ('Accept-Language', 'en-gb,en;q=0.5'),
        ('Accept-Encoding', 'gzip,deflate'),
        ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
        ('Keep-Alive', '115'),
        ('Connection', 'keep-alive'),
        ('Cache-Control', 'max-age=0')]
        
        seng = "princeg"
        thevin = vin
        response = br.open("http://towinquiry.princegeorgescountymd.gov/towinquiry.aspx")
        br.select_form("Form1")
        br.form['vin'] = thevin
        response = br.submit()
        resp = response.read()
        tree = lxml.html.fromstring(resp)
        a = tree.xpath('//*[@id="lblvin"]')   #vin
        b = tree.xpath('//*[@id="lbllicnum"]') # plate
        c = tree.xpath('//*[@id="lblimpdt"]') # impound date format 01/03/2015 %m/%d/%Y
        d = tree.xpath('//*[@id="lblimptm"]') #impound time
        e = tree.xpath('//*[@id="lblreldt"]') #Release Date
    
        if len(a) == 0:
            br.close
        else:
            curdate = str(time.strftime("%m/%d/%Y"))
            impounddate = c[0].text
            releasedate = e[0].text
            plate = b[0].text
            start_date = datetime.strptime(curdate, "%m/%d/%Y")
            end_date = datetime.strptime(impounddate, "%m/%d/%Y")
            since = abs((end_date-start_date).days)
            if releasedate == None:
                releasedate = " Still in custody"
            else:
                releasedate = e[0].text
    
                if plate == None:
                    plate = "No Plate "
                else:
                    plate = b[0].text
    
                    if since <= 14:
                        thevin = a[0].text
                        impounddate = c[0].text
                        impoundtime = d[0].text
                        data = thevin + plate + impounddate + releasedate
                        addhotlist(data,seng,vin,notify,theplate);
    except Exception as e:
            logger.error("There was error inside the pgeorge method "+str(e))
            logger.error('Information are vin -> %s, notify -> %s, theplate -> %s', vin,notify,theplate)
    return



def bge(phnum,vin,notify,theplate):
    try:
         """BGE Search"""
         seng = "bge"
         address = []
         
         while '' in phnum:
            phnum.remove('')
        
         for numbers in phnum:
            if len(numbers) != 0:
                url = "https://secure.bge.com/_layouts/Bge.Canp/AnonymousService.asmx/GetCustomerDataOutage"
                data = {
                    "captchaAns":"null",
                    "captchaEncCode":"null",
                    "accountNumber":""
                }
                data['phoneNumber'] = numbers
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                r = requests.post(url, data=json.dumps(data), headers=headers)
        
                binary = r.content
                output = json.loads(binary)
        
                for eachoutput in output['d']['OutageData']:
                    address.append(str(eachoutput['FullAddress']))
        
        
         if len(address) !=0:
            data = "<br>".join(map(str, address))
            data.rstrip(os.linesep)
            addhotlist(data,seng,vin,notify,theplate)
            
            data = None
          
            address = []
            
    except Exception as e:
            logger.error("There was error inside the bge method "+str(e))
            logger.error('Information are phnumber -> %s, vin -> %s, notify -> %s, theplate -> %s', phnumber,vin,notify,theplate)
    return




def tendigit(firname,midname,lname,vin,notify,theplate):
    try:
         br = mechanize.Browser(mechanize.RobustFactory())
         br.set_handle_robots(False)
         br.set_handle_refresh(False)
         br.addheaders = [('User-Agent', 'Mozilla/5.0 (Linux; U; Android 2.3.4; en-us; T-Mobile myTouch 3G Slide Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'),
         ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
         ('Accept-Language', 'en-gb,en;q=0.5'),
         ('Accept-Encoding', 'gzip,deflate'),
         ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
         ('Keep-Alive', '115'),
         ('Connection', 'keep-alive'),
         ('Cache-Control', 'max-age=0')]
         
         
         seng = "tendigit"
         name = firname + " " + lname
         fixed = name.replace (" ", "_")
         location = 'MD'
         payload = 'http://10digits.us/n/'+fixed+'/location/'+location
         data = urllib.urlopen(payload)
         resp = data.read()
         tree = lxml.html.fromstring(resp)
         ne = tree.xpath('/html/body/div/div[2]/ul/li/ul/li[1]/a')
         nr = tree.xpath('/html/body/div/div[2]/ul/li/ul/li[2]/span/span[1]')
         st = tree.xpath('/html/body/div/div[2]/ul/li/ul/li[2]/span/span[3]')
         cty = tree.xpath('/html/body/div/div[2]/ul/li/ul/li[4]/span/span[1]')
         sat = tree.xpath('/html/body/div/div[2]/ul/li/ul/li[4]/span/span[3]')
         ph = tree.xpath('/html/body/div/div[2]/ul/li/ul/li[5]')
         if len(ne) == 0:
            br.close
         else:
            name = ne[0].text
            st_address = nr[0].text + " " + st[0].text + " " + cty[0].text
            phone = ph[0].text
            if len(ph[0]) <> 0:
              data = name + " " + st_address + " " + phone
            else:
              data = name + " " + st_address
              br.close
              addhotlist(data,seng,vin,notify,theplate);
    except Exception as e:
            logger.error("There was error inside the tendigit method "+str(e))
            logger.error('Information are firname -> %s, midname -> %s, lname -> %s, vin -> %s, notify -> %s, theplate -> %s', firname,midname,lname,vin,notify,theplate)
    return




def autoreturn (vin,notify,theplate):
    try:
         br = mechanize.Browser(mechanize.RobustFactory())
         br.set_handle_robots(False)
         br.set_handle_refresh(False)
         br.addheaders = [('User-Agent', 'Mozilla/5.0 (Linux; U; Android 2.3.4; en-us; T-Mobile myTouch 3G Slide Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'),
         ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
         ('Accept-Language', 'en-gb,en;q=0.5'),
         ('Accept-Encoding', 'gzip,deflate'),
         ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
         ('Keep-Alive', '115'),
         ('Connection', 'keep-alive'),
         ('Cache-Control', 'max-age=0')]
            
         """Autoreturn Search"""
         seng = "autreturn"
         info=[]
         thevin = vin
         payload = urllib.urlencode({'license':'','licenseState':'','vin': thevin,'towDate':'','make':'','model':'','vehicleYear':'','color':''})
         br.open('http://www.autoreturn.com/baltimore-county-md/find-vehicle/results',payload)
         resp = br.response().read()
         tree = lxml.html.fromstring(resp)
         all_list = tree.xpath('//table/tr/td')
        
         if (len(all_list) == 0):
           br.close
         else:
            br.form = list(br.forms())[0]
            control = br.form.controls[0]
            value = control.value
            id = " ".join(map(str, value))
            urpayload = "http://www.autoreturn.com/baltimore-county-md/find-vehicle/details?vehicle=%s" % id
            br.open(urpayload)
            resp = br.response().read()
            tree = lxml.html.fromstring(resp)
            all_list = tree.xpath('//table/tr/td[2]')
            curdate = str(time.strftime("%m/%d/%y"))
            towtime = all_list[4].text.strip().replace(u'\xa0', u' ')
            sentence = towtime.split(" ")
            tom = sentence[0]
            start_date = datetime.strptime(curdate, "%m/%d/%y")
            end_date = datetime.strptime(tom, "%m/%d/%y")
            since = abs((end_date-start_date).days)
        
            if since <= 14:
               trnum = all_list[0].text.strip()
               licenses = all_list[1].text.strip()
               thevin = all_list[2].text.strip()
               vehicle = all_list[3].text.strip()
               towtime = all_list[4].text.strip()
               status = all_list[8].text.strip()
               company = all_list[9].text.strip()
               info.append("TR Number:" + tom)
               info.append("Vehicle:" + vehicle)
               info.append("Status:" + status)
               info.append("Plate:" + licenses)
               info.append("Tow Company:" + company)
               data = '<br>'.join(info)
               addhotlist(data,seng,vin,notify,theplate);
               br.close
    except Exception as e:
            logger.error("There was error inside the autoreturn method "+str(e))
            logger.error('Information are vin -> %s, notify -> %s, theplate -> %s', vin,notify,theplate)
    return




def dcdmvDC (theplate,vin,notify):
    try:
         br = mechanize.Browser(mechanize.RobustFactory())
         br.set_handle_robots(False)
         br.set_handle_refresh(False)
         br.addheaders = [('User-Agent', 'Mozilla/5.0 (Linux; U; Android 2.3.4; en-us; T-Mobile myTouch 3G Slide Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'),
         ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
         ('Accept-Language', 'en-gb,en;q=0.5'),
         ('Accept-Encoding', 'gzip,deflate'),
         ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
         ('Keep-Alive', '115'),
         ('Connection', 'keep-alive'),
         ('Cache-Control', 'max-age=0')]   
         
         """DC DMV - DC Search"""
         seng = "dcdmvmd"
         res = br.open('https://prodpci.etimspayments.com/pbw/include/dc_parking/input.jsp?ticketType=P')
         resp = br.response().read()
         br.form = list(br.forms())[0]
         br.form['statePlate'] = ['DC']
         br.form['plateNumber'] = theplate
         resp = br.submit(name='submit').read()
         tree = lxml.html.fromstring(resp)
         data = list()
         data2 = []
         
         if len(tree) > 2:
            table, = tree.xpath('//*[.="Violation"]/ancestor::table[1]')
            tree1 =  lxml.html.tostring(table)
            tree2 = lxml.html.fromstring(tree1)
            rows = tree2.xpath('//table/tr')
            flagger = False
        
            for row in rows:
                    data.append([c.text for c in row.getchildren()])
            
            #print data[1][1]
            if data[1][1] != None and data[1][1].strip() == 'You must pay all of the following boot eligible tickets to retrieve your vehicle.':
                flagger = True
                start_zone = 3
            else:
                start_zone = 1
            
            for i in range(start_zone,len(data)-1):
                ticket_number = ''
                issue_date = ''
                violation = ''
                location = ''
                
                if flagger == True:
                    if data[i][2] != None and containDate(data[i][2]):
                        #print data[i][2]
                        issue_date = data[i][2]
                        violation = data[i][3]
                        ticket_number = data[i][1]
                        location = data[i][4]
                    else:
                        continue
                else:
                    if data[i][1] != None and containDate(data[i][1]):
                        #print data[i][1]
                        issue_date = data[i][1]
                        violation = data[i][2]
                        location = data[i][3]
                        ticket_number = data[i][0]
                    else:
                        continue
                    
                if len(issue_date) != 0:
                    curdate = str(time.strftime("%m/%d/%Y"))
                    start_date = datetime.strptime(curdate, "%m/%d/%Y")
                    end_date = datetime.strptime(issue_date, "%m/%d/%Y")
                    since = abs((end_date-start_date).days)
        
                    if since <= 14:
                        data2.append ("Ticket#: %s Issue Date: %s Violation: %s Location: %s" % (ticket_number,issue_date,violation,location))
                        
            if len(data2) != 0:
                data = "<br>".join(map(str, data2))
                data.rstrip(os.linesep)
                addhotlist(data,seng,vin,notify,theplate);
                br.close
                        
         else:
            return
        
         
    except Exception as e:
            logger.error("There was error inside the dcdmvDC method "+str(e))
            logger.error('Information are theplate -> %s, vin -> %s, notify -> %s', theplate,vin,notify)
    return


def dcdmvMD (theplate,vin,notify):
    try:
         br = mechanize.Browser(mechanize.RobustFactory())
         br.set_handle_robots(False)
         br.set_handle_refresh(False)
         br.addheaders = [('User-Agent', 'Mozilla/5.0 (Linux; U; Android 2.3.4; en-us; T-Mobile myTouch 3G Slide Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'),
         ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
         ('Accept-Language', 'en-gb,en;q=0.5'),
         ('Accept-Encoding', 'gzip,deflate'),
         ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
         ('Keep-Alive', '115'),
         ('Connection', 'keep-alive'),
         ('Cache-Control', 'max-age=0')]   
         
         """DC DMV - MDC Search"""
         seng = "dcdmvmd"
         res = br.open('https://prodpci.etimspayments.com/pbw/include/dc_parking/input.jsp?ticketType=P')
         resp = br.response().read()
         br.form = list(br.forms())[0]
         br.form['statePlate'] = ['MD']
         br.form['plateNumber'] = theplate
         resp = br.submit(name='submit').read()
         tree = lxml.html.fromstring(resp)
         data = list()
         data2 = []
         
         if len(tree) > 2:
            table, = tree.xpath('//*[.="Violation"]/ancestor::table[1]')
            tree1 =  lxml.html.tostring(table)
            tree2 = lxml.html.fromstring(tree1)
            rows = tree2.xpath('//table/tr')
        
        
            for row in rows:
                data.append([c.text for c in row.getchildren()])
        
        
            for i in range(1,len(data)-1):
                issue_date = data[1][1]
        
                if len(issue_date) != 0:
                    curdate = str(time.strftime("%m/%d/%Y"))
                    start_date = datetime.strptime(curdate, "%m/%d/%Y")
                    end_date = datetime.strptime(issue_date, "%m/%d/%Y")
                    since = abs((end_date-start_date).days)
        
                    if since <= 14:
                        data2.append ("Ticket#: %s Issue Date: %s Violation: %s Location: %s" % (data[i][0],data[i][1],data[i][2],data[i][3]))
                        
            if len(data2) != 0:
                data = "<br>".join(map(str, data2))
                data.rstrip(os.linesep)
                addhotlist(data,seng,vin,notify,theplate);
                br.close
                        
         else:
            return
        
         
    except Exception as e:
            logger.error("There was error inside the dcdmvMD method "+str(e))
            logger.error('Information are theplate -> %s, vin -> %s, notify -> %s', theplate,vin,notify)
    return


def montgom(theplate,vin,notify):
    try:
        pass
    except Exception as e:
            logger.error("There was error inside the montgom method "+str(e))
            logger.error('Information are theplate -> %s, vin -> %s, notify -> %s', theplate,vin,notify)

    return



def mdcityservices (theplate,vin,notify):
    try:   
         br = mechanize.Browser(mechanize.RobustFactory())
         br.set_handle_robots(False)
         br.set_handle_refresh(False)
         br.addheaders = [('User-Agent', 'Mozilla/5.0 (Linux; U; Android 2.3.4; en-us; T-Mobile myTouch 3G Slide Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'),
         ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
         ('Accept-Language', 'en-gb,en;q=0.5'),
         ('Accept-Encoding', 'gzip,deflate'),
         ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
         ('Keep-Alive', '115'),
         ('Connection', 'keep-alive'),
         ('Cache-Control', 'max-age=0')]   
            
         """MD City Services Search"""
         seng = "mdcityservices"
         res = br.open('http://cityservices.baltimorecity.gov/parkingfines/default.aspx')
         resp = br.response().read()
         br.form = list(br.forms())[0]
         lookup = theplate
         br.form['ctl00$ctl00$rootMasterContent$LocalContentPlaceHolder$txtBoxTag'] = lookup
         resp = br.submit(name='ctl00$ctl00$rootMasterContent$LocalContentPlaceHolder$btnSearch').read()
         tree = lxml.html.fromstring(resp)
         table = tree.xpath("//*[@id='ctl00_ctl00_rootMasterContent_LocalContentPlaceHolder_gvParkingFines']")
         data = list()
         data2 = []
         if len(table) > 0:
            rows = table[0].xpath('./tr')
        
            for row in rows:
                data.append([c.text for c in row.getchildren()])
        
            for i in range(1,len(data)-1):
                data2.append ("%s %s %s" % (data[i][0],data[i][2],data[i][7]))
        
         if len(data2) != 0:
            dataold = data2
            data = "<br>".join(map(str, dataold))
            data.rstrip(os.linesep)
            addhotlist(data,seng,vin,notify,theplate);
            br.close
            
    except Exception as e:
            logger.error("There was error inside the mdcityservices method "+str(e))
            logger.error('Information are theplate -> %s, vin -> %s, notify -> %s', theplate,vin,notify)
    return




def mdcourt (firname,midname,lname,vin,notify,theplate):
    try:   
         br = mechanize.Browser(mechanize.RobustFactory())
         br.set_handle_robots(False)
         br.set_handle_refresh(False)
         br.addheaders = [('User-Agent', 'Mozilla/5.0 (Linux; U; Android 2.3.4; en-us; T-Mobile myTouch 3G Slide Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'),
         ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
         ('Accept-Language', 'en-gb,en;q=0.5'),
         ('Accept-Encoding', 'gzip,deflate'),
         ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
         ('Keep-Alive', '115'),
         ('Connection', 'keep-alive'),
         ('Cache-Control', 'max-age=0')]   
             
         """MD Court Search"""
         seng = "mdcourt"
         res = br.open('http://casesearch.courts.state.md.us/inquiry/inquiry-index.jsp')
         br.form = list(br.forms())[0]
         br.form['disclaimer'] = ['Y']
         r = br.submit()
        
         br.form = list(br.forms())[2]
         br.form['lastName'] = lname.upper()
         br.form['firstName'] = firname.upper()
         if midname != 'None':
            br.form['middleName'] = midname.upper()
         br.form['exactMatchLn'] = ['Y']
         r = br.submit()
         tree = lxml.html.fromstring(r.read())
         data = list()
         data2 = list()
         # it fetch me table body (tbody eliminate the table header)
         if (tree.xpath('//*[@id="row"]/tbody')):
            table = tree.xpath('//*[@id="row"]/tbody')[0]
        
            eachline = ''
            breaker = ' <br> '
            seperator = ' | ' # seperator in between data for each row
        
            for row in table.xpath('./tr'):
                if eachline != '':
                    eachline = eachline + breaker
                    data.append(eachline)
        
                eachline = '' #reset me back to original
        
            # first data is under ./td/a/text() and rest of them is under ./td/text()' so I wrote the or condition here
                for column in row.xpath('./td/a/text() | ./td/text()'):
                    if column.strip() != '':
                        if eachline != '':
                            eachline = eachline + seperator + column.strip()
                        else:
                            eachline = eachline + column.strip()
        
        
                for eachoutput in data:
                #print eachoutput
                    stri = eachoutput
                    matched = re.search(r'\d{2}/\d{2}/\d{4}', stri)
                    if (matched):
                        curdate = str(time.strftime("%m/%d/%Y"))
                        start_date = datetime.strptime(curdate, "%m/%d/%Y").date()
                        end_date = datetime.strptime(matched.group(0), "%m/%d/%Y").date()
                        since = abs((end_date-start_date).days)
                        if since <= 14:
                            data2.append(stri)
        
        
         if len(data2) != 0:
            dataold = data2
            data3 = "".join(map(str, dataold))
            addhotlist(data3,seng,vin,notify,theplate);
    except Exception as e:
            logger.error("There was error inside the mdcityservices method "+str(e))
            logger.error('Information are firstname -> %s, midname -> %s, lname -> %s, vin -> %s, notify -> %s, theplate -> %s', firname,midname,lname,vin,notify,theplate)

    return



"""Main Code Loop"""
start_time = time.clock()
try:
 pid_file = 'daily.pid'                                                         #Place lock
 fp = open(pid_file, 'w')
 fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError:
    lt = time.asctime(time.localtime(time.time()))                              #Another Instance is running so we exit.
    logger.info('daily.pid found, Quiting')
    sys.exit(0)

logger.info('Time started is %s', str(datetime.now()))

db = MySQLdb.connect(dbsrvr,dbuser,dbpw, wdb )
cursor = db.cursor()
sqlall = "SELECT * FROM %s" % table_src                                        #Get ALL accounts in the database
cursor.execute(sqlall)
results = cursor.fetchall()
rows=len(results)
if rows == 0:                                                                  #Ensure DB is not empty
    logger.info('Database empty, Quiting')
    sys.exit(0)
else:
    #lt = time.asctime(time.localtime(time.time()))
    logger.info('Database Operation Started')
for row in results:
    try:
        phnumber = []
        case_number = db.escape_string(str(row[1]))
        lname = db.escape_string(str(row[2]))
        fname = db.escape_string(str(row[3]))
        mname = db.escape_string(str(row[4]))
        colast = db.escape_string(str(row[5]))
        cofirst = db.escape_string(str(row[6]))
        vin = db.escape_string(str(row[7]))
        tag_number = db.escape_string(str(row[8]))
        tag_st = db.escape_string(str(row[9]))
        homephone = db.escape_string(str(row[10]))
        phnumber.append(str(homephone))
        workphone = db.escape_string(str(row[11]))
        phnumber.append(str(workphone))
        cellphone = db.escape_string(str(row[12]))
        phnumber.append(str(cellphone))
        cohome = db.escape_string(str(row[13]))
        phnumber.append(str(cohome))
        cowork = db.escape_string(str(row[14]))
        phnumber.append(str(cowork))
        cocell = db.escape_string(str(row[15]))
        phnumber.append(str(cocell))
        notify = db.escape_string(str(row[16]))
        date_added = db.escape_string(str(row[17]))
        search_region = db.escape_string(str(row[18]))
        mdcourt1 = db.escape_string(str(row[19]))
        mdcityservices1 = db.escape_string(str(row[20]))
        dcdmvmd1 = db.escape_string(str(row[21]))
        dcdmvdc1 = db.escape_string(str(row[22]))
        autreturn1 = db.escape_string(str(row[23]))
        tendigit1 = db.escape_string(str(row[24]))
        bge1 = db.escape_string(str(row[25]))
        bimpound = db.escape_string(str(row[26]))
        prince = db.escape_string(str(row[27]))
        status = db.escape_string(str(row[28]))
        last_check = db.escape_string(str(row[29]))
        count += 1

        if len(last_check) == 0:
            cursor.execute ("""
            UPDATE queue
            SET lstchk=%s
            WHERE vin = %s
            """,(date_added,vin))
            db.commit()
            since = 1
        else:
            curdate = str(time.strftime("%m/%d/%y"))
            start_date = datetime.strptime(curdate, "%m/%d/%y")
            end_date = datetime.strptime(last_check, "%m/%d/%y")
            since = abs((end_date-start_date).days)

        if since == 0: #change back to !=
            cursor.execute ("""
            UPDATE queue
            SET lstchk=%s
            WHERE vin = %s
            """,(curdate,vin))
            db.commit()

            if search_region == "1":
                print "some code soon"
            elif search_region == "2":
                region2(lname,fname,tag_number,vin,notify,phnumber);
            elif search_region == "3":
                print "some code soon"
            else:
                print "some code soon"

    except Exception as e:
        logger.error('Error --> : '+str(e))
        continue

cursor.close()
db.close()
timer = time.clock() - start_time
logger.info('System processing done with '+ str(count) +' entries')
logger.info('Total processing time: '+ str(timer))
sys.exit()