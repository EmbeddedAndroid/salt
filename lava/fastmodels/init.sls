# allows syncing of our ARM model simulators
/opt/arm:
  url.sync_extract:
    - url: http://images-private.armcloud.us/models/arm_models-2014-01-22.tgz
    - md5sum: 1d2011ce025fb7881c064206e040a34a
    - user: root
    - group: root
    - mode: 755

libc6:i386:
  pkg:
    - latest

libstdc++6:i386:
  pkg:
    - latest

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
