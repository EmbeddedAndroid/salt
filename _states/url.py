'''
Allows you to keep a tarball from a URL exploded on a target
============================================================

.. code-block:: yaml

    /tmp/blah:
      url.sync_extract
        - url: http://foo.com/blah.tgz:
        - md5sum: 1234ABD #optional
        - user: root      #optional
        - group: root     #optional
        - mode: 755       #optional
'''
import logging
import os
import tempfile
import shutil
import subprocess
import urllib2
import urlparse

log = logging.getLogger(__name__)

MD5SUM_FILE = '.salt.md5sum'


def _touch(fname):
    with file(fname, 'a'):
        os.utime(fname, None)


def _contents(fname):
    try:
        with open(fname, 'r') as f:
            return f.read()
    except IOError:
        return ''


def _download(url, tmpdir):
    bname = urlparse.urlparse(url).path.rsplit('/', 1)[-1]
    fname = os.path.join(tmpdir, bname)

    response = urllib2.urlopen(url)
    with open(fname, 'w') as f:
        bsize = 32768
        buff = response.read(bsize)
        while buff:
            f.write(buff)
            buff = response.read(bsize)
    return fname


def _replace(path, tmpdir, tball, md5sum):
    subprocess.check_call(
        ['tar', '-x', '-f', tball], cwd=tmpdir)
    os.unlink(tball)
    with open(os.path.join(tmpdir, MD5SUM_FILE), 'w') as f:
        f.write(md5sum)
    subprocess.check_call(['rm', '-r', '-f', path])
    subprocess.check_call(['mv', tmpdir, path])


def sync_extract(name, url, md5sum, user=None, group=None, mode=None):
    """
    Will download the tarball and extract it locally if the md5sum has or
    does not yet exist
    """
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}
    ret['changes']['diff'] = ''
    ret['comment'] = '{0} already in sync with {1}'.format(name, url)

    tmpdir = tempfile.mkdtemp()
    try:
        md5sum_file = os.path.join(name, MD5SUM_FILE)
        if not os.path.exists(name):
            log.info('path does not exist')
            if not __opts__['test']:
                os.makedirs(name)
                _touch(md5sum_file)
        orig_md5sum = _contents(md5sum_file)
        if orig_md5sum != md5sum:
            log.info('md5sum is different, downloading and extracting')
            tball = _download(url, tmpdir)
            if not __opts__['test']:
                _replace(name, tmpdir, tball, md5sum)
            ret['comment'] = '{0} is in sync with {1}'.format(name, url)
            ret['changes']['diff'] = '- {0}\n+ {1}'.format(orig_md5sum, md5sum)

        # file.check_perms appends to our "ret" value, so changes are preserved correctly
        __salt__['file.check_perms'](name, ret, user, group, mode)
    except Exception:
        ret['result'] = False
        ret['comment'] = 'Failed to download and extract'
        log.exception('Failed to download and extract')
        shutil.rmtree(tmpdir)

    return ret
