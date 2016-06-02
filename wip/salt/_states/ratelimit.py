import salt.exceptions
import logging
import time

__name__ = 'ratelimit'

log = logging.getLogger(__name__)

def event(name, event_in, event_out):
    bucket = {}
    forward = False
    ret = {'event_in': event_in, 'changes': {}, 'result': False, 'comment': '', 'name': __name__}

    rate = 1.0; # unit: event
    per  = 30.0; # unit: seconds
    
    results = __salt__['sqlite3.fetch']('/etc/salt/rl.db',"select k,allowance,last_check from rl where k='{0}'".format(event_in))
    if len(results) == 1:
       bucket=results[0]

    log.debug(str(bucket))

    if bucket:
       allowance = bucket[1]
       last_check = bucket[2]
       log.debug('event key found in bucket')
    else:
       last_check = int(time.time()); # floating-point, e.g. usec accuracy. Unit: seconds
       allowance = rate; # unit: event
       log.debug('event key NOT found in bucket')
   
    log.debug('BEGIN allowance={0} last_check={1}'.format(allowance,last_check)) 

    current = int(time.time());
    time_passed = current - last_check;
    last_check = current;
    allowance += time_passed * (rate / per);
    if (allowance > rate):
       allowance = rate; # throttle
       ret['comment'] = 'Event "{0}" throttled'.format(event_in)
    if (allowance < 1.0):
       log.debug(__name__ + 'rate limiting event: '+str(event_in))
       ret['comment'] = 'Event "{0}" rate limited'.format(event_in)
    else:
       log.debug('forwarding event: '+str(event_in)+' as '+str(event_out))
       ret['comment'] = 'Event "{0}" forwarded'.format(event_in)
       allowance -= 1.0;
       forward = True

    log.debug('END allowance={0} last_check={1}'.format(allowance,last_check)) 
   
    if not bucket:
       __salt__['sqlite3.modify']('/etc/salt/rl.db',"insert into rl (k,allowance,last_check) values ('{0}',{1},{2})".format(event_in, allowance, last_check))
    else: 
       __salt__['sqlite3.modify']('/etc/salt/rl.db',"update rl set allowance={1},last_check={2} where k='{0}'".format(event_in, allowance, last_check))

    ret['result'] = forward

    if forward:
       __salt__['event.send'](event_out, ret)

    return ret

