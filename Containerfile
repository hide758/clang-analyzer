# get python image
FROM python:3.13.1-slim-bookworm

# working directory
WORKDIR /app

# set timezone
ENV TZ Asia/Tokyo

# copy requirements.txt
COPY requirements.txt $WORKDIR

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
    && \

    echo "## Installing python packages" \
    && \
    
    pip install --upgrade pip \
    && \
    
    pip install -r requirements.txt

CMD ["bash"]
