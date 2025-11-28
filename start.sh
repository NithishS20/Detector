#!/bin/bash

# 🚀 Quick Start Script for Anomaly Detection System
# This script automates the setup and deployment of the complete system

set -e  # Exit on error

echo "=================================================="
echo "🔐 AI-Based Intrusion & Anomaly Detection System"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
print_info "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

print_success "Docker is installed"

# Check Docker permissions
if ! docker ps &> /dev/null; then
    print_warning "Docker permission denied. Trying with sudo..."
    if ! sudo docker ps &> /dev/null; then
        print_error "Cannot access Docker. Please add your user to the docker group:"
        echo "  sudo usermod -aG docker \$USER"
        echo "  newgrp docker"
        echo "Or run this script with sudo: sudo ./start.sh"
        exit 1
    fi
    DOCKER_CMD="sudo docker"
    COMPOSE_CMD="sudo docker compose"
    print_info "Using sudo for Docker commands"
else
    DOCKER_CMD="docker"
    COMPOSE_CMD="docker compose"
    print_success "Docker permissions OK"
fi

# Check if .env exists
if [ ! -f .env ]; then
    print_info "Creating .env file from .env.example..."
    cp .env.example .env
    
    # Generate a random secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32)
    
    # Update SECRET_KEY in .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|your-super-secret-key-change-this-in-production-min-32-chars|$SECRET_KEY|g" .env
    else
        # Linux
        sed -i "s|your-super-secret-key-change-this-in-production-min-32-chars|$SECRET_KEY|g" .env
    fi
    
    print_success "Created .env file with generated SECRET_KEY"
else
    print_info ".env file already exists"
fi

# Clean up old containers and volumes
print_info "Cleaning up old containers..."
$COMPOSE_CMD down -v 2>/dev/null || true

# Build and start services
print_info "Building Docker images (this may take a few minutes)..."
$COMPOSE_CMD build --no-cache

print_success "Docker images built successfully"

print_info "Starting all services..."
$COMPOSE_CMD up -d

# Wait for services to be healthy
print_info "Waiting for services to be ready..."
sleep 10

# Check service health
print_info "Checking service health..."

check_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            print_success "$service is healthy"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service failed to start"
    return 1
}

check_service "PostgreSQL" "http://localhost:5432" || true
check_service "Backend API" "http://localhost:8000/health"
check_service "ML Service" "http://localhost:8001/health"
check_service "Frontend" "http://localhost:3000/health"

# Train ML model
print_info "Training ML model..."
if curl -X POST http://localhost:8001/train -s > /dev/null 2>&1; then
    print_success "ML model trained successfully"
else
    print_warning "ML model training failed. You can train it later with: curl -X POST http://localhost:8001/train"
fi

# Display service URLs
echo ""
echo "=================================================="
print_success "🎉 System is ready!"
echo "=================================================="
echo ""
echo "📍 Service URLs:"
echo "   Frontend Dashboard:  http://localhost:3000"
echo "   Backend API:         http://localhost:8000"
echo "   API Documentation:   http://localhost:8000/docs"
echo "   ML Service:          http://localhost:8001"
echo "   PostgreSQL:          localhost:5432"
echo ""
echo "🔑 Demo Credentials:"
echo "   Email:    admin@example.com"
echo "   Password: password123"
echo ""
echo "🧪 Test Biometrics Demo:"
echo "   cd biometrics-sdk"
echo "   python3 -m http.server 8080"
echo "   Open: http://localhost:8080/demo.html"
echo ""
echo "📊 View Logs:"
if [ "$DOCKER_CMD" = "sudo docker" ]; then
    echo "   sudo docker compose logs -f"
else
    echo "   docker compose logs -f"
fi
echo ""
echo "🛑 Stop System:"
if [ "$DOCKER_CMD" = "sudo docker" ]; then
    echo "   sudo docker compose down"
else
    echo "   docker compose down"
fi
echo ""
echo "📚 Documentation:"
echo "   - README.md"
echo "   - ARCHITECTURE.md"
echo "   - DEPLOYMENT.md"
echo "   - INTEGRATION_EXAMPLE.md"
echo "   - PROJECT_SUMMARY.md"
echo ""
print_success "Happy detecting! 🔍"
