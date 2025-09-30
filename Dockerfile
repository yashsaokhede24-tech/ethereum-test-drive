# Multi-stage Docker build for Quantum-Safe Blockchain Guardrail

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ ./
RUN npm run build

# Stage 2: Build backend Python dependencies
FROM python:3.11-slim AS backend-builder
WORKDIR /app/backend

# Install system dependencies for liboqs
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Final runtime image
FROM python:3.11-slim
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python backend
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY backend/ ./backend/

# Copy Node.js application
COPY package*.json ./
RUN npm ci --only=production

# Copy built frontend
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Copy source code
COPY src/ ./src/

# Create necessary directories
RUN mkdir -p logs data backend/models

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3000
ENV BACKEND_PORT=5000
ENV RPC_URL=http://localhost:8545
ENV WS_URL=ws://localhost:8546

# Expose ports
EXPOSE 3000 5000

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🚀 Starting Quantum-Safe Blockchain Guardrail..."\n\
\n\
# Start Python backend in background\n\
cd backend && python app.py &\n\
BACKEND_PID=$!\n\
\n\
# Wait for backend to start\n\
sleep 5\n\
\n\
# Start main Node.js application\n\
cd .. && node src/index.js &\n\
MAIN_PID=$!\n\
\n\
echo "🎉 Services started!"\n\
echo "📊 Dashboard: http://localhost:3000"\n\
echo "🔧 Backend API: http://localhost:5000"\n\
\n\
# Function to cleanup on exit\n\
cleanup() {\n\
    echo "🛑 Stopping services..."\n\
    kill $BACKEND_PID $MAIN_PID 2>/dev/null\n\
    exit 0\n\
}\n\
\n\
trap cleanup SIGINT SIGTERM\n\
wait\n\
' > /app/start.sh && chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Start the application
CMD ["/app/start.sh"]
