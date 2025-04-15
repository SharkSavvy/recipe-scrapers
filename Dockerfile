FROM apify/actor-node:16

# Install Python
RUN apt-get update && apt-get install -y python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Copy package files and install Node dependencies
COPY package*.json ./
RUN npm ci --only=production

# Install Python package with version pinning
RUN pip3 install --no-cache-dir recipe-scrapers==13.3.5

# Copy source code
COPY . .

# Run npm start by default
CMD ["npm", "start"]
