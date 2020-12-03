# Welcome to Multiarch EKS Springboot Deployment Pipeline with CDK 

# Overview
AWS Graviton 2(using ARM) provides up to 40% better price performance over comparable current generation x86-based instances for a wide variety of workloads.
A hybrid ARM & AMD deployment takes advantage of the Graviton instances, at the same time lowers risks to migrate from AMD to ARM in one shot.
In this sample, you will build a java springboot application on a hybrid ARM & AMD EKS cluster. You will use the same source code to trigger an automatic deployment pipeline, build on both ARM and AMD. The whole setup is based on AWS Cloud Development Kit(CDK). 

## Architecture diagram
![Architecture](/readme_img/architecture.png)

### deployment pipeline
### springboot application backend

# Run the Pipeline
## Prerequisite
1. Install cdk
Follow the [prerequisites and install guidance](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_prerequisites). CDK will be used to deploy the application backend and deployment pipeline stacks.
2. Dockerhub account and access token
Access token can be created in [dockerhub](https://hub.docker.com/settings/security). The username and token will be used to pull images from dockerhub during code build phase.
3. Install kubectl
Follow the [instructions](https://kubernetes.io/docs/tasks/tools/install-kubectl/). kubectl will be used to communicate with the ESK cluster.

## Step by step guidance
1. Create Systems Manager Parameter Store in the console
- Search system manager in services
- Click Parameter Store in the left panel
- Prepare your dockerhub username and access token
- Click Create to create a new parameter, input Name as `/springboot-multiarch/dockerhub/username` and Value as your dockerhub username
- Leave the others as default and click Create Parameter
- Click Create to create a new parameter, input Name as `/springboot-multiarch/dockerhub/password` and Value as your dockerhub access token
- Leave the others as default and click Create Parameter


2. Checkout the code, deploy both springboot application backend and deployment pipeline on AWS via CDK
```shell
# Checkout the code
git clone https://github.com/aws-samples/multiarch-eks-springboot-deployment-pipeline-with-cdk.git

# Prepare env
cd multiarch-eks-springboot-deployment-pipeline-with-cdk/cdk
python3 -m venv .env

# Run cdk to deploy both springboot application backend and deployment pipeline
# Please make sure CodeBuild ARM support(https://aws.amazon.com/codebuild/pricing/) 
# is available in the chosen region 
# e.g. ./bootstrap.sh 12345678 us-east-1
./bootstrap.sh {AWS ACCOUNT ID} {REGION}

# Don't forget to note down the CDK outputs
# i.e.
# backend.EKSConfigCommandxxxx
# pipeline.CodeCommitOutput
```

3. Commit code to codecommit to trigger the pipeline
```shell
# Checkout the new codecommit respository created by CDK in step 2
# i.e. value of pipeline.CodeCommitOutput
git clone https://git-codecommit.{REGION}.amazonaws.com/v1/repos/springboot-multiarch test

# Copy source code to the new codecommit repository
cd test
cp -r ../springboot-multiarch/* .

# Commit source code to trigger deployment pipeline
git add *
git commit -m "trigger commit"
git push
```

4. Get application load balancer(ALB) address and visit
```shell
# Config kubectl to connect to the EKS cluster created by CDK in step 2
# Check CDK output backend.EKSConfigCommandxxxx
# e.g. aws eks update-kubeconfig --name {EKS CLUSTER NAME} --region {REGION} --role-arn {EKS MASTER IAM ROLE}

# get ALB address from kubernetes cluster
kubectl describe ingress | grep Address 
```

## Expected results
1. Visit the ALB address output from step 4 in the last section. NOTE: You need to wait for about 1 minute before ALB is successfully provisioned.
2. Confirm browser shows the content similar to:
```
{"RDS Test":"passed","Node Name":"ip-10-xx-xxx-xx.ap-northeast-1.compute.internal","Redis Test":"passed"}
```
3. Refresh the page several times to observe the Node Name switch. The nodes are running AMD and ARM (graviton) correspondingly.

## Cleanup
```shell
cd cdk
./cleanup.sh {AWS ACCOUNT ID} {REGION}
```

# Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

# License

This library is licensed under the MIT-0 License. See the LICENSE file.

