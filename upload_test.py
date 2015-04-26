import json
import urllib2

url = 'http://worldwater.byu.edu/app/index.php/default/services/api/values'
data = {
    "user2": "admin",     #change this to your username
    "password": "password", #change this to your password
    "siteid": "RCSR-R",        #use your site code here
    "variableid": "KOCOUR",      #use your variable code here
    "methodid": 1,               #use your method id here
    "sourceid": 15,               #use your source id here
    "values": [("2015-01-01 04:00:00", 7.5),
               ("2015-01-01 05:00:00", 7.6),
               ("2015-01-01 10:00:00", 8.98)]
}
req = urllib2.Request(url)
req.add_header('Content-Type', 'application/json')
postdata = json.dumps(data)

try:
    response = urllib2.urlopen(req, postdata)
    print response.read()
    status = json.load(response)
    print status

except urllib2.HTTPError, e:
    print e.code
    print e.msg
    print e.headers
    print e.fp.read()