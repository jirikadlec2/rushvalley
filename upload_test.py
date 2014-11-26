import json
import urllib2

url = 'http://localhost/hslite/services/index.php/upload/values'
data = {
    "user": "YOUR_USERNAME",     #change this to your username
    "password": "YOUR_PASSWORD", #change this to your password
    "sitecode": "SITE01",        #use your site code here
    "variablecode": "tmin",      #use your variable code here
    "methodid": 1,               #use your method id here
    "sourceid": 1,               #use your source id here
    "utcoffset": -7,
    "values": [("2014-09-01 04:00:00", 7.5),
               ("2014-09-01 05:00:00", 7.6),
               ("2014-09-01 10:00:00", 8.98)]
}
req = urllib2.Request(url)
req.add_header('Content-Type', 'application/json')
postdata = json.dumps(data)

try:
    response = urllib2.urlopen(req, postdata)
    status = json.load(response)
    print status

except urllib2.HTTPError, e:
    print e.code
    print e.msg
    print e.headers
    print e.fp.read()