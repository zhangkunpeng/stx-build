FROM centos:7.4.1708

RUN yum install -y git wget sudo
RUN git clone https://opendev.org/starlingx/tools.git --depth 1 --branch master&&\
    cd tools/centos-mirror-tools/ &&\
    bash download_mirror.sh
