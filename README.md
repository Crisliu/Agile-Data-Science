# Agile_Data_Code_2

Code for [Agile Data Science 2.0](http://shop.oreilly.com/product/0636920051619.do), O'Reilly 2017. Now available in [Preview on O'Reilly Safari](https://www.safaribooksonline.com/library/view/agile-data-science/9781491960103/).

This is also the code for the [Realtime Predictive Analytics](http://datasyndrome.com/video) video course and [Introduction to PySpark](http://datasyndrome.com/training) live course!

Have problems? Please file an issue!

## Data Syndrome

Like my work? I am Principal Consultant at [Data Syndrome](http://datasyndrome.com), a consultancy offering assistance and training with building full-stack analytics products, applications and systems. Find us on the web at [datasyndrome.com](http://datasyndrome.com).

![Data Syndrome Logo](images/data_syndrome_logo.png)

## Realtime Predictive Analytics Course

There is now a video course using code from chapter 8, [Realtime Predictive Analytics with Kafka, PySpark, Spark MLlib and Spark Streaming](http://datasyndrome.com/video). Check it out now at [datasyndrome.com/video](http://datasyndrome.com/video).

A free preview of the course is available at [https://vimeo.com/202336113](https://vimeo.com/202336113)

[<img src="images/video_course_cover.png">](http://datasyndrome.com/video)

## Installation

There are two methods of installation: Vagrant/Virtualbox or Amazon EC2.

### Amazon EC2

Amazon EC2 is the preferred environment for this book/course, because it is simple and painless.

Installation takes just a few moments using Amazon EC2. The script [ec2.sh](ec2.sh) uses the file [aws/ec2_bootstrap.sh](aws/ec2_bootstrap.sh) as `--user-data` to boot a single r3.xlarge EC2 instance in the us-east-1 region with all dependencies installed and running.

**Note: You must have two things setup for this script to work!**

1. You must alter the key setup to match your own keys. You can do this by having a key called agile_data_science.pem in the project directory AND in us-east-1. Or you can substitute a key that you do have in whatever zone, and you can change the zone in the command to the one you want.
2. If you change zones, you need to change the image ID. Go to [https://cloud-images.ubuntu.com/locator/ec2/](https://cloud-images.ubuntu.com/locator/ec2/) and find a new image ID, or use the table below.

The images for `yakkety Ubuntu hvm:ebs-ssd` by zone to substitute for the `--image-id` value are:

| Zone           | Image ID     |
|----------------|--------------|
| us-east-1      | ami-4ae1fb5d |
| ap-south-1     | ami-4d542222 |
| ap-northeast-1 | ami-65750502 |
| eu-west-1      | ami-cbfcd2b8 |
| ap-southeast-1 | ami-93a800f0 |
| us-west-1      | ami-818fdfe1 |
| eu-central-1   | ami-5175b73e |
| sa-east-1      | ami-1937ac75 |
| ap-southeast-2 | ami-a87c79cb |
| ap-northeast-2 | ami-9325f3fd |
| us-west-2      | ami-a41eaec4 |
| us-east-2      | ami-d5e7bdb0 |

[<img src="images/ubuntu_images.png">](https://cloud-images.ubuntu.com/locator/ec2/)

#### Amazon EC2 Launch Command

This is the command to alter to match your zone and key setup.

```
# Launch our instance, which ec2_bootstrap.sh will initialize
aws ec2 run-instances \
    --image-id ami-4ae1fb5d \
    --key-name agile_data_science \
    --user-data file://aws/ec2_bootstrap.sh \
    --instance-type r3.xlarge \
    --ebs-optimized \
    --region us-east-1 \
    --block-device-mappings '{"DeviceName":"/dev/sda1","Ebs":{"DeleteOnTermination":false,"VolumeSize":1024}}' \
    --count 1
```

Now jump ahead to "Downloading Data".

### Vagrant/Virtualbox Install

Installation takes a few minutes, using Vagrant and Virtualbox. 

**Note: Vagrant/Virtualbox method requires 9GB free RAM, which will mean closing most programs on a 16GB Macbook Pro. If you don't close most everything, you will run out of RAM and your system will crash. Use the EC2 method if this is a problem for you.**

```
vagrant up
vagrant ssh
```

Now jump ahead to Downloading Data.

### Manual Install

For a manual install read Appendix A for further setup instructions. Checkout [manual_install.sh](manual_install.sh) if you want to install the tools yourself and run the example code. 

## Downloading Data

Once the server comes up, download the data and you are ready to go. First change directory into the `Agile_Data_Code_2` directory.

```
cd Agile_Data_Code_2
```
Now download the data, depending on which activity this is for.

For the book Agile Data Science 2.0, run: 

```
./download.sh
```

For the [Introduction to PySpark](http://datasyndrome.com/training) course, run:

```
./intro_download.sh
```

For the [Realtime Predictive Analytics](http://datasyndrome.com/video) video course, or to skip ahead to chapter 8 in the book, run: 

```
ch08/download_data.sh
```

## Running Examples

All scripts run from the base directory, except the web app which runs in ex. `ch08/web/`.

### Jupyter Notebooks

All notebooks assume you have run the jupyter notebook command from the project root directory `Agile_Data_Code_2`. If you are using a virtual machine image (Vagrant/Virtualbox or EC2), jupyter notebook is already running. See directions on port mapping to proceed.

# The Data Value Pyramid

Originally by Pete Warden, the data value pyramid is how the book is organized and structured. We climb it as we go forward each chapter.

![Data Value Pyramid](images/climbing_the_pyramid_chapter_intro.png)

# System Architecture

The following diagrams are pulled from the book, and express the basic concepts in the system architecture. The front and back end architectures work together to make a complete predictive system.

## Front End Architecture

This diagram shows how the front end architecture works in our flight delay prediction application. The user fills out a form with some basic information in a form on a web page, which is submitted to the server. The server fills out some neccesary fields derived from those in the form like "day of year" and emits a Kafka message containing a prediction request. Spark Streaming is listening on a Kafka queue for these requests, and makes the prediction, storing the result in MongoDB. Meanwhile, the client has received a UUID in the form's response, and has been polling another endpoint every second. Once the data is available in Mongo, the client's next request picks it up. Finally, the client displays the result of the prediction to the user! 

This setup is extremely fun to setup, operate and watch. Check out chapters 7 and 8 for more information!

![Front End Architecture](images/front_end_realtime_architecture.png)

## Back End Architecture

The back end architecture diagram shows how we train a classifier model using historical data (all flights from 2015) on disk (HDFS or Amazon S3, etc.) to predict flight delays in batch in Spark. We save the model to disk when it is ready. Next, we launch Zookeeper and a Kafka queue. We use Spark Streaming to load the classifier model, and then listen for prediction requests in a Kafka queue. When a prediction request arrives, Spark Streaming makes the prediction, storing the result in MongoDB where the web application can pick it up.

This architecture is extremely powerful, and it is a huge benefit that we get to use the same code in batch and in realtime with PySpark Streaming.

![Backend Architecture](images/back_end_realtime_architecture.png)

# Screenshots

Below are some examples of parts of the application we build in this book and in this repo. Check out the book for more!

## Airline Entity Page

Each airline gets its own entity page, complete with a summary of its fleet and a description pulled from Wikipedia.

![Airline Page](images/airline_page_enriched_wikipedia.png)

## Airplane Fleet Page

We demonstrate summarizing an entity with an airplane fleet page which describes the entire fleet.

![Airplane Fleet Page](images/airplanes_page_chart_v1_v2.png)

## Flight Delay Prediction UI

We create an entire realtime predictive system with a web front-end to submit prediction requests.

![Predicting Flight Delays UI](images/predicting_flight_kafka_waiting.png)
