import salt.client

RUNNING = 0
STOPPED = 1
UNKNOWN = 3

STATE_STRING = {
    RUNNING: 'running',
    STOPPED: 'stopped',
    UNKNOWN: '???',
}

LDT = '/home/instance-manager/lava-deployment-tool/lava-deployment-tool'


def salt_client():
    return salt.client.LocalClient()


def info(client, instance):
    """
    Shows whether an instance of LAVA is running or not on its configured hosts.
    """
    cmd = 'status lava-instance LAVA_INSTANCE={0}'.format(instance)
    inst_path = '/srv/lava/instances/{0}'.format(instance)
    worker_file = '{0}/sbin/mount-masterfs'.format(inst_path)

    inf = {}

    ret = client.cmd('*', 'lava.list_instances', [])
    for k, v in ret.iteritems():
        if inst_path in v:
            ret = client.cmd(k, 'cmd.run', [cmd])
            running = UNKNOWN
            if ret[k] == 'status: Unknown instance: %s' % instance:
                running = STOPPED
            elif ret[k] == 'lava-instance (%s) start/running' % instance:
                running = RUNNING

            ret = client.cmd(k, 'file.file_exists', [worker_file])
            master = not ret[k]
            server_ret = client.cmd(k, 'cmd.run', ["grep lava-server /srv/lava/instances/%s/bin/lava-server|grep git-cache" % instance])
            dispatcher_ret = client.cmd(k, 'cmd.run', ["grep dispatch /srv/lava/instances/%s/bin/lava-dispatch" % instance])
            server = server_ret[k].split("'")[1].replace("/srv/lava/.cache/git-cache/exports/lava-server/", "")
            dispatcher = dispatcher_ret[k].split("\"")[1].replace("/srv/lava/instances/%s/code/" % instance,"").replace("/bin/lava", "")
            inf[k] = {'running': running, 'master': master, 'dispatcher':dispatcher, 'server':server}
    return inf


def stop(client, instance, just_workers=False):
    """
    Issues a command to stop a given instance name on all minions where the
    LAVA instance appears to be running.
    """
    cmd = 'stop lava-instance LAVA_INSTANCE={0}'.format(instance)

    hosts = []
    for host, props in info(client, instance).iteritems():
        if props['running'] != STOPPED:
            if not just_workers or not props['master']:
                hosts.append(host)

    if len(hosts):
        return client.cmd(hosts, 'cmd.run', [cmd], expr_form='list')


def start(client, instance):
    """
    Issues a command to start a given instance name on all minions where the
    LAVA instance appears to not be running.
    """
    cmd = 'start lava-instance LAVA_INSTANCE={0}'.format(instance)

    hosts = []
    for host, props in info(client, instance).iteritems():
        if props['running'] != RUNNING:
            hosts.append(host)

    if len(hosts):
        return client.cmd(hosts, 'cmd.run', [cmd], expr_form='list')


def upgrade(client, instance, dry_run=True):
    """
    Runs lava-deployment-tool upgrade for a LAVA setup. It first shuts down
    each worker node instance. Then it runs lava-deployment-tool upgrade on
    the master. Lastly, it runs lava-deployment-tool upgradeworker on the
    worker nodes.
    """
    timeout = 300  # 5 minutes
    workers = []
    master = None

    for host, props in info(client, instance).iteritems():
        if props['master']:
            assert not master, 'Detected multiple master instances in LAVA deployment'
            master = host
        else:
            workers.append(host)

    assert master, 'No master instance found in LAVA deployment'

    w_ret = {}
    for h in workers:
        w_ret[h] = {'stop': 'dry-run', 'upgrade': 'dry-run', 'start': 'dry-run'}

    if dry_run:
        m_ret = {master: 'dry-run: upgrade master'}
        return m_ret, w_ret

    # first stop workers. This prevents a DB error if the upgrade changes
    # the schema.
    ret = stop(client, instance, True)
    if ret:
        for host, msg in ret.iteritems():
            w_ret[host]['stop'] = msg

    # now upgrade the master node
    skip_root_check = 'env={SKIP_ROOT_CHECK: "yes"}'
    client.cmd(master, 'cmd.run', ['{0} setup'.format(LDT), skip_root_check])
    cmd = '{0} upgrade {1}'.format(LDT, instance)
    m_ret = client.cmd(master, 'cmd.run', [cmd, skip_root_check], timeout=timeout)

    # now upgrade the workers
    cmd = '{0} upgradeworker {1}'.format(LDT, instance)
    if len(workers):
        client.cmd(workers, 'cmd.run', ['{0} setupworker'.format(LDT), skip_root_check])
        ret = client.cmd(workers, 'cmd.run', [cmd, skip_root_check], timeout=timeout, expr_form='list')
        for host, msg in ret.iteritems():
            w_ret[host]['upgrade'] = msg

    ret = start(client, instance)
    if ret:
        for host, msg in ret.iteritems():
            if host in w_ret:
                w_ret[host]['start'] = msg

    # last thing: l-d-t ran as root, lets chmod things
    cmd = 'chown -R instance-manager:instance-manager /srv/lava/instances/{0}/code/*'.format(instance)
    client.cmd(workers + [master], 'cmd.run', [cmd], expr_form='list')

    return m_ret, w_ret


def _update_props(inifile_content, props):
    for line in inifile_content.split('\n'):
        if not line.strip().startswith('#'):
            key, val = line.split('=')
            if key in props:
                props[key] = val.replace("'", '')


def add_worker(client, minion, minion_ip, instance, dry_run=True):
    """
    Creates a new lava workernode on a salt-minion.
    """

    args = {
        'LAVA_SERVER_IP': None,
        'LAVA_SYS_USER': None,
        'LAVA_PROXY': None,
        'masterdir': '/srv/lava/instances/{0}'.format(instance),
        'workerip': minion_ip,
        'ldt': LDT,
        'instance': instance,
        'dbuser': None,
        'dbpass': None,
        'dbname': None,
        'dbserver': None,
    }

    # ensure the instance exists and isn't already installed on the minion
    master = None
    for host, props in info(client, instance).iteritems():
        if props['master']:
            assert not master, 'Detected multiple master instances in LAVA deployment'
            master = host
        assert minion != host, 'LAVA instance already deployed on minion'

    assert master, 'No master instance found in LAVA deployment'

    # determine settings needed by looking at master instance
    cmd = 'cat {0}/instance.conf'.format(args['masterdir'])
    ret = client.cmd(master, 'cmd.run', [cmd])
    _update_props(ret[master], args)

    # get the db information
    cmd = 'cat {0}/etc/lava-server/default_database.conf'.format(args['masterdir'])
    ret = client.cmd(master, 'cmd.run', [cmd])
    _update_props(ret[master], args)
    if not args['dbserver']:
        args['dbserver'] = args['LAVA_SERVER_IP']

    cmd = ('{ldt} installworker -n {instance} 2>&1 | tee /tmp/ldt.log'.format(**args))
    env = 'env={ SKIP_ROOT_CHECK: "yes", '\
            'LAVA_DB_SERVER: "{dbserver}", ' \
            'LAVA_DB_NAME": "{dbname}", ' \
            'LAVA_DB_USER: "{dbuser}", ' \
            'LAVA_DB_PASSWORD: "{dbpass}", ' \
            'LAVA_REMOTE_FS_HOST: "{LAVA_SERVER_IP}", ' \
            'LAVA_REMOTE_FS_USER: "{LAVA_SYS_USER}", ' \
            'LAVA_REMOTE_FS_DIR: "{masterdir}", ' \
            'LAVA_PROXY: "{LAVA_PROXY}", ' \
            'LAVA_SERVER_IP: "{workerip}" }'.format(**args)

    if dry_run:
        return {minion: 'dry-run: {0}, {1}'.format(cmd, env)}

    ret = client.cmd(minion, 'cmd.run', [cmd, env], timeout=600)

    # l-d-t ran as root, lets chmod things
    cmd = 'chown -R instance-manager:instance-manager /srv/lava/instances/{0}/code/*'.format(instance)
    client.cmd(minion, 'cmd.run', [cmd])

    # now add the pubkey of the minion to the master's list of authorized keys
    cmd = 'cat /srv/lava/instances/{0}/home/.ssh/id_rsa.pub'.format(instance)
    pubkey = client.cmd(minion, 'cmd.run', [cmd])
    pubkey = pubkey[minion].replace('ssh key used by LAVA for sshfs', minion)
    authorized_keys = '{0}/home/.ssh/authorized_keys'.format(args['masterdir'])
    client.cmd(master, 'file.append', [authorized_keys, pubkey])

    return ret
