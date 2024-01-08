#!/usr/bin/env bash

# The script assumes the Lambdas are found in the same directory
SCRIPT_DIR=$(pwd)/$(dirname $0)

# Find all the projects with tests
TEST_DIRS=$(find $SCRIPT_DIR/*/* -name "tests" -print | grep -v "junit_reports")

if [[ -z $TEST_DIRS ]]; then
  echo "No test folders found"
  exit 1
else
  printf "Test folders found:\n%s\n\n" "$TEST_DIRS"
fi

# Install common dependencies for testing
python -m pip install pytest pytest-cov ddt > /dev/null 2>&1

export AWS_REGION="us-east-1"

# Delete existing reports
rm -f $SCRIPT_DIR/.coverage
rm -rf $SCRIPT_DIR/junit_reports/
rm -rf $SCRIPT_DIR/coverage_reports/

# Get the number of test folders
LAST_INDEX=$(echo $TEST_DIRS | wc -w)
INDEX=1

# Loop through each project and run the tests
for TEST_DIR in $TEST_DIRS
do
    # Change to the directory that is up one level from the tests
    cd "$TEST_DIR"/.. || exit 1

    # Get the name of the current directory
    PROJECT_NAME=${PWD##*/}

    # Optionally pass the PROJECT_NAME as argument to isolate those tests
    if [ $1 ] && [ "$PROJECT_NAME" != "$1" ]; then
        continue
    fi

    # Change to the Lambda's root directory so that common utilities can be imported
    # by the tests, and set the PYTHONPATH to include the Lambda's main source code directory
    cd ..
    export PYTHONPATH=.:${PROJECT_NAME}/handler
    # Install the requirements for the tests
    echo "Installing dependencies for $PROJECT_NAME"
    python -m pip install -r ${PROJECT_NAME}/tests/requirements.txt > /dev/null 2>&1

    # Execute the tests with code coverage
    FAIL_UNDER=0
    if [[ $INDEX -eq $LAST_INDEX ]]
    then
        FAIL_UNDER=90
    fi

    echo "Executing tests against $PROJECT_NAME"
    echo "python -m pytest -W=ignore --cov-report term-missing --cov-report xml:${SCRIPT_DIR}/coverage_reports/${PROJECT_NAME}-coverage.xml --cov-config=${PROJECT_NAME}/.coveragerc --cov=${PROJECT_NAME}/. --cov-append --cov-fail-under=${FAIL_UNDER} --junitxml ${SCRIPT_DIR}/junit_reports/${PROJECT_NAME}.xml ${PROJECT_NAME}/tests"
    if ! python -m pytest -W=ignore --cov-report term-missing --cov-report xml:${SCRIPT_DIR}/coverage_reports/${PROJECT_NAME}-coverage.xml --cov-config=${PROJECT_NAME}/.coveragerc --cov=${PROJECT_NAME}/. --cov-append --cov-fail-under=${FAIL_UNDER} --junitxml ${SCRIPT_DIR}/junit_reports/${PROJECT_NAME}.xml ${PROJECT_NAME}/tests
    then
        # Fail when tests fail
        exit 1
    fi

    # This line may be required at a later date, if tests
    # in different projects require non-combatible requirements
    #
    #echo "Uninstalling dependencies for $PROJECT_NAME"
    #python -m pip uninstall -y -r ${PROJECT_NAME}/tests/requirements.txt > /dev/null 2>&1

    cd "$SCRIPT_DIR" || exit 1

    INDEX=$(expr $INDEX + 1)

done

exit 0
