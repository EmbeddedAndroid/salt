'''
Support for the bzr SCM

based on: https://raw.github.com/saltstack/salt/develop/salt/modules/git.py
'''

import os
import logging

from salt import utils, exceptions

log = logging.getLogger(__name__)


def _bzr_run(cmd, cwd=None, **kwargs):
    '''
    simple, throw an exception with the error message on an error return code.

    this function may be moved to the command module, spliced with
    'cmd.run_all', and used as an alternative to 'cmd.run_all'. Some
    commands don't return proper retcodes, so this can't replace 'cmd.run_all'.
    '''
    result = __salt__['cmd.run_all'](cmd, cwd=cwd, **kwargs)

    retcode = result['retcode']

    if retcode == 0:
        return result['stdout']
    else:
        raise exceptions.CommandExecutionError(result['stderr'])

def _check_bzr():
    utils.check_or_die('bzr')

def revision(cwd, opts=None, user=None):
    '''
    Returns the revno the repository is at

    cwd
        The path to the bzr repository

    user : None
        Run bzr as a user other than what the minion runs as

    CLI Example::

        salt '*' bzr.revision /path/to/repo
    '''
    _check_bzr()

    if not opts:
        opts = ''
    cmd = 'bzr revno {0}'.format(opts)
    return _bzr_run(cmd, cwd, runas=user)

def branch(cwd, repository, opts=None, user=None):
    '''
    Perform a bzr branch on the given repository

    cwd
        The path to the repository to save as

    repository
        The bzr uri of the repository

    opts : None
        Any additional options to add to the command line

    user : None
        Run as a user other than what the minion runs as

    CLI Example::

        salt '*' bzr.branch /path/to/repo lp:lava-deployment-tool

        salt '*' bzr.branch /path/to/repo \\
                lp:lava-deployment-tool '-r 33'

    '''
    _check_bzr()

    if not opts:
        opts = ''
    cmd = 'bzr branch {0} {1} {2}'.format(repository, cwd, opts)

    return _bzr_run(cmd, runas=user)

def pull(cwd, opts=None, user=None):
    '''
    Perform a pull on the given repository

    cwd
        The path to the bzr repository

    opts : None
        Any additional options to add to the command line

    user : None
        Run bzr as a user other than what the minion runs as

    CLI Example::

        salt '*' bzr.pull /path/to/repo opts='--overwrite'
    '''
    _check_bzr()

    if not opts:
        opts = ''
    return _bzr_run('bzr pull {0}'.format(opts), cwd=cwd, runas=user)

