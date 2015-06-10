import urllib, urllib2, cookielib
import datetime
import random

# this is a sample python client for the datapoint API for adding one data value
# author: Jiri Kadlec
# to check if data value was added, go to worldwater.byu.edu/mvc and site 'Teva Test' inside Utah Lake.

username = 'admin'
password = 'password'

sourceID = 15
variableID = 43
siteID = 170
methodID = 10
dataValue = random.random() * 100

currentDateTime = datetime.datetime.now()
date = currentDateTime.strftime('%Y-%m-%d')
time = currentDateTime.strftime('%H:%M:%S')

parameters = {'sid':siteID,
            'varid':variableID,
            'mid':methodID,
            'dt':date,
            'time':time,
            'val':dataValue}
url = 'http://worldwater.byu.edu/mvc/index.php/default/datapoint/add' + '?' + urllib.urlencode(parameters)
print url

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
login_data = urllib.urlencode({'username' : username, 'password' : password, 'submit' : 'Login'})
opener.open('http://worldwater.byu.edu/mvc/index.php/default/auth/login', login_data)

resp = opener.open(url)
print resp.read()
