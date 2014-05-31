/etc/lava-dispatcher/devices:
  file.recurse:
    - source: salt://lava/devices/{{ grains['id'] }}
    - clean: True
    - include_empty: True

/etc/lava-dispatcher/device-types:
  file.recurse:
    - source: salt://lava/device-types
    - clean: True
    - include_empty: True

/usr/local/lab-scripts:
  file.recurse:
    - source: salt://lava/lab-scripts
    - file_mode: 755
    - clean: True
    - include_empty: True
