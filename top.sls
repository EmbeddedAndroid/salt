base:

  'lava-master':
    - lava
    - snmp
    - expect

  'lava-worker-*':
    - match: pcre
    - adb
    - fastboot
    - udev
    - lit
    - lava
    - nfs
    - vsftpd
    - snmp
    - expect
    - lit
    - lava.coordinator

  'lava-worker-03':
    - bridge-utils
    - lava.fastmodels
