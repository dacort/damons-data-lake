# Build your own data lake

How to build your own cloud-native data lake using AWS with typical data ingest patterns.

## Overview

This project uses managed services from AWS to ingest and store various sources of streaming and batch data.

It uses several personal data sources including my own website, nerdy quantified self metrics, and Apple Health data.

Using a simple [shell script](src/github-stats.py), I publish basic stats to a Kinesis Data Stream.
A Kinesis Data Firehose is then setup to consume the data from that stream and write it out to S3 every so often.
Once in S3, a Glue Crawler identifies the schema and keeps the partitions up-to-date. And then the data can be
queried with Athena!

## Getting started

Currently, I provision this all manually using the AWS console. I will eventually make a CloudFormation template.

Set up the following services - details for each one are below.

- [S3 bucket](#s3-bucket) for raw storage
- AWS [Kinesis](#kinesis) data stream for laptop metrics
- AWS [Kinesis](#kinesis) Firehose for saving the data to S3
- AWS [Glue](#glue)
  - Crawler to create necessary tables
  - Python Shell Job & Trigger for fetching Github stats

### S3 Bucket

- Create an [S3 bucket](https://s3.console.aws.amazon.com/s3/home) with the default settings
  - Feel free to enable "Server access logging" if you want an additional data source :)

### Kinesis

- Setup a [Kinesis data stream](https://console.aws.amazon.com/kinesis/home#/streams/create) with 1 shard
- Setup a [Kinesis Firehose delivery stream](https://console.aws.amazon.com/firehose/home#/wizard/nameAndSource) using the previously-created data stream as the source
  - Select S3 bucket from above as the destination
  - Configure a date-partitioned prefix for the raw data, e.g. `raw/life/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/hour=!{timestamp:HH}/`
  - Configure a prefix for errors, e.g. `kinesisErrors/life/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/hour=!{timestamp:HH}/!{firehose:error-output-type}`
  - Tweak the buffer size and interval as desired - I used 128MB and 900 seconds
  - Enable GZIP compression

### Glue

- Add a Glue Crawler for the Firehose prefix in your S3 bucket: `s3://<bucket>/raw/life/`
  - Schedule it to run every hour
  - On the "Configure the crawler's output" page, ensure that:
    - `Create a single schema for each S3 path` is checked under "Grouping behavior"
    - `Update all new and existing partitions with metadata from the table.` is checked under "Configuration options"

For the Glue job that fetches Github stats data, I'll add more detail soon. :) 
The source code for the Glue job is in [src/github-stats.py](src/github-stats.py) and an [egg file](glue_deps/) needs to be built and uploaded to S3.

## Generating Data

### Website

I currently build and deploy the website in [web](web/) using CodePipeline and CloudFront. This is not required for this demo, but I use it as a source of S3 and CloudFront access logs. :) 

### Laptop metrics

I have a bunch of nerdy metrics that I generate from my laptop, including:
- Unread email count
- Open Chrome tab count
- Open iTerm tab count
- Different system events like lock/unlock
- Source/Destination app for every copy and paste 😳

Currently these are scattered across a few different scripts. Here's how to run them.

#### Email/tab counts

These metrics are collected using AppleScript and just sent up Kinesis using the AWS CLI.

Specify the Kinesis data stream name as an environment variable and, optionally, an AWS profile:

```shell
AWS_PROFILE=profile-name STREAM_NAME=stream-name ./src/macos_data.sh
```

#### Clipboard stats

Collected using a poorly-written shell script. Run the same way as email/tab counts.

```shell
AWS_PROFILE=profile-name STREAM_NAME=stream-name ./src/clipstats.sh
```

## Analyzing the data!

OK, now that we've got data streaming in and it's being stored in S3, let's use [Amazon Athena](https://console.aws.amazon.com/athena/home) to query it!

Take a look at a few example [Athena queries](Notes_Athena.md).

## Resources

- [web](web/) - Public-facing website artifacts
- [src](src/) - AWS Glue Jobs and other scripts
- [glue_deps](glue_deps/) - AWS Glue Python Shell dependencies

### CodePipeline setup

- Need an artifacts bucket and a deployment bucket. Artifacts bucket must be in same region.
- Need to set this up in CF so it deploys to a specific set of resources

## Other ideas

- Real-time web analytics
- Twitter keywords
- Emoji feelings
- Screen brightness (`ioreg -c AppleBacklightDisplay | grep brightness | cut -f2- -d= | sed 's/=/:/g' | jq -c '.brightness'`)
- Failed logins (`log show --style syslog --predicate 'process == "loginwindow"' --debug --info --last 1d | grep "Verify password called with PAM auth set to YES, but pam handle == nil"`)