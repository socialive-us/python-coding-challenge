#!/bin/bash

# Run the tests
./run_tests.sh
TEST_RESULTS=$?

if [[ $TEST_RESULTS -ne 0 ]]
then
    exit 1
fi

exit 0
