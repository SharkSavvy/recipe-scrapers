FROM apify/actor-node-python:16

WORKDIR /usr/src/app

# Copy package files and install Node dependencies
COPY package*.json ./
RUN npm ci --only=production

# Install Python package with version pinning
RUN pip install --no-cache-dir recipe-scrapers==13.3.5

# Copy source code
COPY . .

# Run npm start by default
CMD ["npm", "start"]
