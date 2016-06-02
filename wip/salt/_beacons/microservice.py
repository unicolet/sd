# -*- coding: utf-8 -*-
'''
Watch listening tcp ports.
Fire when the port changes (in number or ports)

'''

# Import Python libs
from __future__ import absolute_import
import logging

log = logging.getLogger(__name__)

__ports__ = []

__virtualname__ = 'microservice'

def __virtual__():
   return __virtualname__

def validate(config):
    '''
    Validate the beacon configuration
    '''
    if not isinstance(config, dict):
        return False, ('Configuration for microservice beacon must be a dictionary.')
    return True, 'Valid beacon configuration'

def beacon(config):
    global __ports__
    log.debug('microservice beacon starting')
    ret = []
    _validate = validate(config)
    if not _validate:
        log.debug('microservice beacon unable to validate')
        return ret

    log.debug('microservice previous ports='+str(__ports__))

    server = __grains__['id']
    changed = False
    ports_now = []

    ports_all = __salt__['network.netstat']()
    for port in ports_all:
       if port.has_key('state') and port.get('state')=='LISTEN' and port.get('proto')=='tcp':
          current_port = int(port.get('local-address').split(':')[1])
          if current_port >= 3000 and current_port < 10000:
             ports_now.append(current_port)
             if not current_port in __ports__:
                changed = True

    if len(ports_now) != len(__ports__):
       changed = True
       __ports__ = ports_now

    if changed :
       _data = {'total_ports_seen': len(ports_now)}
       log.debug('Emit because changed={0} for {1} ( {2} != {3})'.format(changed, server,len(ports_now), len(__ports__)))
       ret.append(_data)
    return ret

