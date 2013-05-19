from apscheduler.scheduler import Scheduler
from bottle import get, run, static_file
from json import loads, dumps, load, dump
import re
import sys
from threading import Thread, Event, Lock

WWW_FILES = './www'
DEBUG = False


RE_LENGTH = re.compile(r'length (\d+)')

bytes_this_second = 0
bytes_lock = Lock()

sched = Scheduler()
sched.start()


i = 0

def save_state():
    with file('history.json', 'w') as f:
        dump(history, f)

def load_state():
    with file('history.json') as f:
        return load(f)
        
try:
    history = load_state()
except:
    history = {
        'minute':    [0] * 60,
        'hour':      [0] * 60,
        'day':       [0] * 24,
        'month':     [0] * 30,
        'year':      [0] * 12,
        'progress' : [0] * 5}
    save_state()
    print 'Initialized Database'    

def collector():
    '''collects output from tcpdump [-i eth*] -qtv[n]'''
    

    while True:
        line = sys.stdin.readline()
        len_fields = RE_LENGTH.findall(line)
        for len_field in len_fields:
            if len_field.isdigit():
                collect_size(int(len_field))
        collect_count()


def collect_size(length):
    global bytes_lock, bytes_this_second, i
    with bytes_lock:
        bytes_this_second += int(length)

def collect_count(n = 1):
    global bytes_lock, bytes_this_second, i
    with bytes_lock:
        i += n
            

@sched.interval_schedule(seconds=1)
def aggregate():
    global bytes_lock, bytes_this_second, i
    
    with bytes_lock:
        current_bps = bytes_this_second
        bytes_this_second = 0
    #print current_bps, 'B/s'
    #print i, 'Packets/s'
    rotate(current_bps, [
        history['minute'],
        history['hour'],
        history['day'],
        history['month'],
        history['year']],
           history['progress'])
    i = 0

@sched.interval_schedule(minutes=1)
def autosave():
    save_state()

def rotate(insert, arrays, state, i = 0):
    assert len(arrays) == len(state)
    assert i < len(arrays)
    
    arrays[i].pop(0)
    arrays[i].append(insert)
    state[i] += 1
    if state[i] >= len(arrays[i]):
        state[i] = 0
        if i < len(arrays):
            rotate(sum(arrays[i]), arrays, state, i + 1)
    
        
    
    

if DEBUG:
    import random
    
    @sched.interval_schedule(seconds=1)
    def inject():
        collect_size(random.randint(0, 100000))
        collect_count(random.randint(0, 1000))
else:
    Thread(target=collector).start()
    

@get('/')
def index():
    return static_file('index.html', WWW_FILES)

@get('/history')
def index():
    #aggregate()
    return dumps([
        zip(range(-59, 1), map(lambda x: round(x / float(1<<10), 2), history['minute'])),
        zip(range(-59, 1), map(lambda x: round(x / float(1<<20), 2), history['hour'])),
        zip(range(-23, 1), map(lambda x: round(x / float(1<<20), 1), history['day'])),
        zip(range(-29, 1), map(lambda x: round(x / float(1<<30), 2), history['month'])),
        zip(range(-11, 1), map(lambda x: round(x / float(1<<30), 1), history['year']))
        ])

@get('/accumulated')
def index():
    m = sum(history['minute'])
    h = sum(history['hour'])
    d = sum(history['day'])
    M = sum(history['month'])
    Y = sum(history['year'])
    
    return dumps({
           'minute': m,
           'hour':   m + h,
           'day':    m + h + d,
           'month':  m + h + d + M,
           'year' :  m + h + d + M + Y
        })

@get('/favicon.ico')
def favicon():
    return static_file('favicon.ico', WWW_FILES)

@get('/static/<filename>')
def index(filename):
    return static_file(filename, WWW_FILES)

run(host='0.0.0.0', port=8002)
