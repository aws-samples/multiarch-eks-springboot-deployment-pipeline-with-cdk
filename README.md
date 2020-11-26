# Welcome to Multiarch EKS Springboot Deployment Pipeline with CDK 

# Overview

## Architecture diagram
![Architecture](/readme_img/architecture.png)

### deployment pipeline
### springboot application backend

# Run the Pipeline
## Prerequisite
1. install cdk
2. dockerhub account
3. install aws cli & config access
4. install kubectl

## Step by step guidance
1. create Systems Manager Parameter on the console
/springboot-multiarch/dockerhub/username
/springboot-multiarch/dockerhub/password
TODO

2. Checkout the code, deploy both springboot application backend and deployment pipeline on AWS via CDK
```
# Checkout the code
git clone https://github.com/lazydragon/eks_arm_with_gitlab_cicd.git

# Prepare env
cd eks_arm_with_gitlab_cicd/cdk
python3 -m venv .env

# Run cdk to deploy both springboot application backend and deployment pipeline
# Please make sure CodeBuild ARM support(https://aws.amazon.com/codebuild/pricing/) is available in the chosen region 
./bootstrap.sh {AWS ACCOUNT ID} {REGION}
# e.g. ./bootstrap.sh 12345678 us-east-1

# Don't forget to note down the CDK outputs
# Such as TODO
```

3. Commit code to codecommit to trigger the pipeline
```
# Checkout the new codecommit respository created by CDK in step 2
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
```
# Config kubectl to connect to the EKS cluster created by CDK in step 2
# Check CDK output TODO
# e.g. aws eks update-kubeconfig --name {EKS CLUSTER NAME} --region {REGION} --role-arn {EKS MASTER IAM ROLE}

# get ALB address from kubernetes cluster
kubectl describe ingress | grep Address 
```

## Expected results

## Cleanup
```
cd cdk
./cleanup.sh
```

# Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

# License

This library is licensed under the MIT-0 License. See the LICENSE file.

