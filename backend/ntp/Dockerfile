FROM alpine:latest

#################################################
#### Blatently stolen from cturra/docker-ntp ####
#################################################

ARG BUILD_DATE

# install chrony
RUN apk add --no-cache chrony

# script to configure/startup chrony (ntp)
COPY startup.sh /opt/startup.sh

# ntp port
EXPOSE 123/udp

# let docker know how to test container health
HEALTHCHECK CMD chronyc tracking || exit 1

# start chronyd in the foreground
ENTRYPOINT [ "/bin/sh", "/opt/startup.sh" ]
