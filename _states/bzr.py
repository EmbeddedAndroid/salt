'''
Interaction with bzr repositories.
==================================

based on https://raw.github.com/saltstack/salt/develop/salt/states/git.py

.. code-block:: yaml

    lp:lava-deployment-tool
      bzr.latest:
        - target: /tmp/lava-deployment-tool
'''
import logging
import os
import shutil

log = logging.getLogger(__name__)


def __virtual__():
    '''
    Only load if git is available
    '''
    return 'bzr' if __salt__['cmd.has_exec']('bzr') else False


def latest(name, target=None, runas=None, force=None):
    '''
    Make sure the repository is branched to the given directory and is up to date

    name
        Address of the remote repository as passed to "bzr branch"
    target
        Name of the target directory where repository is about to be cloned
    runas
        Name of the user performing repository management operations
    force
        Force bzr into pre-existing directories (deletes contents)
    '''
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}
    if not target:
        return _fail(ret, '"target" option is required')

    if os.path.isdir(target) and os.path.isdir('{0}/.bzr'.format(target)):
        # bzr pull is probably required
        log.debug(
                'target {0} is found, "bzr pull" is probably required'.format(
                    target)
                )
        try:
            opts = '-r revno:-1:{0}'.format(name)
            cur_r = __salt__['bzr.revision'](cwd=target, user=runas)
            new_r = __salt__['bzr.revision'](cwd=target, opts=opts, user=runas)
        except Exception as exc:
            return _fail(ret, str(exc))

        if cur_r != new_r:
            log.info('Repository {0} updated: {1} => {2}'.format(
                target, cur_r, new_r))
            ret['comment'] = 'Repository {0} updated'.format(target)
            ret['changes']['revision'] = '{0} => {1}'.format(cur_r, new_r)

            if __opts__['test']:
                return ret
            try:
                __salt__['bzr.pull'](target, user=runas)
                new_r = __salt__['bzr.revision'](cwd=target, user=runas)
                ret['changes']['revision'] = '{0} => {1}'.format(cur_r, new_r)
            except Exception as exc:
                return _fail(ret, str(exc))
    else:
        if os.path.isdir(target):
            # bzr branch is required, target exists but force is turned on
            if force:
                log.debug(
                    'target {0} found, but not a bzr repo. Since force option'
                    ' is in use, deleting.'.format(target))
                shutil.rmtree(target)
            # bzr branch is required, but target exists and is non-empty
            elif os.listdir(target):
                return _fail(ret, 'Directory exists, is non-empty, and force '
                    'option not in use')

        # git clone is required
        log.debug(
            'target {0} is not found, "bzr branch" is required'.format(target))

        if __opts__['test']:
            return _neutral_test(
                    ret,
                    'Repository {0} is about to be branched to {1}'.format(
                        name, target))
        try:
            # make the branch
            __salt__['bzr.branch'](target, name, user=runas)
            new_r = __salt__['bzr.revision'](target, user=runas)

        except Exception as exc:
            return _fail(ret, str(exc))

        message = 'Repository {0} branched to {1}'.format(name, target)
        log.info(message)
        ret['comment'] = message

        ret['changes']['new'] = name
        ret['changes']['revision'] = new_r
    return ret


def _fail(ret, comment):
    ret['result'] = False
    ret['comment'] = comment
    return ret


def _neutral_test(ret, comment):
    ret['result'] = None
    ret['comment'] = comment
    return ret
