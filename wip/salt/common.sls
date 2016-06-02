haproxy:
  pkg.installed:
     - pkgs:
        - haproxy
        - haproxyctl
        - python-pip
        - socat
        - wget
        - curl

haproxy_pip:
  pip.installed:
     - name: haproxyctl

helper_sh:
  file.managed:
     - name: /bin/svc_deploy.sh
     - source: salt://sd/svc_deploy.sh
     - user: root
     - group: root
     - mode: 755


