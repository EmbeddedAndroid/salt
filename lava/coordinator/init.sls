/etc/lava-coordinator/:
  file.directory:
    - user: root
    - group: root
    - mode: 755

/etc/lava-coordinator/lava-coordinator.conf:
  file.managed:
    {% if grains['id'] == 'ubuntu'%}
    - source: salt://lava/coordinator/lava-coordinator-staging.conf
    {% else %}
    - source: salt://lava/coordinator/lava-coordinator-production.conf
    {% endif %}
    - owner: root
    - mode: 644
