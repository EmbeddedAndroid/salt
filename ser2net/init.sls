ser2net:
  pkg:
    - installed
  file.managed:
    - source: salt://ser2net/ser2net.conf
    - name: /etc/ser2net.conf
    - owner: root
    - mode: 600
    - require:
      - pkg: ser2net
  service.running:
    - enable: True
    - watch:
      - file: /etc/ser2net.conf
      - pkg: ser2net
