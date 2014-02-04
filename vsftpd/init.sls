vsftpd:
  pkg:
    - latest
  service.running:
    - enable: True

ftp:
    user.present:
        {% if grains['id'] == 'ubuntu'%}
        - home: /srv/lava/instances/staging/var/www/lava-server/images/
        {% else %}
        - home: /srv/lava/instances/production/var/www/lava-server/images/
        {% endif %}
        - require:
            - pkg.installed: vsftpd
