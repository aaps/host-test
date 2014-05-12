#!/usr/bin/env python2.5
from threading import Thread
import subprocess
from Queue import Queue
import urllib
import httplib

num_threads = 4
queue = Queue()
results = {}
reportto = "tkkrnet.vuurrosmedia.nl"
ips = ["google.com", "10.0.1.3", "10.0.1.11", "10.0.1.51"]
#wraps system ping command
def pinger(r, q):
    """Pings subnet"""
    while True:
        ip = q.get()
        # print "Pinging %s" %  ip
        ret = subprocess.Popen(["ping", "-c 3" , "-q",  ip], stdout=subprocess.PIPE)
        splitted = ret.communicate()[0].split('\n')
        lastsplit =  splitted[3].split(' ')
        if lastsplit[0].strip() == lastsplit[3].strip():
            data = {'message':str(ip)+': alive','milis':lastsplit[9].strip()}
            r[ip] = data
        else:
            data = {'message':'%s: down' % ip}
            r[ip] = data
        q.task_done()
#Spawn thread pool
for i in ips:
    worker = Thread(target=pinger, args=(results, queue))
    worker.setDaemon(True)
    worker.start()
#Place work in queue
for ip in ips:
    queue.put(ip)
#Wait until worker threads are done to exit    
queue.join()

encoded = urllib.urlencode(results)

h = httplib.HTTPConnection('pyrotest:80')
headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
h.request('POST', '/index.php/periods/logit', encoded, headers)
r = h.getresponse()

print r.read()