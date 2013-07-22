'''
Interaction with LAVA instances
===============================

.. code-block:: yaml

    salt://lava/devices/<host>/<instance>:
      lava:
        - sync_devices

'''
import difflib
import logging
import os
import shutil
import tempfile
import time

log = logging.getLogger(__name__)


def _inst_dir(inst):
    p = os.path.join('/srv/lava/instances', inst, 'etc/lava-dispatcher')
    dp = os.path.join(p, 'devices')
    if os.path.exists(p) and not os.path.exists(dp):
        os.mkdir(dp)
    return dp


def _local_devices(inst):
    devices = []
    for d in os.listdir(_inst_dir(inst)):
        if d.endswith('.conf'):
            devices.append(d)
    return set(devices)


def _get_diff(old, new):
    with open(old, 'r') as f:
        olines = f.readlines()
    with open(new, 'r') as f:
        nlines = f.readlines()

    return ''.join(difflib.unified_diff(olines, nlines, old, new))


def _sync_instances(ret, tmpdir, inst, devices):
    inst_dir = _inst_dir(inst)

    cur = _local_devices(inst)
    new = set(devices)

    for x in (new - cur):
        ret['changes']['new'].append('{0}.{1}'.format(inst, x))
    for x in (cur - new):
        ret['changes']['removed'].append('{0}.{1}'.format(inst, x))
        if not __opts__['test']:
            f = os.path.join(inst_dir, x)
            log.debug('deleting %s', f)
            os.unlink(f)

    # this helps reduce the unlikely situation where two schedulers wind
    # up trying to serve the same device
    time.sleep(5)

    for x in devices:
        curfile = os.path.join(inst_dir, x)
        newfile = os.path.join(tmpdir, inst, x)

        curhash = __salt__['cp.hash_file'](curfile)
        newhash = __salt__['cp.hash_file'](newfile)
        if curhash != newhash:
            if curhash:
                ret['changes']['diff'] += '\n' + _get_diff(curfile, newfile)
            if not __opts__['test']:
                if os.path.exists(curfile):
                    os.unlink(curfile)
                shutil.move(newfile, curfile)

    return True


def sync_devices(name):
    """
    If lava has instances defined on the minion, it will check on the master
    server for the device configs to keep in sync.

    name
        The salt url to this hosts inst/device files
    """
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}
    ret['changes']['new'] = []
    ret['changes']['removed'] = []
    ret['changes']['diff'] = ''

    if __opts__['test']:
        ret['result'] = None

    if not os.path.exists('/srv/lava'):
        return _fail(ret, 'LAVA not installed on this node')

    host = __grains__['host']

    tmpdir = tempfile.mkdtemp()
    try:
        files = __salt__['cp.get_dir'](name, tmpdir)
        if not files or len(files) == 0:
            ret['comment'] = 'No devices defined for {0}'.format(host)
            return ret
        # the cp.get_dir always includes the base from the remote path,
        # append that to tmpdir so we are really where we need to traverse
        parts = name.rsplit('/')
        if parts[-1]:
            instdir = os.path.join(tmpdir, parts[-1])
        else:  # name had a trailing '/'
            instdir = os.path.join(tmpdir, parts[-2])

        comments = []
        for inst in os.listdir(instdir):
            path = os.path.join(instdir, inst)
            if not os.path.isdir(path):
                comments.append('{0} not a directory, ignoring'.format(inst))
            else:
                devices = os.listdir(path)
                if not _sync_instances(ret, instdir, inst, devices):
                    return ret
    finally:
        shutil.rmtree(tmpdir)

    changes = ret['changes']
    if changes['diff'] or len(changes['new']) > 0 or len(changes['new']) > 0:
        comments.append('Device config changed on {0}'.format(host))
    ret['comment'] = '\n'.join(comments)

    return ret


def _fail(ret, comment):
    ret['result'] = False
    ret['comment'] = comment
    return ret
