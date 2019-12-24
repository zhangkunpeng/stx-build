FROM centos:7.4.1708

ENV DISTRO="centos"
RUN yum install -y epel-release git rpm-build rpm-sign make gcc gcc-c++ createrepo wget bzip2 && \
    yum install -y postgresql-devel \
    libuuid-devel \
    python-devel \
    python-setuptools \
    python2-pip \
    python2-wheel &&\
    pip install --upgrade pip 

CMD /usr/sbin/init