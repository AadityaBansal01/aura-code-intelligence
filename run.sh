#!/usr/bin/env bash
# ==============================================================================
# AURA-Code Intelligence Platform Runner
# Samsung PRISM GenAI Hackathon 3.0 (Theme 01: Agentic Code Intelligence)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
cat << "EOF"
   █████╗ ██╗   ██╗██████╗  █████╗       ██████╗ ██████╗ ██████╗ ███████╗
  ██╔══██╗██║   ██║██╔══██╗██╔══██╗     ██╔════╝██╔═══██╗██╔══██╗██╔════╝
  ███████║██║   ██║██████╔╝███████║     ██║     ██║   ██║██║  ██║█████╗  
  ██╔══██║██║   ██║██╔══██╗██╔══██║     ██║     ██║   ██║██║  ██║██╔══╝  
  ██║  ██║╚██████╔╝██║  ██║██║  ██║     ╚██████╗╚██████╔╝██████╔╝███████╗
  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝      ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
EOF
echo -e "   Samsung PRISM GenAI Hackathon 3.0 | Theme 01: Agentic Code Intelligence${NC}\n"

# Verify Python Environment
if [ -d ".venv" ]; then
    PYTHON_BIN=".venv/bin/python"
    PYTEST_BIN=".venv/bin/pytest"
    UVICORN_BIN=".venv/bin/uvicorn"
elif command -v python3 &>/dev/null; then
    PYTHON_BIN="python3"
    PYTEST_BIN="pytest"
    UVICORN_BIN="uvicorn"
else
    echo -e "${RED}[!] Error: Python 3 is required but not found.${NC}"
    exit 1
fi

export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Mode dispatch
MODE="${1:-server}"

case "$MODE" in
    test|tests)
        echo -e "${GREEN}[+] Running Automated Engine Test Suite...${NC}"
        "$PYTEST_BIN" tests/ -v
        ;;
    cli|search)
        shift
        QUERY="${*:-which files call tool requestPermissions before tool launchDeeplink}"
        echo -e "${GREEN}[+] Executing CLI Query:${NC} \"$QUERY\""
        "$PYTHON_BIN" cli/aura.py search "$QUERY"
        ;;
    benchmark)
        echo -e "${GREEN}[+] Running Official 15-Query Evaluation Benchmark...${NC}"
        "$PYTHON_BIN" cli/aura.py benchmark
        ;;
    docker)
        echo -e "${GREEN}[+] Launching Container via Docker Compose...${NC}"
        docker compose up --build
        ;;
    server|ui|*)
        echo -e "${GREEN}[+] Verifying Engine Health & Running Pre-flight Tests...${NC}"
        "$PYTEST_BIN" tests/ -q
        echo -e "${GREEN}[✓] Test Suite Passed (18/18 checks).${NC}\n"
        echo -e "${CYAN}[*] Starting AURA-Code API & Dashboard at http://localhost:8000${NC}"
        echo -e "${YELLOW}[*] Interactive Web Dashboard: http://localhost:8000${NC}"
        echo -e "${YELLOW}[*] Swagger API Documentation: http://localhost:8000/docs${NC}\n"
        echo -e "Press Ctrl+C to terminate the server.\n"
        exec "$UVICORN_BIN" engine.server:app --host 0.0.0.0 --port 8000 --reload
        ;;
esac
