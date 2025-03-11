FROM public.ecr.aws/lambda/python:3.9

# Custom binaries for ffmepg and ffprobe
# Set the working directory inside the container


WORKDIR /var/task
COPY custom_bin /var/task/custom_bins
# Ensure the custom binaries have executable permissions
RUN chmod -R +x /var/task/custom_bins
# Add the custom_bins folder to the PATH environment variable
ENV PATH="/var/task/custom_bins:$PATH"

ENV NUMBA_CACHE_DIR="/tmp"

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.lambda_handler" ]