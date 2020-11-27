# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_cdk import (core,  aws_lambda as lambda_, 
                     aws_s3 as s3, aws_eks as eks,
                     aws_iam as iam, aws_ec2 as ec2,
                     aws_elasticache as elasticache,
                     aws_rds as rds)
                     
import json


class BackendStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        
        super().__init__(scope, id, **kwargs)
        
        # create new vpc
        vpc = ec2.Vpc(self, "VPC")
        
        # create eks
        self.eks = self.create_eks(vpc)
        
        # create elasticache redis
        self.redis = self.create_redis(vpc, self.eks)
        
        # create rds
        self.rds_cluster = self.create_rds(vpc, self.eks)
        
        
    def create_eks(self, vpc):
        # create eks cluster with amd nodegroup
        cluster = eks.Cluster(self, "EKS", vpc=vpc, version=eks.KubernetesVersion.V1_18,
                                default_capacity_instance=ec2.InstanceType("m5.large"),
                                default_capacity=1)
        # add arm/graviton nodegroup
        cluster.add_nodegroup_capacity("graviton", desired_size=1, 
                                instance_type=ec2.InstanceType("m6g.large"), 
                                nodegroup_name="graviton", node_role=cluster.default_nodegroup.role)
                                
        # add secret access to eks node role
        cluster.default_nodegroup.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite"))
        
        # create service account
        sa = self.add_service_account(cluster=cluster, name="aws-load-balancer-controller", 
                                      namespace="kube-system")
        
        # add helm charts
        ingress = cluster.add_helm_chart("LBIngress", chart="aws-load-balancer-controller",
                                release="aws-load-balancer-controller",
                                repository="https://aws.github.io/eks-charts",
                                namespace="kube-system", values={
                                    "clusterName": cluster.cluster_name,
                                    "serviceAccount.name": "aws-load-balancer-controller",
                                    "serviceAccount.create": "false"
                                })

        return cluster
        
        
    def create_redis(self, vpc, eks):
        # create subnet group
        subnet_group = elasticache.CfnSubnetGroup(self, "RedisClusterPrivateSubnetGroup",
                                        cache_subnet_group_name="redis-springboot-multiarch",
                                        subnet_ids=vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE).subnet_ids,
                                        description="springboot multiarch demo")
        # create security group
        security_group = ec2.SecurityGroup(self, "RedisSecurityGroup", vpc=vpc,
                                        description="Allow redis connection from eks",
                                        allow_all_outbound=True)
        eks.connections.allow_to(security_group, ec2.Port.tcp(6379))
        # create redis cluster
        redis = elasticache.CfnCacheCluster(self, "RedisCluster",
                                          engine="redis",
                                          cache_node_type= "cache.t2.small",
                                          num_cache_nodes=1,
                                          cluster_name="redis-springboot-multiarch",
                                          vpc_security_group_ids=[security_group.security_group_id],
                                          cache_subnet_group_name=subnet_group.cache_subnet_group_name)
        redis.add_depends_on(subnet_group);
        
        return redis
        
        
    def create_rds(self, vpc, eks):
        rds_cluster = rds.DatabaseCluster(self, "Database",
            engine=rds.DatabaseClusterEngine.aurora_mysql(version=rds.AuroraMysqlEngineVersion.VER_2_08_1),
            instance_props={
                "instance_type": ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.SMALL),
                "vpc_subnets": {
                    "subnet_type": ec2.SubnetType.PRIVATE
                },
                "vpc": vpc
            }
        ) 
        eks.connections.allow_to(rds_cluster, ec2.Port.tcp(3306))
        
        return rds_cluster
        
    
    def add_service_account(self, cluster, name, namespace):
        """
        workaround to add helm role to service account
        
        """
        # create role 
        conditions = core.CfnJson(self, 'ConditionJson',
          value = {
            "%s:aud" % cluster.cluster_open_id_connect_issuer : "sts.amazonaws.com",
            "%s:sub" % cluster.cluster_open_id_connect_issuer : "system:serviceaccount:%s:%s" % (namespace, name),
          },
        )
        principal = iam.OpenIdConnectPrincipal(cluster.open_id_connect_provider).with_conditions({
          "StringEquals": conditions,
        })
        role = iam.Role(self, 'ServiceAccountRole', assumed_by=principal)
        
        # create policy for the service account
        statements = []
        with open('backend/iam_policy.json') as f:
            data = json.load(f)
            for s in data["Statement"]:
                statements.append(iam.PolicyStatement.from_json(s))
        policy = iam.Policy(self, "LBControllerPolicy", statements=statements)
        policy.attach_to_role(role)
    
        return eks.KubernetesManifest(self, "ServiceAccount", cluster=cluster,
          manifest=[{
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
              "name": name, 
              "namespace": namespace ,
              "labels": {
                "app.kubernetes.io/name": name, 
                "app.kubernetes.io/managed-by": "Helm",
              },
              "annotations": {
                "eks.amazonaws.com/role-arn": role.role_arn,
                "meta.helm.sh/release-name": name, 
                "meta.helm.sh/release-namespace": namespace, 
              },
            },
          }],
        );