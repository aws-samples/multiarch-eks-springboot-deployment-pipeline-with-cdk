#!/bin/bash
if [[ $# -ge 2 ]]; then
    export CDK_DEPLOY_ACCOUNT=$1
    export CDK_DEPLOY_REGION=$2
    shift; shift
    source .env/bin/activate
    pip install -r requirements.txt
    cdk bootstrap aws://$1/$2
    # cdk deploy backend
    cdk deploy pipeline
    exit $?
else
    echo 1>&2 "Provide AWS account and region as first two args."
    exit 1
fi
