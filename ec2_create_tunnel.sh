#!/usr/bin/env bash

EC2_HOSTNAME=`cat ./.ec2_hostname`
if [ -z $EC2_HOSTNAME ]; then
  echo ""
  echo "No hostname detected in '.ec2_hostname' :( Exiting!"
  echo ""
  echo "The command to create an ssh tunnel to port 5000 of your ec2 instance is: ssh -R 5000:localhost:5000 ubuntu@<ec2_hostname>"
  echo ""
  exit
fi

echo ""
echo "This script will create an ssh tunnel between the ec2 host's port 5000 and your local port 5000."
echo "This will enable you to view web applications you run from ex. Agile_Data_Code_2/ch08/web to be viewed at http://localhost:5000"
echo "Note: the tunnel will run in the background, and will die when you terminate the EC2 instance."
echo ""

# Create a tunnel to our ssh instance, port 5000 and map it to localhost:5000
echo 'Executing: ssh -N -i ./agile_data_science.pem -L 5000:localhost:5000 ubuntu@$EC2_HOSTNAME &'
ssh -N -i ./agile_data_science.pem -o StrictHostKeyChecking=no -L 5000:localhost:5000 ubuntu@$EC2_HOSTNAME &
