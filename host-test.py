#!/usr/bin/env python2.5
from threading import Thread
import subprocess
from Queue import Queue
import urllib
import httplib

num_threads = 4
queue = Queue()
results = {}

reportto = "tkkrnet.vuurrosmedia.nl:80"
reporturl = "/index.php/graphit/logit"
ips = ["www.google.com", "10.42.2.252", "10.42.3.101", "10.42.3.102", "10.42.3.103", "10.42.3.104","10.42.3.105","10.42.3.106","10.42.3.107","10.42.3.108","10.42.3.109"]
#wraps system ping command
def pinger(r, q):
    """Pings subnet"""
    while True:
        ip = q.get()
        # print "Pinging %s" %  ip
        ret = subprocess.Popen(["ping", "-c 3" , "-q",  ip], stdout=subprocess.PIPE)
        splitted = ret.communicate()[0].split('\n')
        
	if splitted[4] is not '':
            lastsplit = splitted[4].split(' ')                
            data = {'name':'tkkrlab','slug':'tkkrlab',ip:lastsplit[3].split('/')[1].strip()}
            r.update(data);
        else:
            data = {'name':'tkkrlab','slug':'tkkrlab',ip:'999'}
            r.update(data);
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
print results
encoded = urllib.urlencode(results)

h = httplib.HTTPConnection(reportto)
headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
h.request('POST', reporturl, encoded, headers)
r = h.getresponse()

print r.read()
