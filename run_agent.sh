#!/bin/bash

# Resolve the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
AGENT_DIR="$SCRIPT_DIR/Ticket-Agent"

# Ensure we are in the right place
if [ ! -d "$AGENT_DIR" ]; then
    echo "❌ Error: Cannot find directory '$AGENT_DIR'."
    exit 1
fi

cd "$AGENT_DIR" || exit

echo "✅ Entered $AGENT_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if Server is running on port 8000
if lsof -i :8000 > /dev/null; then
    echo "🚀 Agent Server is already running."
else
    echo "🔄 Starting Agent Server in background..."
    npm run start > server.log 2>&1 &
    # Give it a moment to boot
    sleep 3
fi

echo "💬 Starting Chat Client..."
npx tsx scripts/chat_cli.ts
