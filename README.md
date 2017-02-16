# Agile_Data_Code_2

Code for Agile Data Science 2.0, O'Reilly 2017.

## Installation

There are two methods of installation: Vagrant/Virtualbox or Amazon EC2.

### Amazon EC2

Amazon EC2 is the preferred environment for this book/course, because it is simple and painless.

Installation takes just a few moments using Amazon EC2. The script [ec2.sh](ec2.sh) uses the file [aws/ec2_bootstrap.sh](aws/ec2_bootstrap.sh) as `--user-data` to boot a single r3.xlarge EC2 instance in the us-east-1 region with all dependencies installed and running.

```
# Launch our instance, which ec2_bootstrap.sh will initialize
aws ec2 run-instances \
    --image-id ami-4ae1fb5d \
    --key-name agile_data_science \
    --user-data file://aws/ec2_bootstrap.sh \
    --instance-type r3.xlarge \
    --ebs-optimized \
    --placement "AvailabilityZone=us-east-1d" \
    --block-device-mappings '{"DeviceName":"/dev/sda1","Ebs":{"DeleteOnTermination":false,"VolumeSize":1024}}' \
    --count 1
```



Once the server comes up, download the data and you are ready to go:

```
cd Agile_Data_Code_2
./download.sh
```

Note: if you change the zone from us-east-1, you will need to update to a new image that corresponds to that region. This is explained in chapter 2. Go to [https://cloud-images.ubuntu.com/locator/ec2/](https://cloud-images.ubuntu.com/locator/ec2/) to find the Ubuntu image for your desired region.

### Vagrant/Virtualbox Install

Installation takes a few minutes, using Vagrant and Virtualbox. 

Note: this method requires 9GB free RAM, which will mean closing most programs on a 16GB Macbook Pro.

```
vagrant up
vagrant ssh
```

Then download the data:

```
cd Agile_Data_Code_2
./download.sh
```

### Manual Install

For a manual install read Appendix A for further setup instructions. Checkout [manual_install.sh](manual_install.sh) if you want to install the tools yourself and run the example code. 

## Running Examples

All scripts run from the base directory, except the web app which runs in ex. `ch08/web/`.

# Screenshots

![Airline Page](images/airline_page_enriched_wikipedia.png)
![Airplane Fleet Page](images/airplanes_page_chart_v1_v2.png)
![Predicting Flight Delays UI](images/predicting_flight_kafka_waiting.png)

# The Data Value Pyramid

Originally by Pete Warden, the data value pyramid is how the book is organized and structured. We climb it as we go forward each chapter.

![Data Value Pyramid](images/climbing_the_pyramid_chapter_intro.png)

# Architecture Diagrams

Pulled from the book, the basic concepts are expressed by these.

![Front End Architecture](images/front_end_realtime_architecture.png)
![Backend Architecture](images/back_end_realtime_architecture.png)
