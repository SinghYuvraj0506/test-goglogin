FROM python:3.11-slim

# Install system dependencies needed for GoLogin and AppImage
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    libfuse2 \
    xvfb \
    libgtk-3-0 \
    libgconf-2-4 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libxtst6 \
    libatspi2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo-gobject2 \
    fonts-liberation \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libcurl3-gnutls \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Download and extract GoLogin
# RUN curl -L -o gologin.tar https://dld.gologin.com/gologin.tar && \
#     mkdir -p /opt/gologin && \
#     tar -xf gologin.tar -C /opt/gologin && \
#     find /opt/gologin -type f -executable -exec chmod +x {} \; && \
#     rm gologin.tar

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
ENV DISPLAY=:99
ENV CHROME_PATH=/root/.gologin/browser/orbita-browser-137/chrome

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY src /app/src

# Create a script to start Xvfb and run the application
RUN echo '#!/bin/bash\n\
Xvfb :99 -screen 0 1920x1080x24 &\n\
sleep 2\n\
python src/index.py' > /app/start.sh && \
chmod +x /app/start.sh

# Run the script
CMD ["/app/start.sh"]