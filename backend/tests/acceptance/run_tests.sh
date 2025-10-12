#!/bin/bash
#
# NeuroAgent Acceptance Tests Runner
#
# Usage:
#   ./backend/tests/acceptance/run_tests.sh [OPTIONS]
#
# Options:
#   all          - Run all tests (default)
#   critical     - Run only critical tests
#   positive     - Run only positive tests
#   negative     - Run only negative tests
#   validation   - Run only validation tests
#   red_flag     - Run only red flag tests
#   performance  - Run only performance tests
#   localization - Run only localization tests
#   report       - Generate HTML report
#   coverage     - Generate coverage report
#   help         - Show this help message

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
TEST_DIR="$PROJECT_ROOT/backend/tests/acceptance"
REPORT_DIR="$PROJECT_ROOT/reports/acceptance"

# Create report directory
mkdir -p "$REPORT_DIR"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check dependencies
check_dependencies() {
    print_info "Checking dependencies..."

    if ! command -v python3 &> /dev/null; then
        print_error "python3 not found. Please install Python 3.9+"
        exit 1
    fi

    if ! python3 -c "import pytest" &> /dev/null; then
        print_error "pytest not found. Installing dependencies..."
        pip install -r "$TEST_DIR/requirements.txt"
    fi

    print_success "Dependencies OK"
}

# Function to set environment variables
setup_environment() {
    print_info "Setting up test environment..."

    export TEST_API_BASE_URL="${TEST_API_BASE_URL:-http://localhost:8000}"
    export AWS_REGION="${AWS_REGION:-us-east-1}"
    export TEST_DYNAMODB_TABLE="${TEST_DYNAMODB_TABLE:-NeuroAgent-PatientCases-Test}"
    export TEST_TIMEOUT="${TEST_TIMEOUT:-30}"
    export ENABLE_MOCKS="${ENABLE_MOCKS:-true}"

    print_info "TEST_API_BASE_URL: $TEST_API_BASE_URL"
    print_info "ENABLE_MOCKS: $ENABLE_MOCKS"

    print_success "Environment configured"
}

# Function to run tests
run_tests() {
    local marker=$1
    local description=$2

    print_info "Running $description..."

    cd "$PROJECT_ROOT"

    if [ -z "$marker" ]; then
        # Run all tests
        pytest "$TEST_DIR" \
            -v \
            --junit-xml="$REPORT_DIR/junit.xml" \
            --html="$REPORT_DIR/report.html" \
            --self-contained-html
    else
        # Run tests with specific marker
        pytest "$TEST_DIR" \
            -m "$marker" \
            -v \
            --junit-xml="$REPORT_DIR/junit-${marker}.xml" \
            --html="$REPORT_DIR/report-${marker}.html" \
            --self-contained-html
    fi

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        print_success "$description completed successfully"
        print_info "Report: $REPORT_DIR/report${marker:+-$marker}.html"
    else
        print_error "$description failed with exit code $exit_code"
        exit $exit_code
    fi
}

# Function to run tests with coverage
run_with_coverage() {
    print_info "Running tests with coverage analysis..."

    cd "$PROJECT_ROOT"

    pytest "$TEST_DIR" \
        -v \
        --cov=backend \
        --cov-report=html:"$REPORT_DIR/coverage" \
        --cov-report=term-missing \
        --cov-report=xml:"$REPORT_DIR/coverage.xml" \
        --junit-xml="$REPORT_DIR/junit.xml" \
        --html="$REPORT_DIR/report.html" \
        --self-contained-html

    print_success "Coverage report: $REPORT_DIR/coverage/index.html"
}

# Function to show help
show_help() {
    cat << EOF
${GREEN}NeuroAgent Acceptance Tests Runner${NC}

Usage:
    $0 [OPTIONS]

Options:
    ${YELLOW}all${NC}          - Run all tests (default)
    ${YELLOW}critical${NC}     - Run only critical tests (@critical marker)
    ${YELLOW}positive${NC}     - Run only positive tests (@positive marker)
    ${YELLOW}negative${NC}     - Run only negative tests (@negative marker)
    ${YELLOW}validation${NC}   - Run only validation tests (@validation marker)
    ${YELLOW}red_flag${NC}     - Run only red flag tests (@red_flag marker)
    ${YELLOW}performance${NC}  - Run only performance tests (@performance marker)
    ${YELLOW}localization${NC} - Run only localization tests (@localization marker)
    ${YELLOW}report${NC}       - Run all tests and generate HTML report
    ${YELLOW}coverage${NC}     - Run tests with coverage analysis
    ${YELLOW}help${NC}         - Show this help message

Examples:
    # Run all tests
    $0 all

    # Run only critical tests
    $0 critical

    # Run with coverage
    $0 coverage

    # Run specific scenario by keyword
    pytest backend/tests/acceptance/ -k "typical_migraine" -v

Environment Variables:
    TEST_API_BASE_URL      - API endpoint (default: http://localhost:8000)
    ENABLE_MOCKS           - Use mocks instead of real AWS (default: true)
    AWS_REGION             - AWS region (default: us-east-1)
    TEST_DYNAMODB_TABLE    - DynamoDB table name
    TEST_TIMEOUT           - Test timeout in seconds (default: 30)

Test Markers:
    @critical              - Critical path tests (must pass for MVP)
    @positive              - Positive test cases (expected success)
    @negative              - Negative test cases (expected failure)
    @validation            - Input validation tests
    @red_flag              - Red flag symptom detection
    @performance           - Performance/SLA tests
    @localization          - Multi-language tests
    @drug_interaction      - Drug interaction checking

Reports:
    HTML Report:     $REPORT_DIR/report.html
    JUnit XML:       $REPORT_DIR/junit.xml
    Coverage Report: $REPORT_DIR/coverage/index.html

EOF
}

# Main execution
main() {
    local command=${1:-all}

    # Print banner
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║       NeuroAgent Acceptance Tests (Pytest-BDD)           ║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    check_dependencies
    setup_environment

    case $command in
        all)
            run_tests "" "all acceptance tests"
            ;;
        critical)
            run_tests "critical" "critical path tests"
            ;;
        positive)
            run_tests "positive" "positive test cases"
            ;;
        negative)
            run_tests "negative" "negative test cases"
            ;;
        validation)
            run_tests "validation" "validation tests"
            ;;
        red_flag)
            run_tests "red_flag" "red flag detection tests"
            ;;
        performance)
            run_tests "performance" "performance tests"
            ;;
        localization)
            run_tests "localization" "localization tests"
            ;;
        drug_interaction)
            run_tests "drug_interaction" "drug interaction tests"
            ;;
        report)
            run_tests "" "all tests with HTML report"
            ;;
        coverage)
            run_with_coverage
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac

    echo ""
    print_success "Test execution completed!"
    echo ""
}

# Run main function
main "$@"
