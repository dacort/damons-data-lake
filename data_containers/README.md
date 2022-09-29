
# Data Containers CDK Python project!

This project is the next iteration of [Damon's Data Lake](https://github.com/dacort/damons-data-lake) that moves fetching of 3rd-party data from a Glue script to Docker containers running in ECS.

I built my own set of container images that are intended to fetch data from remote APIs ([cargo-crates](https://github.com/dacort/cargo-crates)) and then write the data to dynamic paths on S3 using another utility I wrote ([forklift](https://github.com/dacort/forklift)).

I use CDK to build and deploy:
- Scheduled ECS jobs
- Glue Crawler for resulting data

The containers fetch data for the following:
- GitHub traffic stats
- YouTube channel stats
- YouTube video stats 

## Deploying

If you want to use an existing bucket for writing data to, provide the `bucket_name` context variable.

```shell
cdk deploy --all -c bucket_name=data-lake-bucket
```
