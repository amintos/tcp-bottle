from bottle import get, run
import sys
from threading import Thread, Event, Lock
import re
from apscheduler.scheduler import Scheduler

RE_LENGTH = re.compile(r'length (\d+)')

bytes_this_second = 0
bytes_lock = Lock()

sched = Scheduler()
sched.start()

i = 0

def collector():
    '''collects output from tcpdump [-i eth*] -qtv[n]'''
    global bytes_lock, bytes_this_second, i

    while True:
        line = sys.stdin.readline()
        len_fields = RE_LENGTH.findall(line)
        for len_field in len_fields:
            if len_field.isdigit():
                with bytes_lock:
                    bytes_this_second += int(len_field)
        i += 1
                    #print int(len_str[0])
        #print line[:50], len_fields
        
            

@sched.interval_schedule(seconds=1)
def aggregate():
    global bytes_lock, bytes_this_second, i
    
    with bytes_lock:
        current_bps = bytes_this_second
        bytes_this_second = 0
    print current_bps, 'B/s'
    print i, 'Packets/s'
    i = 0


collector()
