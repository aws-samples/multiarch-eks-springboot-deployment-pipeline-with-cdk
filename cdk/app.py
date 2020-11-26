#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import os

from aws_cdk import core

from pipeline.pipeline_stack import PipelineStack
from backend.backend_stack import BackendStack

env = core.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"],
                       region=os.environ["CDK_DEFAULT_REGION"])

app = core.App()

backend = BackendStack(app, "backend", env=env)
pipeline = PipelineStack(app, "pipeline", eks=backend.eks, redis=backend.redis,
                        rds_cluster=backend.rds_cluster, env=env)

app.synth()
