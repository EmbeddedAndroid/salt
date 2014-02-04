vsftpd:
  pkg:
    - latest
  service.running:
    - enable: True
    - reload: True

update_ftp_dir:
  cmd.run:
    {% if grains['id'] == 'ubuntu'%}
    - name: usermod -d /srv/lava/instances/staging/var/www/lava-server/images/ ftp
    {% else %}
    - name: usermod -d /srv/lava/instances/production/var/www/lava-server/images/ ftp
    {% endif %}
    - require:
      - pkg: vsftpd
