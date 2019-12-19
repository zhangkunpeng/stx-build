FROM centos:7.4.1708

RUN yum install -y epel-release git rpm-build rpm-sign make gcc gcc-c++ && \
    yum install -y postgresql-devel \
    libuuid-devel \
    python-devel \
    python-setuptools \
    python2-pip \
    python2-wheel &&\
    pip install --upgrade pip 

WORKDIR /workspace

COPY stx-build ./stx-build

RUN cd ./stx-build && pip install -r requirements.txt && python setup.py install && rm -rf /workspace/stx-build

ENV DISTRO="centos"

CMD /usr/sbin/init