nfs-kernel-server:
  pkg:
    - latest
  file.managed:
    {% if grains['id'] == 'ubuntu'%}
    - source: salt://nfs/exports-staging
    {% else %}
    - source: salt://nfs/exports-production
    {% endif %}
    - name: /etc/exports
    - owner: root
    - group: root
    - mode: 644
    - require:
      - pkg: nfs-kernel-server
  service.running:
    - enable: True
    - watch:
      - file: /etc/exports
      - pkg: nfs-kernel-server

rpcbind:
  pkg:
    - latest

update_exports:
  cmd.run:
    - name: exportfs -ra
    - require:
      - pkg: nfs-kernel-server
    - watch:
      - file: /etc/exports
