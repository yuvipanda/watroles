import ldap3


class Instance(object):
    def __init__(self, **kwargs):
        self.data = kwargs

    def __getattr__(self, name):
        return self.data[name]

    def to_dict(self):
        return self.data


class Connection(object):
    def __init__(self, server, bindas, passwd):
        server = ldap3.Server(server)
        self.conn = ldap3.Connection(
            server, read_only=True,
            user=bindas, password=passwd,
            auto_bind=ldap3.AUTO_BIND_TLS_AFTER_BIND)

    def _get_instances(self, query):
        self.conn.search(
            'ou=hosts,dc=wikimedia,dc=org',
            query,
            ldap3.SEARCH_SCOPE_WHOLE_SUBTREE,
            attributes=ldap3.ALL_ATTRIBUTES)
        hosts = []
        for responseitem in self.conn.response:
            hostinfo = responseitem['attributes']
            if 'aRecord' in hostinfo:
                ip = [a for a in hostinfo['aRecord'] if a.startswith('10.')][0]
            else:
                ip = None
            puppetvars = {
                var[0]: var[1]
                for var in [pv.split("=") for pv in hostinfo['puppetVar']]
            }
            hosts.append(Instance(
                name=puppetvars['instancename'] if 'instancename' in puppetvars else None,
                ip=ip,
                roles=hostinfo['puppetClass'],
                vars=puppetvars,
                project=puppetvars['instanceproject'] if 'instanceproject' in puppetvars else None
            ))
        return hosts

    def with_role(self, role):
        return self._get_instances('(puppetClass=%s)' % role)

    def with_var(self, var, value):
        return self._get_instances('(puppetVar=%s=%s)' % (var, value))

    def from_project(self, project):
        return self.with_var('instanceproject', project)
