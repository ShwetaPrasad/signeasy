FROM ubuntu:18.04
RUN apt-get update && apt-get install --no-install-recommends -y python3-pip supervisor
RUN echo "export TERM=xterm" >> /etc/bash.bashrc
RUN mkdir -p /opt/webapps/signeasy
COPY requirements.txt /tmp/
COPY signeasy/ /opt/webapps/signeasy/
COPY confs/supervisord/*.conf /etc/supervisor/conf.d/
COPY confs/startapp.sh /
RUN pip3 install wheel && pip3 install --upgrade setuptools && pip3 install -r /tmp/requirements.txt
EXPOSE 8181
CMD ["/usr/bin/supervisord"]