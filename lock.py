#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
import time

#once code works move the code and wrap it with elegant python goodness

#initialize values
lock_key = "bitcoin:lock"
exec_timeout = 60
lock_timeout = 10
lock_state = None

r = redis.StrictRedis(host='localhost', port=6379, db=0)

#loop till timeout
while exec_timeout >= 0:
    #for redis lt 2.6 use time.time() but it's quite error prone in a distributed env
    current_time = r.time()
    current_time = float('.'.join(str(i) for i in current_time))
    
    #setnx will set the value if key exists
    #the value is epoch + lock_timeout
    #if setnx returns 1 then lock is set
    if r.setnx(lock_key, (current_time + lock_timeout)):
        lock_state = "Acquired"
        print "Lock acquired"
        
        break

    #lock is already set. either someone has set lock or it has gone stale.
    
    #get the value of the lock key to check whether it has gone stale
    old_lock_expiry = float(r.get(lock_key))

    #if the lock expiry time has bypassed we kick it out
    #we also see whether someone jumped us to clear the stale lock
    #getset gives us the old value and we try to match it with the time we compared and if it differs no high fives as of yet
    if old_lock_expiry and old_lock_expiry < current_time and float(r.getset(lock_key, (current_time + lock_timeout))) == old_lock_expiry:
        lock_state = "Acquired"
        print "Stale lock cleared"
        
        break

    exec_timeout -= 1
    time.sleep(1)

if lock_state == "Acquired":
    #do your stuff here
    print "Mint your bitcoin here or walk your dog"

    lock_expiry = float(r.get(lock_key))
    
    #for redis lt 2.6 use time.time()
    current_time = r.time()
    current_time = float('.'.join(str(i) for i in current_time))

    #time to delete the lock but before deletion check whether we are within our timeout period to do so
    if lock_expiry and lock_expiry > current_time:
        print "Lock deleted"
        
        r.delete(lock_key)
    else:
        print "Backing off from deleting the lock"
else:
    print "Timed out."