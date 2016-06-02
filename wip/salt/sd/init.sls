#!py
# https://docs.saltstack.com/en/latest/ref/renderers/all/salt.renderers.py.html

import time
import re

def parse_netstat_data():
   haproxy_re=re.compile('haproxy')
   netstats = __salt__['mine.get']('*','network.netstat')
   endpoints = {}

   has_ports = True

   for host, ports in netstats.iteritems():
      if len(ports) == 0:
         # I can't find a way to get the follwoing checks cover all cases.
         # for now I'll just leave to orchestarte to detect a failed mine.update
         # and here abort quickly. Don't try to be too smart
         #
         # try to ssh the host...
         #if __salt__['network.connect'](host, 22, True)
         #   # the host is up, but for some reason it has not updated the salt mine yet, do not
         #   # apply this config to haproxy or there might be service disruption
         has_ports = False

      for port in ports:
         if port.has_key('state') and port.get('state') == 'LISTEN' and port.get('proto') == 'tcp' and haproxy_re.search(port.get('program')) is None:
            (listenaddress, listenport) = port['local-address'].split(':')
            listenport = int(listenport)
            if listenaddress != "127.0.0.1":
               if listenport >= 3000 and listenport < 10000 and listenport not in [4505, 4506]:
                  if listenport in endpoints:
                     endpoints[listenport].append(host)
                  else:
                     endpoints[listenport]=[host]
   return (endpoints, has_ports)

def run():
   endpoints = {}
   has_ports = True
   retries = 2

   (endpoints, has_ports) = parse_netstat_data()

   while retries > 0 and not has_ports:
      # if mine data is incomplete retry two times with a pause in between
      (endpoints, has_ports) = parse_netstat_data()
      retries = retries - 1
      time.sleep(10)

   cfg = {}

   # if a host still has no ports then maybe it did not push netstat into mine yet
   # leave the configuration be to avoid disruption.
   if has_ports:
      cfg['haproxy_cfg'] = {
            'file.managed': [
                {'name': '/etc/haproxy/haproxy.cfg'},
                {'source': 'salt://sd/haproxy.cfg'},
                {'template': 'jinja'},
                {'context': {
                    'endpoints': endpoints,
                    },
                },
            ],
      }
      cfg['haproxy_svc'] = {
         'pkg.installed': [
             { 'name' : 'haproxy' },
          ],
          'service.running': [
             { 'name' : 'haproxy' },
             { 'enable' : False },
             { 'watch': [
                { 'file' : 'haproxy_cfg' }
             ] },
             { 'require' : [
                { 'pkg' : 'haproxy_svc' }
             ] }
          ]
      }

   return cfg

