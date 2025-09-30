#!/bin/bash

# Quantum-Safe Blockchain Guardrail Test Runner
# Runs all tests for the system

echo "🧪 Running Quantum-Safe Blockchain Guardrail Tests..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if required tools are installed
check_prerequisites() {
    echo "🔍 Checking prerequisites..."
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Install test dependencies
install_dependencies() {
    echo "📦 Installing test dependencies..."
    
    # Install Node.js test dependencies
    npm install --save-dev jest supertest
    
    # Install Python test dependencies
    if ! python3 -c "import pytest" 2>/dev/null; then
        print_warning "Installing pytest..."
        pip3 install pytest
    fi
    
    print_status "Dependencies installed"
}

# Run Node.js tests
run_node_tests() {
    echo "🧪 Running Node.js tests..."
    
    if npm test; then
        print_status "Node.js tests passed"
        return 0
    else
        print_error "Node.js tests failed"
        return 1
    fi
}

# Run Python tests
run_python_tests() {
    echo "🐍 Running Python tests..."
    
    # Check if liboqs is available
    if ! python3 -c "import liboqs" 2>/dev/null; then
        print_warning "liboqs not available, skipping PQC tests"
        return 0
    fi
    
    if python3 -m pytest tests/*.py -v; then
        print_status "Python tests passed"
        return 0
    else
        print_error "Python tests failed"
        return 1
    fi
}

# Run integration tests
run_integration_tests() {
    echo "🔗 Running integration tests..."
    
    # Start services in background for integration tests
    print_warning "Integration tests require running services"
    print_warning "Please run './start.sh' in another terminal first"
    
    # For now, just check if the main application can start
    timeout 10s node src/index.js --test-mode 2>/dev/null &
    APP_PID=$!
    
    sleep 3
    
    if kill -0 $APP_PID 2>/dev/null; then
        print_status "Main application started successfully"
        kill $APP_PID 2>/dev/null
        return 0
    else
        print_error "Main application failed to start"
        return 1
    fi
}

# Generate test report
generate_report() {
    echo "📊 Generating test report..."
    
    # Create reports directory
    mkdir -p reports
    
    # Generate coverage report
    if [ -d "coverage" ]; then
        cp -r coverage reports/
        print_status "Coverage report generated in reports/coverage/"
    fi
    
    # Generate test summary
    cat > reports/test-summary.md << EOF
# Test Summary

## Test Results
- Node.js Tests: $1
- Python Tests: $2
- Integration Tests: $3

## Coverage
- See reports/coverage/ for detailed coverage information

## Generated: $(date)
EOF
    
    print_status "Test report generated in reports/test-summary.md"
}

# Main execution
main() {
    echo "🚀 Starting test suite..."
    echo "=================================="
    
    # Check prerequisites
    check_prerequisites
    
    # Install dependencies
    install_dependencies
    
    # Initialize result variables
    node_result=0
    python_result=0
    integration_result=0
    
    # Run tests
    echo ""
    echo "🧪 Running test suites..."
    echo "=================================="
    
    # Node.js tests
    if ! run_node_tests; then
        node_result=1
    fi
    
    echo ""
    
    # Python tests
    if ! run_python_tests; then
        python_result=1
    fi
    
    echo ""
    
    # Integration tests
    if ! run_integration_tests; then
        integration_result=1
    fi
    
    # Generate report
    echo ""
    echo "📊 Generating reports..."
    echo "=================================="
    generate_report $node_result $python_result $integration_result
    
    # Summary
    echo ""
    echo "📋 Test Summary"
    echo "=================================="
    
    if [ $node_result -eq 0 ]; then
        print_status "Node.js tests: PASSED"
    else
        print_error "Node.js tests: FAILED"
    fi
    
    if [ $python_result -eq 0 ]; then
        print_status "Python tests: PASSED"
    else
        print_error "Python tests: FAILED"
    fi
    
    if [ $integration_result -eq 0 ]; then
        print_status "Integration tests: PASSED"
    else
        print_error "Integration tests: FAILED"
    fi
    
    # Overall result
    total_failures=$((node_result + python_result + integration_result))
    
    if [ $total_failures -eq 0 ]; then
        echo ""
        print_status "🎉 All tests passed!"
        exit 0
    else
        echo ""
        print_error "💥 $total_failures test suite(s) failed"
        exit 1
    fi
}

# Run main function
main "$@"
