FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget gnupg unzip xvfb libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libgbm1 libxss1 libasound2 fonts-liberation libcups2 libxcomposite1 libxdamage1 libxrandr2 libxfixes3 libxtst6 libxi6 libx11-xcb1 libx11-6 libxcb1 libxext6 libxrender1 libcairo2 libglib2.0-0 libgtk-3-0 libgdk-pixbuf2.0-0 libpango-1.0-0 libpangocairo-1.0-0 libatk1.0-0 libcairo-gobject2 libxshmfence1 libgl1-mesa-glx libgl1-mesa-dri libegl1-mesa libxau6 libxdmcp6 libappindicator3-1 xdg-utils ca-certificates libcurl3-gnutls \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Download and extract Orbita browser (matching GoLogin's BrowserManager method)
RUN mkdir -p /root/.gologin/browser && \
    MAJOR_VERSION=135 && \
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
ENV LIBGL_ALWAYS_SOFTWARE=1
ENV MESA_GL_VERSION_OVERRIDE=3.3
ENV GALLIUM_DRIVER=llvmpipe

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY src /app/src

# Create a script to start Xvfb and run the application
# RUN echo '#!/bin/bash\n\
# Xvfb :99 -screen 0 ${SCREEN_WIDTH}x${SCREEN_HEIGHT}x${SCREEN_DEPTH} &\n\
# sleep 2\n\
# python src/index.py' > /app/start.sh && \
# chmod +x /app/start.sh

# Run the script
# CMD ["/app/start.sh"]
CMD ["python" ,"/app/src/index.py"]
