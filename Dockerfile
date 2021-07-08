FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
  apt-get install -y \
  build-essential \
  ca-certificates \
  cmake \
  ethtool \
  g++ \
  git \
  gdb-multiarch \
  libpixman-1-dev \
  python3-pip \
  python3-venv \
  python-tk \
  tcpdump \
  vim \
  wget && \
  apt-get clean && \
  apt-get autoclean -y && \
  rm -rf /var/lib/apt/lists/*

ARG INSTALL_CERTS=
RUN ["/bin/bash", "-c", "if [ -n $INSTALL_CERTS ]; then \
  IFS=',' read -r -a arr <<< $INSTALL_CERTS; \
  for i in ${!arr[@]}; do \
    wget ${arr[$i]} -e use_proxy=no \
      -O /usr/local/share/ca-certificates/custom$i.crt; \
  done && \
  update-ca-certificates; fi"]

WORKDIR /root
ADD . ./halucinator
RUN mkdir -p ./halucinator/deps
WORKDIR /root/halucinator/deps/avatar2
RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org -e ./

WORKDIR /root/halucinator/deps/avatar2/targets
RUN bash -c "sed -i -e 's/sudo //g' build_qemu.sh && echo 'Yes' | ./build_qemu.sh"

WORKDIR /root/halucinator
RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r src/requirements.txt
RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org -e src
ENV HALUCINATOR_QEMU_ARM /root/halucinator/deps/avatar2/targets/build/qemu/arm-softmmu/qemu-system-arm
ENV HALUCINATOR_QEMU_ARM64 /root/halucinator/deps/avatar2/targets/build/qemu/aarch64-softmmu/qemu-system-aarch64
RUN echo "export HALUCINATOR_QEMU_ARM=/root/halucinator/deps/avatar2/targets/build/qemu/arm-softmmu/qemu-system-arm\nexport HALUCINATOR_QEMU_ARM64=/root/halucinator/deps/avatar2/targets/build/qemu/aarch64-softmmu/qemu-system-aarch64" >> /root/.profile
RUN ln -s -T /usr/bin/gdb-multiarch /usr/bin/arm-none-eabi-gdb

# # Now set up the vxworks and firmware folders

CMD /root/halucinator
