udev:
  pkg:
    - installed
  file.managed:
    - source: salt://udev/99-usb-serial.rules
    - name: /etc/udev/rules.d/99-usb-serial.rules
    - owner: root
    - mode: 600
    - require:
      - pkg: udev
  service.running:
    - enable: True
    - watch:
      - file: /etc/udev/rules.d/99-usb-serial.rules
      - pkg: udev
