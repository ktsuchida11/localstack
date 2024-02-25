FROM localstack/localstack
COPY --chown=localstack ./provision.sh /etc/localstack/init/ready.d/provision.sh
RUN chmod u+x /etc/localstack/init/ready.d/provision.sh