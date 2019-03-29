# My own personal Data Lake :cringe:

## Overview

Step 1: Build a personal website that describes who I am and what I do.
Step 2: Deploy this to S3 and front it with CloudFront
Step 3: Log all this data to S3 :)
Step 4: Ingest it using my own library
Step 5: Ingest external data from Github, Twitter, internal, etc

Site will have links to demo code, github repos, etc.
Maybe we even put an event tracker on the site?

Then we use several pieces of tech to munge everything together:
- Amazon Kinesis
- AWS Step Functions
- AWS Glue
- Amazon Athena

It'd be great to have the site be interactive, or a useful resource somehow. 
People won't visit unless there is something of value.

- Polls?
- My favorite Data Eng posts?
- Ideas that people can submit/vote up? (should just be github)

Would be fun to use in demos, also people could send me an "alert" or if enough people visited...

## Supported Data Sources

- Server
  - Kinesis [web analytics](https://github.com/awslabs/real-time-web-analytics-with-kinesis)
  - [x] S3 Access
  - ELB
  - [x] CloudFront
  - Should have an RDBMS somewhere...
- Social
  - Twitter
  - [x] Github Commits & Traffic Stats
  - [x] Email volume? (`osascript -e 'tell application "Microsoft Outlook" to unread count of folder "Inbox" of default account'`)
  - Emoji feelings?
- AWS
  - Athena queries per day
  - EMR clusters per day
- Random
  - Chrome tabs open (`osascript -e 'tell application "Google Chrome" to count every tab of every window'`)
  - Screen brightness (`ioreg -c AppleBacklightDisplay | grep brightness | cut -f2- -d= | sed 's/=/:/g' | jq -c '.brightness'`)
  - Failed logins (`log show --style syslog --predicate 'process == "loginwindow"' --debug --info --last 1d | grep "Verify password called with PAM auth set to YES, but pam handle == nil"`)

## Providing access to your customers

Do I want to make this data publicly available? Seems like it could be tough...

## Also...what questions am I trying to answer? :)

- Where do people access my site from?
- How popular are my different repos?

## Resources

- [web](web/) - Public-facing website artifacts
- [src](src/) - AWS Glue Jobs and other scripts
- [glue_deps](glue_deps/) - AWS Glue Python Shell dependencies

## TODO/Notes

### CodePipeline setup

- Need an artifacts bucket and a deployment bucket. Artifacts bucket must be in same region.
- Need to set this up in CF so it deploys to a specific set of resources