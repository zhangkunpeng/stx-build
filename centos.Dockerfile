FROM centos:7.4.1708

ENV STXREPO=https://opendev.org/starlingx/fault.git

RUN yum install -y epel-release git rpm-build rpm-sign make gcc gcc-c++ && \
    yum install -y postgresql-devel \
    libuuid-devel \
    python-devel \
    python-setuptools \
    python2-pip \
    python2-wheel &&\
    pip install --upgrade pip

WORKDIR /workspace

COPY . ./stx-build

RUN cd ./stx-build && pip install -r requirements.txt && python setup.py install

ENV DISTRO="centos"

CMD /usr/sbin/init