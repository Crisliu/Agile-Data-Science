#!/usr/bin/env bash

# Create a new VPC
VPC_ID = `aws ec2 create-vpc --cidr-block 10.0.0.1/24 | jq -r ".Vpc.VpcId"`

# Create a subnet in that VPC
SUBNET_ID = `aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.0.1/24 | jq -r ".Subnet.SubnetId"`

# Create a gateway for our subnet
aws ec2 create-internet-gateway \


# Create a security group in that VPC
aws ec2 create-security-group \
    --group-name agile_data_science_group \
    --description "ADS Security Group" \
    --vpc-id $VPC_ID

# Authorize port 22 inbound in our security group
aws ec2 authorize-security-group-ingress \
    --group-name agile_data_science_group \
    --protocol tcp \
    --port 22 \
    --cidr 10.0.0.1/24

# Authorize port 22 on the VPC security group
aws ec2 authorize-security-group-ingress \
    --group-name default \
    --protocol tcp \
    --port 22 \
    --cidr 10.0.0.1/24

# Launch our instance, which ec2_bootstrap.sh will initialize
aws ec2 run-instances \
    --image-id ami-4ae1fb5d \
    --key-name agile_data_science \
    --user-data file://aws/ec2_bootstrap.sh \
    --instance-type r4.xlarge \
    --ebs-optimized \
    --associate-public-ip-address \
    --subnet-id $SUBNET_ID \
    --count 1 \
    --block-device-mappings '{"DeviceName":"/dev/sda1","Ebs":{"DeleteOnTermination":false,"VolumeSize":1024}}' \
    --dry-run