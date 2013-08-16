# allows us to keep files in sync with lava instances on hosts
# this assumes a file layout on the server like:
#   /srv/salt/lava/devices/<host>/<instance>/
#           device1.conf, device2.conf, ...
salt://lava/devices/{{ grains['id'] }}:
  lava:
    - sync_devices

{% for inst in salt['lava.list_instances']() %}
{{ inst }}/etc/lava-dispatcher/device-types:
  file.recurse:
    - source: salt://lava/device-types
    - clean: True
{% endfor %}

/usr/local/lab-scripts:
  file.recurse:
    - source: salt://lava/lab-scripts
    - file_mode: 755
    - clean: True
