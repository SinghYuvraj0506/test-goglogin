FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    curl \
    unzip \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libglib2.0-0 \
    libdbus-1-3 \
    libdrm2 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libgtk-3-0 \
    libcurl3-gnutls \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Download and extract Orbita browser (matching GoLogin's BrowserManager method)
RUN mkdir -p /root/.gologin/browser && \
    MAJOR_VERSION=137 && \
    curl -L -o /root/.gologin/browser/orbita-browser-temp.tar.gz https://orbita-browser-linux.gologin.com/orbita-browser-latest-${MAJOR_VERSION}.tar.gz && \
    mkdir -p /root/.gologin/browser/temp-extract-${MAJOR_VERSION} && \
    tar -xzf /root/.gologin/browser/orbita-browser-temp.tar.gz -C /root/.gologin/browser/temp-extract-${MAJOR_VERSION} && \
    mkdir -p /root/.gologin/browser/orbita-browser-${MAJOR_VERSION} && \
    SUBFOLDER=$(ls /root/.gologin/browser/temp-extract-${MAJOR_VERSION} | head -1) && \
    mv /root/.gologin/browser/temp-extract-${MAJOR_VERSION}/${SUBFOLDER}/* /root/.gologin/browser/orbita-browser-${MAJOR_VERSION}/ && \
    rm -rf /root/.gologin/browser/temp-extract-${MAJOR_VERSION} && \
    rm /root/.gologin/browser/orbita-browser-temp.tar.gz && \
    find /root/.gologin/browser/orbita-browser-${MAJOR_VERSION} -name "chrome" -type f -exec chmod +x {} \; && \
    find /root/.gologin/browser/orbita-browser-${MAJOR_VERSION} -name "orbita" -type f -exec chmod +x {} \;

# Set environment variables to match the expected paths
ENV ORBITA_PATH=/root/.gologin/browser/orbita-browser-137
ENV CHROME_PATH=/root/.gologin/browser/orbita-browser-137/chrome
ENV DISPLAY=:99
ENV SCREEN_WIDTH=1920
ENV SCREEN_HEIGHT=1080
ENV SCREEN_DEPTH=24

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY src /app/src

# Create a script to start Xvfb and run the application
RUN echo '#!/bin/bash\n\
Xvfb :99 -screen 0 ${SCREEN_WIDTH}x${SCREEN_HEIGHT}x${SCREEN_DEPTH} &\n\
sleep 2\n\
python src/test.py' > /app/start.sh && \
chmod +x /app/start.sh

# RUN echo '#!/bin/bash\n\
# python src/test.py' > /app/start.sh && \
# chmod +x /app/start.sh

# Run the script
CMD ["/app/start.sh"]
