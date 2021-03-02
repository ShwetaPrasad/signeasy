set -e
/usr/bin/python3 /opt/webapps/signeasy/manage.py migrate
/usr/local/bin/gunicorn --access-logfile - --workers 3 --bind 0.0.0.0:8181 --chdir /opt/webapps/signeasy signeasy.wsgi:application
