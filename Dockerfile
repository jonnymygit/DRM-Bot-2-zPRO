# Use a modern, supported base image
FROM python:3.9-slim-bullseye

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install system dependencies (clean + combined)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        cmake \
        aria2 \
        wget \
        pv \
        jq \
        python3-dev \
        ffmpeg \
        mediainfo && \
    rm -rf /var/lib/apt/lists/*

# Build Bento4 from source
RUN git clone https://github.com/axiomatic-systems/Bento4.git /tmp/Bento4 && \
    mkdir /tmp/Bento4/cmakebuild && \
    cd /tmp/Bento4/cmakebuild && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make -j$(nproc) && \
    make install && \
    rm -rf /tmp/Bento4

# Install Python requirements
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Start the bot
CMD ["sh", "start.sh"]
