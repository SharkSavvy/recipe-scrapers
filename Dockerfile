FROM apify/actor-node:16

# Install Python using Alpine package manager
RUN apk add --no-cache python3 py3-pip

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
