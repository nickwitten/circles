source $(find /var/app/venv/*/bin/activate);
export $(sudo cat /opt/elasticbeanstalk/deployment/env | xargs);
