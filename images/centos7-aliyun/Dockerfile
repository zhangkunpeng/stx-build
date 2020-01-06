FROM centos:7

ENV DISTRO="centos"
RUN rm /etc/yum.repos.d/*
COPY yum.repos.d/* /etc/yum.repos.d/
RUN yum clean all && \
    yum update -y && \
    yum install -y git rpm-build rpm-sign make createrepo wget bzip2 sudo python2-pip yum-plugin-priorities.noarch&& \
    pip install --upgrade pip && \
    sed -i 's/keepcache=0/keepcache=1/' /etc/yum.conf

CMD /usr/sbin/init