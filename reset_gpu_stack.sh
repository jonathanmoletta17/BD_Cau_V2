#!/bin/bash
#
# GPU Stack Reset Script
# Purpose: Safely reset AI inference stack to resolve VRAM contention
# Compatible with: NVIDIA RTX A4000 (16GB VRAM)
#
# Usage: ./reset_gpu_stack.sh [--force]
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/home/workbench/projects/BD_Cau_V2"
GPU_SERVICES=("nim-llm" "ollama")
CORE_SERVICES=("redis" "core-db")
BACKEND_SERVICES=("backend")

echo "================================================"
echo "🔧 GPU Stack Reset Script"
echo "================================================"
echo ""

# Function: Check if running as root (we don't need it)
check_root() {
    if [ "$EUID" -eq 0 ]; then
        echo -e "${RED}⚠️  Don't run as root. Run as regular user with docker permissions.${NC}"
        exit 1
    fi
}

# Function: Check Docker access
check_docker() {
    if ! docker ps &>/dev/null; then
        echo -e "${RED}❌ Cannot access Docker. Ensure user is in docker group.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker access confirmed${NC}"
}

# Function: Check NVIDIA GPU
check_gpu() {
    if ! command -v nvidia-smi &>/dev/null; then
        echo -e "${YELLOW}⚠️  nvidia-smi not found. GPU management unavailable.${NC}"
        return 1
    fi
    
    echo "📊 Current GPU Status:"
    nvidia-smi --query-gpu=index,name,memory.used,memory.total --format=csv,noheader,nounits
    echo ""
    return 0
}

# Function: Stop GPU services gracefully
stop_gpu_services() {
    echo "🛑 Stopping GPU inference services..."
    
    cd "$PROJECT_DIR"
    
    for service in "${GPU_SERVICES[@]}"; do
        if docker ps --format '{{.Names}}' | grep -q "^${service}$"; then
            echo "  Stopping ${service}..."
            docker compose stop "$service" --timeout 30
            echo -e "  ${GREEN}✓${NC} ${service} stopped"
        else
            echo "  ${service} not running (skipped)"
        fi
    done
    
    echo ""
}

# Function: Check for zombie GPU processes
check_gpu_zombies() {
    if ! command -v nvidia-smi &>/dev/null; then
        return 0
    fi
    
    echo "🔍 Checking for zombie GPU processes..."
    
    # Get PIDs using GPU
    GPU_PIDS=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null || true)
    
    if [ -z "$GPU_PIDS" ]; then
        echo -e "  ${GREEN}✓${NC} No GPU processes found"
        return 0
    fi
    
    echo "  Found GPU processes:"
    for pid in $GPU_PIDS; do
        if ps -p "$pid" &>/dev/null; then
            PROCESS_NAME=$(ps -p "$pid" -o comm=)
            echo "    PID $pid: $PROCESS_NAME"
        fi
    done
    
    # Don't kill automatically - just warn
    echo -e "  ${YELLOW}⚠️  GPU processes still running. They should clear after service stop.${NC}"
    echo "    If issues persist, manually kill with: kill <PID>"
    echo ""
}

# Function: Clean Docker GPU resources (safe)
clean_docker_gpu() {
    echo "🧹 Cleaning Docker GPU resources..."
    
    # Remove stopped GPU containers (safe - doesn't affect volumes)
    STOPPED_GPU=$(docker ps -a --filter "name=glpi-nim" --filter "name=ollama" --filter "status=exited" -q)
    
    if [ -n "$STOPPED_GPU" ]; then
        echo "  Removing stopped GPU containers..."
        docker rm $STOPPED_GPU
        echo -e "  ${GREEN}✓${NC} Cleaned stopped containers"
    else
        echo "  No stopped containers to clean"
    fi
    
    echo ""
}

# Function: Start stack in correct order
start_stack_ordered() {
    echo "🚀 Starting stack in correct order..."
    
    cd "$PROJECT_DIR"
    
    # Phase 1: Core infrastructure
    echo "  Phase 1: Starting core services (DB, Redis)..."
    for service in "${CORE_SERVICES[@]}"; do
        docker compose up -d "$service"
    done
    
    echo "  Waiting for core services to be healthy (15s)..."
    sleep 15
    
    # Phase 2: Backend
    echo "  Phase 2: Starting backend..."
    for service in "${BACKEND_SERVICES[@]}"; do
        docker compose up -d "$service"
    done
    
    echo "  Waiting for backend to initialize (10s)..."
    sleep 10
    
    # Phase 3: AI inference (GPU services)
    echo "  Phase 3: Starting AI inference services..."
    
    # Start Ollama first (lighter)
    if [[ " ${GPU_SERVICES[@]} " =~ " ollama " ]]; then
        echo "    Starting Ollama (fallback LLM)..."
        docker compose up -d ollama
        sleep 5
    fi
    
    # Start NIM last (heavier)
    if [[ " ${GPU_SERVICES[@]} " =~ " glpi-nim " ]]; then
        echo "    Starting NIM (primary LLM)..."
        docker compose up -d glpi-nim || {
            echo -e "    ${YELLOW}⚠️  NIM failed to start (expected if low VRAM)${NC}"
            echo "    Backend will use Ollama fallback"
        }
    fi
    
    echo ""
}

# Function: Wait and verify
verify_stack() {
    echo "🔍 Verifying stack health..."
    
    cd "$PROJECT_DIR"
    
    echo "  Waiting for services to stabilize (20s)..."
    sleep 20
    
    # Check backend health
    if curl -sf http://localhost:4000/health >/dev/null; then
        echo -e "  ${GREEN}✓${NC} Backend is healthy"
    else
        echo -e "  ${YELLOW}⚠️  Backend health check failed${NC}"
    fi
    
    # Check LLM status
    if curl -sf http://localhost:4000/llm-status >/dev/null; then
        echo -e "  ${GREEN}✓${NC} LLM service responding"
    else
        echo -e "  ${YELLOW}⚠️  LLM status unavailable${NC}"
    fi
    
    # Show container status
    echo ""
    echo "📊 Container Status:"
    docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    
    echo ""
}

# Function: Show GPU status
show_final_gpu_status() {
    if ! command -v nvidia-smi &>/dev/null; then
        return 0
    fi
    
    echo "📊 Final GPU Memory Usage:"
    nvidia-smi --query-gpu=index,name,memory.used,memory.total --format=csv,noheader
    echo ""
}

# Main execution
main() {
    echo "Starting GPU stack reset..."
    echo ""
    
    # Checks
    check_root
    check_docker
    check_gpu
    
    # Stop GPU services
    stop_gpu_services
    
    # Check for zombies
    check_gpu_zombies
    
    # Clean resources
    clean_docker_gpu
    
    # Wait for VRAM to clear
    echo "⏳ Waiting for GPU VRAM to clear (10s)..."
    sleep 10
    
    # Start in order
    start_stack_ordered
    
    # Verify
    verify_stack
    
    # Final GPU status
    show_final_gpu_status
    
    # Summary
    echo "================================================"
    echo -e "${GREEN}✅ GPU Stack Reset Complete!${NC}"
    echo "================================================"
    echo ""
    echo "Next steps:"
    echo "  1. Monitor logs: docker compose logs -f backend"
    echo "  2. Test endpoint: curl http://localhost:4000/health"
    echo "  3. Check LLM: curl http://localhost:4000/llm-status"
    echo ""
    
    # Show any ECONNREFUSED errors
    REDIS_ERRORS=$(docker logs glpi-backend 2>&1 | grep -c "ECONNREFUSED" || true)
    if [ "$REDIS_ERRORS" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Warning: Found ${REDIS_ERRORS} ECONNREFUSED errors${NC}"
        echo "    → Apply docker-compose.yml fixes (see docker_fixes.md)"
    else
        echo -e "${GREEN}✓${NC} No Redis connection errors detected"
    fi
}

# Run main function
main "$@"
