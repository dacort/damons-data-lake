import datetime
import json
import sys

# boto3 modules are apparently already present in sys.modules when this script runs.
# Because we need a new version of boto3 to be able to use secretsmanager, we need to
# clear out any boto3 and botocore-related modules before we import.
module_keys = sys.modules.keys()  # Otherwise, we get an error about the dict changing
for key in module_keys:
    if key.startswith("boto3") or key.startswith("botocore"):
        print("Deleting " + key)
        del sys.modules[key]


import os
import boto3
import requests
from awsglue.utils import getResolvedOptions

JOB_ARGS = getResolvedOptions(sys.argv, ['sekret', 'bucket', 'prefix'])

# --------------------------------------------------
# Helper functions to retrieve environment variables
# --------------------------------------------------
def get_region():
    return os.environ.get('AWS_DEFAULT_REGION')

def get_job_arg(name):
    return JOB_ARGS.get(name)

def get_secret():
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        'secretsmanager',
        region_name=get_region()
    )


    get_secret_value_response = client.get_secret_value(
        SecretId=get_job_arg('sekret')
    )

    return json.loads(get_secret_value_response['SecretString'])['github_pat']

def save_results(bucket, key, value):
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, key)
    obj.put(Body=json.dumps(value))
    
github_repos = ['dacort/athena-query-stats', 'awslabs/athena-glue-service-logs', 'awslabs/athena-adobe-datafeed-splitter', 'dacort/demo-code', 'dacort/sample-code', 'dacort/syslog-to-athena', 'dacort/damons-data-lake']
traffic_endpoints = ['popular/referrers', 'popular/paths', 'views', 'clones']

for repo in github_repos:
    for endpoint in traffic_endpoints:
        url = 'https://api.github.com/repos/' + repo + '/traffic/' + endpoint
        headers = {'Authorization': "token " + get_secret()}
        r = requests.get(url, headers=headers)
        if(r.ok):
            events = json.loads(r.text or r.content)
            # Only write out the file if we got any useful data
            if events:
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                s3_key = '%s/%s/%s/%s.json' % (get_job_arg('prefix'), endpoint.replace('popular/', 'traffic/'), repo, today)
                save_results(get_job_arg('bucket'), s3_key, events)
        else:
            # TODO: Error handling :)
            print(r)
