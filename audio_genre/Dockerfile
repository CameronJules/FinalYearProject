FROM public.ecr.aws/lambda/python:3.9

# --- Install pre-requisite dev packages ---
RUN yum install -y \
    wget \
    gcc \
    gcc-c++ \
    make \
    automake \
    autoconf \
    libtool \
    patch \
    cmake \
    git \
    pkgconf \
    pkgconf-pkg-config

# --- Install everything needed to compile essentia ---
RUN wget https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz \
    && tar -xzf eigen-3.4.0.tar.gz \
    && cd eigen-3.4.0 \
    && mkdir build_dir \
    && cd build_dir \
    && cmake .. \
    && make install

RUN git clone https://github.com/MTG/essentia.git \
    && cd essentia \
    && python3 waf configure --build-static --with-python --with-cpptests --with-examples --with-vamp --with-tensorflow\
    && python3 waf build \
    && python3 waf install

# RUN git clone https://gitlab.com/libeigen/eigen.git
# RUN pip install https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz
# RUN pip install http://www.mega-nerd.com/SRC/libsamplerate-0.1.9.tar.gz


# Custom binaries for ffmepg and ffprobe
# Set the working directory inside the container
WORKDIR /var/task
COPY custom_bin /var/task/custom_bins
# Ensure the custom binaries have executable permissions
RUN chmod -R +x /var/task/custom_bins
# Add the custom_bins folder to the PATH environment variable
ENV PATH="/var/task/custom_bins:$PATH"

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.lambda_handler" ]


# # ENV PKG_CONFIG_PATH=/usr/local/include
# RUN wget https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz \
#     && tar -xzf eigen-3.4.0.tar.gz \
#     && echo eigen-3.4.0 \
#     && mv eigen-3.4.0 /usr/local/include/eigen  \
#     && rm -rf eigen-3.4.0*


# Clone and build Essentia using waf
# RUN git clone https://github.com/MTG/essentia.git /opt/essentia \
#     && cd /opt/essentia \
#     && python3 waf configure --build-static --with-python --with-cpptests --with-examples --with-vamp --with-tensorflow\
#     && python3 waf build \
#     && python3 waf install
