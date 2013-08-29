/etc/lava-coordinator/:
  file.directory:
    - user: root
    - group: root
    - mode: 755

/etc/lava-coordinator/lava-coordinator.conf:
  file.managed:
    - source: salt://lava/coordinator/lava-coordinator.conf
    - owner: root
    - mode: 644
