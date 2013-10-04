# allows syncing of our ARM model simulators
/opt/arm:
  url.sync_extract:
    - url: http://192.168.1.2/images/models/arm_models-2013-10-03.tgz
    - md5sum: 7fdf3a677cf40601bb4190ddecef7de1
    - user: root
    - group: root
    - mode: 755

#install tapctrl
/usr/sbin/tapctrl:
  file.symlink:
  - target: /opt/arm/RTSMv8_VE/scripts/tapctrl
  - require:
    - url: /opt/arm

#copy lava/fastmodels/FMNetwork script
/etc/init.d/FMNetwork:
  file.managed:
    - source: salt://lava/fastmodels/FMNetwork
    - mode: 0755
    - user: root
    - group: root

#start the FMNetwork script:
start_FMNetwork:
  service:
    - running
    - enable: True
    - name: FMNetwork
  require:
    - file: /etc/init.d/FMNetwork
    - url: /opt/arm
