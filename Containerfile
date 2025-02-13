# get python image
FROM python:3.13.1-slim-bookworm

# working directory
WORKDIR /app

# set timezone
ENV TZ Asia/Tokyo

# copy initial module/package files.
COPY requirements.txt $WORKDIR
COPY package.json $WORKDIR

# install packages
RUN apt-get update -y \
    && \

    apt-get upgrade -y \
    && \

    echo "## Installing packages" \
    && \
    
    apt-get install -y \
        pkg-config \
        build-essential \
        default-libmysqlclient-dev \
        default-mysql-client \
        clang-14 \
        python3-clang-14 \
        npm \
    && \

    echo "## Installing python packages" \
    && \
    
    pip install --upgrade pip \
    && \
    
    pip install -r requirements.txt \
    && \

    npm --verbose install

CMD ["bash"]
