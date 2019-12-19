FROM centos:7.4.1708

RUN yum install -y epel-release git rpm-build rpm-sign make gcc gcc-c++ createrepo && \
    yum install -y postgresql-devel \
    libuuid-devel \
    python-devel \
    python-setuptools \
    python2-pip \
    python2-wheel &&\
    pip install --upgrade pip 

COPY stx-build /stx-build

RUN cd /stx-build && \
    pip install -r requirements.txt && \
    python setup.py install && \
    rm -rf /stx-build &&\
    echo "[stx-rpm]" >> /etc/yum.repos.d/stx.repo &&\
    echo "name=SatrlingX Packages" >> /etc/yum.repos.d/stx.repo &&\
    echo "baseurl=file:///tmp/centos/rpm/" >> /etc/yum.repos.d/stx.repo &&\
    echo "enabled=1" >> /etc/yum.repos.d/stx.repo &&\
    echo "gpgcheck=0" >> /etc/yum.repos.d/stx.repo &&\
    echo "" >> /etc/yum.repos.d/stx.repo &&\
    echo "[stx-srpm]" >> /etc/yum.repos.d/stx.repo &&\
    echo "name=SatrlingX Packages" >> /etc/yum.repos.d/stx.repo &&\
    echo "baseurl=file:///tmp/centos/srpm/" >> /etc/yum.repos.d/stx.repo &&\
    echo "enabled=1" >> /etc/yum.repos.d/stx.repo &&\
    echo "gpgcheck=0" >> /etc/yum.repos.d/stx.repo

ENV DISTRO="centos"

CMD /usr/sbin/init