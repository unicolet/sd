mine.update:
  salt.function:
    - tgt: '*'
    - expect_minions: True
    - kwarg:
      - clear: True

update_haproxy:
  salt.state:
    - tgt: '*'
    - sls:
      - sd
    - require:
      - salt: mine.update

