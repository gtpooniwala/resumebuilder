# Use Node.js Alpine for smaller image size
FROM node:18-alpine

# Install dependencies for better compatibility
RUN apk add --no-cache libc6-compat

# Set the working directory
WORKDIR /app

# Copy package files first for better Docker layer caching
COPY package.json package-lock.json* ./

# Install dependencies
# Use npm install with --frozen-lockfile for consistency but without strict ci requirements
RUN npm install --frozen-lockfile && npm cache clean --force

# Copy the application code
COPY . .

# Create .next directory
RUN mkdir -p .next

# Note: Running as root for development simplicity
# In production, you should create and use a non-root user

# Expose the port
EXPOSE 3000

# Set environment variable
ENV NODE_ENV=development

# Command to run the application in development mode
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]
