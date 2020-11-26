#!/bin/bash
source .env/bin/activate
pip install -r requirements.txt
cdk bootstrap aws://$1/us-east-1
# cdk deploy backend
cdk deploy pipeline