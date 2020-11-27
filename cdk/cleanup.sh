#!/bin/bash
if [[ $# -ge 2 ]]; then
    source .env/bin/activate
    export CDK_DEPLOY_ACCOUNT=$1
    export CDK_DEPLOY_REGION=$2
    source .env/bin/activate
    cdk destroy pipeline backend
    exit $?
else
    echo 1>&2 "Provide AWS account and region as first two args."
    exit 1
fi