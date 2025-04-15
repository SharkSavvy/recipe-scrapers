FROM apify/actor-node:16

# Install Python and required build dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    python3-dev \
    libxml2-dev \
    libxslt-dev \
    gcc \
    musl-dev

WORKDIR /usr/src/app

# Copy package files and install Node dependencies
COPY package*.json ./
RUN npm install --production

# Install Python packages in correct order
RUN pip3 install --no-cache-dir \
    lxml==4.9.3 \
    extruct==0.16.0 \
    beautifulsoup4==4.12.3 \
    isodate==0.6.1 \
    recipe-scrapers==13.3.5

# Copy source code
COPY . .

CMD ["npm", "start"]
