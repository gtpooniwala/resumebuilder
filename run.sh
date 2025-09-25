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
#!/bin/bash

# Resume Builder Development Script

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
COMMAND=${1:-"up"}

case $COMMAND in
    "up")
        print_status "Starting Resume Builder application..."
        # Use --build only if images don't exist or --force-build is passed
        if [[ "$2" == "--force-build" ]] || ! docker images | grep -q "resumebuilder"; then
            print_status "Building images..."
            docker-compose up --build
        else
            print_status "Using cached images (use --force-build to rebuild)..."
            docker-compose up
        fi
    ;;
    "build")
        print_status "Building all images..."
        docker-compose build --parallel
    ;;
    "down")
        print_status "Stopping and removing containers..."
        docker-compose down
    ;;
    "clean")
        print_warning "Cleaning up all containers, images, and volumes..."
        docker-compose down -v
        docker system prune -f
        docker volume prune -f
    ;;
    "logs")
        SERVICE=${2:-""}
        if [[ -n "$SERVICE" ]]; then
            print_status "Showing logs for $SERVICE..."
            docker-compose logs -f "$SERVICE"
        else
            print_status "Showing logs for all services..."
            docker-compose logs -f
        fi
    ;;
    "restart")
        SERVICE=${2:-""}
        if [[ -n "$SERVICE" ]]; then
            print_status "Restarting $SERVICE..."
            docker-compose restart "$SERVICE"
        else
            print_status "Restarting all services..."
            docker-compose restart
        fi
    ;;
    "status")
        print_status "Checking service status..."
        docker-compose ps
    ;;
    "help")
        echo "Resume Builder Development Script"
        echo ""
        echo "Usage: $0 [COMMAND] [OPTIONS]"
        echo ""
        echo "Commands:"
        echo "  up [--force-build]  Start the application (default)"
        echo "  build              Build all images in parallel"
        echo "  down               Stop and remove containers"
        echo "  clean              Remove containers, images, and volumes"
        echo "  logs [service]     Show logs (optionally for specific service)"
        echo "  restart [service]  Restart services (optionally specific service)"
        echo "  status             Show container status"
        echo "  help               Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0                    # Start with cached images"
        echo "  $0 up --force-build   # Start and rebuild images"
        echo "  $0 logs frontend      # Show frontend logs"
        echo "  $0 restart backend    # Restart only backend"
    ;;
    *)
        print_error "Unknown command: $COMMAND"
        print_status "Use '$0 help' for available commands"
        exit 1
    ;;
esac

echo "✅ Resume Builder App is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   Database: localhost:5432"
echo ""
echo "Press Ctrl+C to stop all services."

# Keep the script running
wait
