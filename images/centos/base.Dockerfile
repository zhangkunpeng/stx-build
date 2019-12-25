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

# Install repo tool
RUN curl https://storage.googleapis.com/git-repo-downloads/repo > /usr/bin/repo && \
    chmod a+x /usr/bin/repo
ENV REPO_URL='https://aosp.tuna.tsinghua.edu.cn/git-repo'

CMD /usr/sbin/init