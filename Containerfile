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
        curl \
        gnupg \
        pkg-config \
        python3-dev \
        default-libmysqlclient-dev \
        build-essential \
        default-mysql-client \
    && \

    echo "## Installing clang" \
    && \
    
    curl -fsSL https://apt.llvm.org/llvm-snapshot.gpg.key | gpg --dearmor -o /etc/apt/keyrings/llvm.gpg \
    && \

    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/llvm.gpg] http://apt.llvm.org/jammy/ llvm-toolchain-jammy main" | tee /etc/apt/sources.list.d/llvm.list > /dev/nul \
    && \

    apt-get update -y \
    && \

    apt-get install -y \
        clang-19 \
    && \
        
    echo "## Installing python packages" \
    && \
    
    pip install --upgrade pip \
    && \
    
    pip install -r requirements.txt




CMD ["bash"]
