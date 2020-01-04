FROM centos:7

ENV DISTRO="centos"
RUN rm /etc/yum.repos.d/*
COPY yum.repos.d/* /etc/yum.repos.d/
RUN sed -i 's/keepcache=0/keepcache=1/' /etc/yum.conf && \
    yum clean all && \
    yum update -y && \
    yum install -y git rpm-build rpm-sign make createrepo wget bzip2 sudo gcc

# Install repo tool
RUN curl https://storage.googleapis.com/git-repo-downloads/repo > /usr/bin/repo && \
    chmod a+x /usr/bin/repo
ENV REPO_URL='https://aosp.tuna.tsinghua.edu.cn/git-repo'

CMD /usr/sbin/init