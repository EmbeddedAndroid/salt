instance-manager:
  user.present:
    - fullname: LAVA Instance Manager
    - shell: /bin/bash
    - home: /home/instance-manager/
    - password: "$6$deeghiuc$XR0x84I.p6/JEMUuZjRLKM6Q7NWD9YsdjwT/qeR9zuGLKNBJRPRKpX7malPM59lV4Cqi2DDsTDEQ3R/ZL2.im/"
    - groups:
      - sudo

/etc/sudoers.d/instance-manager:
  file.managed:
      - source: salt://instance_manager/sudoer_file
      - user: root
      - group: root
      - mode: 440

/usr/local/bin/become-instance-manager:
  file.managed:
      - source: salt://instance_manager/become-instance-manager
      - user: root
      - group: root
      - mode: 755

http://git.linaro.org/git/lava/lava-deployment-tool.git:
  git.latest:
    - target: /home/instance-manager/lava-deployment-tool
    - force: yes
