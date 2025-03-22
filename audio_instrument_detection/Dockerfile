ARG FUNCTION_DIR="/function"

FROM ubuntu:22.04 AS essentia-build
# Stop interative inputs when installing
ENV DEBIAN_FRONTEND=noninteractive 

# Install required dependencies
RUN apt-get update && apt-get install -y build-essential libeigen3-dev libyaml-dev libfftw3-dev libavcodec-dev libavformat-dev libavutil-dev libswresample-dev libsamplerate0-dev libtag1-dev libchromaprint-dev git pip wget
RUN apt-get install -y python3-dev python3-numpy python3-yaml python3-six
RUN pip install numpy==1.26.4

# Install tensorflow
# RUN python3 -m pip install --upgrade pip setuptools \
#     && pip3 install --no-cache-dir tensorflow==2.18.0

# Clone and compile repo from last verified commit before dev1177 release date
RUN mkdir -p /usr/local/lib/pkgconfig && git clone https://github.com/MTG/essentia.git
WORKDIR /essentia
RUN git checkout 1d1cc983e9b30a040b0563184344950effc532b4 
# Run the tensorflow setup directly from python file with libtensorflow flag
RUN python3 src/3rdparty/tensorflow/setup_tensorflow.py -m libtensorflow -c /usr/local/
# PC defined in issue: https://github.com/MTG/essentia-docker/pull/7#discussion_r380782792
RUN echo "Requires: python3" >> /usr/local/lib/pkgconfig/tensorflow.pc && ldconfig
# Configure and build essentia
RUN python3 waf configure --build-static --with-python --with-examples --with-vamp --with-tensorflow 
RUN python3 waf && python3 waf install




FROM ubuntu:22.04

ARG FUNCTION_DIR
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3 python3-yaml python3-six pip \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p ${FUNCTION_DIR}
COPY . ${FUNCTION_DIR}
COPY custom_bin ${FUNCTION_DIR}/bin

ENV PATH="${FUNCTION_DIR}/bin:${PATH}"


# Install the function's dependencies
RUN pip install \
    --target ${FUNCTION_DIR} \
        awslambdaric

# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Copy in the built dependencies
COPY --from=essentia-build /usr/local/ /usr/local/
COPY --from=essentia-build /usr/lib/x86_64-linux-gnu/ /usr/lib/x86_64-linux-gnu/

# Update path for python to find library - must use ENV to have it for all containers
ENV PYTHONPATH=/usr/local/lib/python3/dist-packages:$PYTHONPATH
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

RUN pip install -r requirements.txt


# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "/usr/bin/python3", "-m", "awslambdaric" ]
# Pass the name of the function handler as an argument to the runtime
CMD [ "lambda_function.handler" ]
# Define custom function directory

