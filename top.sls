base:
  '*':
    - sshd
    - udev
    - instance_manager
    - bzr
    - lava
    - ser2net
    - lava.fastmodels
    - adb
    - fastboot
    - openbsd-inetd
    - tftpd-hpa
    - nfs
    - qemu
    - snmp
    - expect
    - lit
    - ia32-libs
    - bridge-utils
    - salt-minion
    - lava.coordinator

  'vps-1140700-17880.manage.myhosting.com':
    - salt-master
