#!/bin/bash

# Crypto Trading Bot Deployment Script
# Usage: ./deploy.sh [environment] [action]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${1:-production}
ACTION=${2:-deploy}
IMAGE_TAG=${3:-latest}

# Configuration
DOCKER_REGISTRY="ghcr.io"
REPOSITORY_NAME="your-username/crypto-trading"
FULL_IMAGE_NAME="${DOCKER_REGISTRY}/${REPOSITORY_NAME}:${IMAGE_TAG}"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking requirements..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        log_error ".env file not found. Please create it from env.example"
        exit 1
    fi
    
    log_success "Requirements check passed"
}

pull_latest_image() {
    log_info "Pulling latest Docker image..."
    docker pull "${FULL_IMAGE_NAME}" || {
        log_warning "Could not pull image. Building locally..."
        docker build -t "${FULL_IMAGE_NAME}" .
    }
    log_success "Image ready"
}

deploy() {
    log_info "Deploying to ${ENVIRONMENT} environment..."
    
    # Stop existing containers
    log_info "Stopping existing containers..."
    docker-compose down || true
    
    # Pull latest image
    pull_latest_image
    
    # Start services
    log_info "Starting services..."
    docker-compose up -d
    
    # Wait for health check
    log_info "Waiting for health check..."
    sleep 30
    
    # Check if container is running
    if docker-compose ps | grep -q "Up"; then
        log_success "Deployment completed successfully!"
        log_info "Container status:"
        docker-compose ps
    else
        log_error "Deployment failed. Container is not running."
        docker-compose logs
        exit 1
    fi
}

stop() {
    log_info "Stopping services..."
    docker-compose down
    log_success "Services stopped"
}

restart() {
    log_info "Restarting services..."
    docker-compose restart
    log_success "Services restarted"
}

logs() {
    log_info "Showing logs..."
    docker-compose logs -f
}

status() {
    log_info "Checking service status..."
    docker-compose ps
}

update() {
    log_info "Updating to latest version..."
    git pull origin main
    deploy
}

backup() {
    log_info "Creating backup..."
    BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "${BACKUP_DIR}"
    
    # Backup logs
    if [ -d "logs" ]; then
        cp -r logs "${BACKUP_DIR}/"
    fi
    
    # Backup .env
    cp .env "${BACKUP_DIR}/"
    
    log_success "Backup created in ${BACKUP_DIR}"
}

cleanup() {
    log_info "Cleaning up old images and containers..."
    
    # Remove stopped containers
    docker container prune -f
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    log_success "Cleanup completed"
}

show_help() {
    echo "Crypto Trading Bot Deployment Script"
    echo ""
    echo "Usage: $0 [environment] [action] [image_tag]"
    echo ""
    echo "Environments:"
    echo "  production  - Deploy to production (default)"
    echo "  staging     - Deploy to staging"
    echo ""
    echo "Actions:"
    echo "  deploy      - Deploy the application (default)"
    echo "  stop        - Stop all services"
    echo "  restart     - Restart all services"
    echo "  logs        - Show logs"
    echo "  status      - Show service status"
    echo "  update      - Pull latest code and deploy"
    echo "  backup      - Create backup of logs and config"
    echo "  cleanup     - Clean up old Docker resources"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Deploy to production"
    echo "  $0 staging deploy     # Deploy to staging"
    echo "  $0 production logs    # Show production logs"
    echo "  $0 production update  # Update and deploy"
}

# Main script
case $ACTION in
    deploy)
        check_requirements
        deploy
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    status)
        status
        ;;
    update)
        check_requirements
        update
        ;;
    backup)
        backup
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown action: $ACTION"
        show_help
        exit 1
        ;;
esac 