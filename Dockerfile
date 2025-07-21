FROM ubuntu:22.04

# Đặt environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV DOCKER_ENV=true
ENV DISPLAY=:1
ENV PYTHONUNBUFFERED=1

# Cài đặt các packages cần thiết
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    curl wget gnupg2 software-properties-common \
    libnss3 libgconf-2-4 libx11-xcb1 libxss1 libasound2 \
    fonts-liberation libappindicator3-1 libatk-bridge2.0-0 libgtk-3-0 \
    xvfb x11vnc fluxbox \
    dbus-x11 \
    libnss3-dev \
    libxrandr2 \
    libasound2-dev \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Cài uv trực tiếp bằng pip
RUN pip install uv

# Cài đặt Microsoft Edge
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg && \
    install -o root -g root -m 644 microsoft.gpg /etc/apt/trusted.gpg.d/ && \
    sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge.list' && \
    apt-get update && \
    apt-get install -y microsoft-edge-stable && \
    rm -rf /var/lib/apt/lists/*

# Tạo các thư mục cần thiết với permissions phù hợp
RUN mkdir -p /tmp/edge_profiles && \
    chmod 777 /tmp/edge_profiles && \
    mkdir -p /app/profiles && \
    chmod 777 /app/profiles && \
    mkdir -p /root/.config && \
    chmod 777 /root/.config

# Tạo Xauthority file
RUN touch /root/.Xauthority && chmod 600 /root/.Xauthority

# Entrypoint script để khởi động Xvfb và Fluxbox
RUN echo '#!/bin/bash\n\
Xvfb :1 -screen 0 1920x1080x24 &\n\
export DISPLAY=:1\n\
sleep 2\n\
fluxbox &\n\
sleep 2\n\
exec "$@"' > /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

WORKDIR /app

# Copy và install dependencies
COPY pyproject.toml ./
RUN uv pip install --system --no-cache-dir -r pyproject.toml

# Copy source code
COPY . /app

# Expose port
EXPOSE 50051

# Use entrypoint script
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Start command
CMD ["python3", "./test_grpc_server.py"]
