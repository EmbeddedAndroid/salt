linaro-image-tools:
  pkgrepo.managed:
    - humanname: Linaro PPA
    - name: deb http://ppa.launchpad.net/linaro-maintainers/tools/ubuntu/ precise main
    - file: /etc/apt/sources.list.d/linaro.list
    - keyid: 7BE1F97B
    - keyserver: keyserver.ubuntu.com
    - require_in:
      - pkg: linaro-image-tools
  pkg.latest:
    - name: linaro-image-tools
    - refresh: True
