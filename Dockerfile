FROM apify/actor-node:16

# Install Python using Alpine package manager
RUN apk add --no-cache python3 py3-pip gcc musl-dev python3-dev

WORKDIR /usr/src/app

# Copy package files and install Node dependencies
COPY package*.json ./
RUN npm install --production

# Install Python packages properly
RUN pip3 install --no-cache-dir \
    beautifulsoup4==4.12.3 \
    extruct==0.16.0 \
    isodate==0.6.1 \
    recipe-scrapers==13.3.5

# Copy source code
COPY . .

CMD ["npm", "start"]
