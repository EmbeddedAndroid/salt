base:

  'lava-master':
    - lava
    - snmp
    - expect

  'lava-worker-*':
    - match: pcre
    - udev
    - lava
    - snmp
    - expect
    - lit
    - lava.coordinator

