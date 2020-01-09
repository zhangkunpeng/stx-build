FROM centos:7.4.1708

ENV DISTRO="centos"
#RUN yum install -y epel-release git rpm-build rpm-sign make createrepo wget bzip2 sudo && \
#    yum install -y python2-pip && \
#    pip install --upgrade pip 

COPY yum.conf /etc/yum.conf
COPY .rpmmacros /root/.rpmmacros

CMD /usr/sbin/init