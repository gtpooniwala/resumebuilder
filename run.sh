#!/bin/bash

# Resume Builder App - Run Script

echo "🚀 Starting Resume Builder App..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Function to handle cleanup
cleanup() {
    echo "🧹 Cleaning up..."
    docker-compose down
    exit 0
}

# Set up trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Build and start all services
echo "🔨 Building and starting all services..."
docker-compose up --build

echo "✅ Resume Builder App is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   Database: localhost:5432"
echo ""
echo "Press Ctrl+C to stop all services."

# Keep the script running
wait
