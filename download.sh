#!/bin/bash

if [ $# -eq 0 ]
then
    cat << EOF
    You must supply a local data path as the first argument. e.g:

    ./download.sh /my/data/path
EOF
exit
fi

# Install aws-cli if it doesn't exist
if ! command -v aws &> /dev/null
then
    cat << EOF
    AWS shell must be installed. To install run:

    pip install aws-shell
EOF
fi

ENDPOINT=https://s3.echo.stfc.ac.uk:443
LOCATION=s3://sciml-bench-datasets/e2e

aws s3 --no-sign-request --endpoint-url $ENDPOINT sync $LOCATION $1
