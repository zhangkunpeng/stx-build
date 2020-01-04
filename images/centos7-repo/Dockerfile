FROM centos:7

ENV DISTRO="centos"
RUN yum install -y epel-release git rpm-build rpm-sign make createrepo wget bzip2 sudo && \
    yum install -y python2-pip && \
    pip install --upgrade pip 

# Install repo tool
RUN curl https://storage.googleapis.com/git-repo-downloads/repo > /usr/bin/repo && \
    chmod a+x /usr/bin/repo
ENV REPO_URL='https://aosp.tuna.tsinghua.edu.cn/git-repo'

# Customizations for mirror creation
RUN rm /etc/yum.repos.d/CentOS-Sources.repo
RUN rm /etc/yum.repos.d/epel.repo
COPY yum.repos.d/* /etc/yum.repos.d/
COPY rpm-gpg-keys/* /etc/pki/rpm-gpg/

# Import GPG keys
RUN rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY*

# Try to continue a yum command even if a StarlingX repo is unavailable.
RUN yum-config-manager --setopt=StarlingX\*.skip_if_unavailable=1 --save

CMD /usr/sbin/init