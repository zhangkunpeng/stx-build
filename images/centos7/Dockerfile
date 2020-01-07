FROM centos:7

ENV DISTRO="centos"
#RUN yum install -y epel-release git rpm-build rpm-sign make createrepo wget bzip2 sudo && \
#    yum install -y python2-pip && \
#    pip install --upgrade pip 

COPY yum.conf /etc/yum.conf

CMD /usr/sbin/init