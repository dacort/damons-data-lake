import json

from aws_cdk import (
    aws_iam as iam,
    core as cdk,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_glue as glue,
    aws_s3 as s3,
    aws_ecs_patterns as ecs_patterns,
    aws_applicationautoscaling as autoscaling,
    aws_secretsmanager as secrets,
)


class DataContainersStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "MyVpc", max_azs=3)  # default is all AZs in region

        cluster = ecs.Cluster(self, "cargo-crates", vpc=vpc)

        data_bucket = self.get_or_create_bucket("bucket_name")

        github_task = GitHubTraffic(self, cluster).scheduled_task(data_bucket)
        data_bucket.grant_read_write(github_task.task_definition.task_role)

        youtube_task = YouTubeVideo(self, cluster).scheduled_task(data_bucket)
        data_bucket.grant_read_write(youtube_task.task_definition.task_role)

        youtube_channel_task = YouTubeChannel(self, cluster).scheduled_task(data_bucket)
        data_bucket.grant_read_write(youtube_channel_task.task_definition.task_role)

    def get_or_create_bucket(self, context_key) -> s3.Bucket:
        bucket_name = self.node.try_get_context(context_key)
        if bucket_name:
            return s3.Bucket.from_bucket_name(self, "data-bucket", bucket_name)
        else:
            return s3.Bucket(self, "data-bucket")


class GitHubTraffic:
    def __init__(self, stack: cdk.Stack, cluster: ecs.Cluster) -> None:
        self._repos = [
            "awslabs/amazon-athena-cross-account-catalog",
            "awslabs/athena-adobe-datafeed-splitter",
            "awslabs/athena-glue-service-logs",
            "dacort/athena-gmail",
            "dacort/athena-query-stats",
            "dacort/athena-sqlite",
            "dacort/cargo-crates",
            "dacort/damons-data-lake",
            "dacort/demo-code",
            "dacort/forklift",
            "dacort/metabase-athena-driver",
        ]
        self._stack = stack
        self._cluster = cluster

    def scheduled_task(self, s3_bucket: s3.Bucket) -> ecs_patterns.ScheduledFargateTask:
        return ecs_patterns.ScheduledFargateTask(
            self._stack,
            "GitHubTraffic",
            cluster=self._cluster,  # Required
            schedule=autoscaling.Schedule.rate(cdk.Duration.days(1)),
            scheduled_fargate_task_image_options=ecs_patterns.ScheduledFargateTaskImageOptions(
                image=ecs.ContainerImage.from_registry("ghcr.io/dacort/crates-github"),
                command=["traffic", ",".join(self._repos)],
                environment={
                    "FORKLIFT_URI": f'{s3_bucket.s3_url_for_object()}/forklift/github/traffic/{{{{json "path"}}}}/{{{{json "repo"}}}}/{{{{today}}}}.json'
                },
                secrets={
                    "GITHUB_PAT": ecs.Secret.from_secrets_manager(
                        secrets.Secret.from_secret_name_v2(
                            self._stack, "GitHubPAT", "ddl/github_pat"
                        )
                    )
                },
            ),
        )


class YouTubeVideo:
    def __init__(self, stack: cdk.Stack, cluster: ecs.Cluster) -> None:
        self._stack = stack
        self._cluster = cluster
        self._video_ids = [
            "avXbYBPzpIE",  # EMR on EKS Online Tech Talk
            "oVgyL5W9FPU",  # Intro to EMR Studio (personal)
            "rZ3zeJ6WKPY",  # Intro to EMR Studio (AWS),
            "apgCbmX68VI",  # What is EMR on EKS?
            "MTim5ifjYiE",  # Running jobs on EMR on EKS
            "73PFjhMkNYw",  # Metastores w/EMR on EKS
            "NnePXN-0geQ",  # Airflow w/EMR on EKS
            "9nJ1n4rUzX8",  # Optimizing EMR on EKS jobs
            "3cW6e64YRdY",  # EMR Studio Online Tech Talk
            "0x4DRKmNPfQ",  # EMR on EKS Custom Images
        ]

    def scheduled_task(self, s3_bucket: s3.Bucket) -> ecs_patterns.ScheduledFargateTask:
        return ecs_patterns.ScheduledFargateTask(
            self._stack,
            "YouTubeVideo",
            cluster=self._cluster,
            schedule=autoscaling.Schedule.rate(cdk.Duration.days(1)),
            scheduled_fargate_task_image_options=ecs_patterns.ScheduledFargateTaskImageOptions(
                image=ecs.ContainerImage.from_registry("ghcr.io/dacort/crates-youtube"),
                command=["videos", ",".join(self._video_ids)],
                environment={
                    "FORKLIFT_URI": f"{s3_bucket.s3_url_for_object()}/forklift/youtube/{{{{today}}}}.json"
                },
                secrets={
                    "YOUTUBE_API_KEY": ecs.Secret.from_secrets_manager(
                        secrets.Secret.from_secret_name_v2(
                            self._stack, "YouTubeAPIKey", "ddl/youtube_api_key"
                        )
                    )
                },
            ),
        )


class YouTubeChannel:
    def __init__(self, stack: cdk.Stack, cluster: ecs.Cluster) -> None:
        self._stack = stack
        self._cluster = cluster
        self._channel_id = "UCKtlXVZC2DqzayRlZYLObZw"

    def scheduled_task(self, s3_bucket: s3.Bucket) -> ecs_patterns.ScheduledFargateTask:
        return ecs_patterns.ScheduledFargateTask(
            self._stack,
            "YouTubeChannel",
            cluster=self._cluster,
            schedule=autoscaling.Schedule.rate(cdk.Duration.hours(1)),
            scheduled_fargate_task_image_options=ecs_patterns.ScheduledFargateTaskImageOptions(
                image=ecs.ContainerImage.from_registry("ghcr.io/dacort/crates-youtube"),
                command=["channel_videos", self._channel_id],
                environment={
                    "FORKLIFT_URI": f"{s3_bucket.s3_url_for_object()}/forklift/youtube_channel/{{{{today}}}}.json"
                },
                secrets={
                    "YOUTUBE_API_KEY": ecs.Secret.from_secrets_manager(
                        secrets.Secret.from_secret_name_v2(
                            self._stack, "YouTubeChannelAPIKey", "ddl/youtube_api_key"
                        )
                    )
                },
            ),
        )


class GlueStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        db = glue.Database(self, "DamonsDataLake", database_name="damons_datalake")

        s3_bucket = get_or_create_bucket(self, "glue-data-bucket", "bucket_name")
        glue_crawler = iam.Role(
            self,
            "glue-crawler-role",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSGlueServiceRole"
                )
            ],
        )
        s3_bucket.grant_read(glue_crawler)

        crawler = glue.CfnCrawler(
            self,
            "data-lake-crawler",
            role=glue_crawler.role_arn,
            database_name=db.database_name,
            targets=glue.CfnCrawler.TargetsProperty(
                s3_targets=[
                    glue.CfnCrawler.S3TargetProperty(
                        path=s3_bucket.s3_url_for_object("forklift/youtube"),
                    ),
                    glue.CfnCrawler.S3TargetProperty(
                        path=s3_bucket.s3_url_for_object("forklift/github/traffic"),
                    ),
                    glue.CfnCrawler.S3TargetProperty(
                        path=s3_bucket.s3_url_for_object("forklift/youtube_channel"),
                    ),
                ]
            ),
            configuration=json.dumps(
                {
                    "Version": 1.0,
                    "Grouping": {"TableGroupingPolicy": "CombineCompatibleSchemas"},
                    "CrawlerOutput": {
                        "Partitions": {"AddOrUpdateBehavior": "InheritFromTable"}
                    },
                }
            ),
        )


def get_or_create_bucket(
    stack: cdk.Stack, bucket_id: str, context_key: str = None
) -> s3.Bucket:
    if context_key is None or stack.node.try_get_context(context_key) is None:
        return s3.Bucket(
            stack,
            bucket_id,
        )
    else:
        bucket_name = stack.node.try_get_context(context_key)
        return s3.Bucket.from_bucket_name(stack, bucket_id, bucket_name)
