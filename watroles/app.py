import re
from flask import Flask, render_template, g
from query import Connection

app = Flask(__name__)
app.config.from_pyfile('settings.py')


@app.before_request
def setup():
    g.conn = Connection(
        app.config['LDAP_SERVER'],
        app.config['LDAP_BINDAS'],
        app.config['LDAP_PASSWORD']
    )


def output_instances(instances):
    """
    Outputs list of instances in appropriate format
    """
    # Sort by project by default
    instances.sort(key=lambda i: i.project)
    return render_template('instance_list.html', instances=instances)


@app.route('/role/<string:role>')
def with_role(role):
    # Roles can have 0-9, a-z, -, :, _ only
    if not re.match(r'^[a-z0-9_:-]+$', role):
        return 'Invalid role specified', 400
    return output_instances(g.conn.with_role(role))


@app.route('/variable/<string:key>/<string:value>')
def with_var(key, value):
    # Keys can only be a-z, _, value is a little more lax but not
    # too much - any more complex queries can be done by the user by hand
    if not re.match(r'^[a-z_]+$', key) or not re.match('^[a-zA-Z0-9:_-]+$', value):
        return 'Invalid key or value requested', 400
    return output_instances(g.conn.with_var(key, value))


@app.route('/project/<string:project>')
def from_project(project):
    # Project names are a-z, A-Z, 0-9, _, -
    if not re.match(r'^[a-zA-Z0-9_-]+$', project):
        return 'Invalid project specified', 400
    return output_instances(g.conn.from_project(project))


if __name__ == '__main__':
    app.run(debug=True)
