tftpd-hpa:
  pkg:
    - latest
  file.managed:
    {% if grains['id'] == 'ubuntu'%}
    - source: salt://tftpd-hpa/tftpd-hpa-staging
    {% else %}
    - source: salt://tftpd-hpa/tftpd-hpa-production
    {% endif %}
    - name: /etc/default/tftpd-hpa
    - owner: root
    - mode: 600
    - require:
      - pkg: tftpd-hpa
  service.running:
    - enable: True
    - watch:
      - file: /etc/default/tftpd-hpa
      - pkg: tftpd-hpa
