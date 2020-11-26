#!/usr/bin/env python3

from aws_cdk import core

from pipeline.pipeline_stack import PipelineStack
from backend.backend_stack import BackendStack

env = core.Environment(region="us-east-1")

app = core.App()

backend = BackendStack(app, "backend", env=env)
pipeline = PipelineStack(app, "pipeline", eks=backend.eks, redis=backend.redis,
                        rds_cluster=backend.rds_cluster, env=env)

app.synth()
