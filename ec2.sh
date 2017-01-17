#!/usr/bin/env bash

VPC_ID = `aws ec2 create-vpc --cidr-block 10.0.0.1/24 | jq -r ".Vpc.VpcId"`

aws ec2 create-security-group \
    --group-name agile_data_science_group \
    --description "ADS Security Group"

aws ec2 run-instances \
    --dry-run \
    --image-id ami-4ae1fb5d \
    --key-name agile_data_science \
    --user-data ./ec2_bootstrap.sh \
    --instance-type r4.large \
    --ebs-optimized \
    --associate-public-ip-address \
    --security-groups agile_data_science_group \
      \
    --count 1