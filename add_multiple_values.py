import urllib, urllib2, cookielib
import json
import datetime
import random

# this is a sample python client for the datapoint API for adding multiple data values
# author: Jiri Kadlec
# to check if data values were added, go to worldwater.byu.edu/app and site 'Teva Test' inside Utah Lake.

username = 'admin'
password = 'password'

sourceID = 15
variableID = 43
siteID = 170
methodID = 10
dataValue1 = random.random() * 100
dataValue2 = random.random() * 100
dataValue3 = random.random() * 100

currentDateTime = datetime.datetime.now()
date1 = currentDateTime + datetime.timedelta(minutes=10)
date2 = currentDateTime + datetime.timedelta(minutes=20)
date3 = currentDateTime + datetime.timedelta(minutes=30)

#STEP 1: prepare the uploaded data in JSON format
data = {
    "siteid": siteID,
    "varid": variableID,
    "methodid": methodID,
    "sourceid": sourceID,
    "values": [(date1.strftime("%Y-%m-%d %H:%M:%S"), dataValue1),
               (date2.strftime("%Y-%m-%d %H:%M:%S"), dataValue2),
               (date3.strftime("%Y-%m-%d %H:%M:%S"), dataValue3)]
}
postdata = json.dumps(data)


#STEP 2: login and get the authentication cookie (NOTE: cookie is like API key)
loginPage = 'http://worldwater.byu.edu/app/index.php/default/auth/login'
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
login_data = urllib.urlencode({'username' : username, 'password' : password, 'submit' : 'Login'})
opener.open(loginPage, login_data)

#STEP 3: post the data values to HydroServer and check response status
uploadPage = 'http://localhost/hslite-mvc/index.php/default/datapoint/addmultiple'
print uploadPage
resp = opener.open(uploadPage, postdata)
print resp.read()
