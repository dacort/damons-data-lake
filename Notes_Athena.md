# Various Athena queries for my data

## Athena Life Stats Query 

😁

```sql
WITH minute_stats AS (
  SELECT
    from_iso8601_timestamp(ts) AT TIME ZONE 'Europe/London' as ts,
    event,
    MAX(value) as value
  FROM "dcortesi"."dl_life"
  WHERE EVENT IN ('outlook_unread', 'chrome_tabs', 'iterm_tabs')
    AND ts > '' -- We didn't log timestamp initially
    AND from_iso8601_timestamp(ts) >= (current_timestamp - interval '1' day)
  GROUP BY 1, 2
  ORDER BY 1 DESC, 2
)

SELECT
  ts,
  try_cast(kv['outlook_unread'] as integer) AS outlook_unread,
  try_cast(kv['chrome_tabs'] as integer) AS chrome_tabs,
  try_cast(kv['iterm_tabs'] as integer) AS iterm_tabs
FROM (
  SELECT ts, map_agg(event, value) kv
  FROM minute_stats
  GROUP BY ts
) t
ORDER BY 1 DESC
```

## Querying ~~real-time~~ CloudFront logs

```sql
-- Show most recent cloudfront logs
SELECT * FROM "dcortesi"."dl_cloudfront_raw"
ORDER BY concat(date, 'T', time) DESC
limit 100;

-- Find most common user agents
SELECT count(*) as cnt, url_decode(url_decode(useragent)) FROM "dcortesi"."dl_cloudfront_raw"
WHERE uri = '/'
group by 2 order by 1 desc
limit 100;

-- Show requests from my own startup 🤗
SELECT * FROM dl_cloudfront_raw where useragent = 'SMUrlExpander'

-- Use S3 access logs to determine how much CloudFront uploads/downloads
SELECT
  SUM(CAST(bytes_sent AS integer))/1024/1024 AS uploadtotal_mib,
  SUM(CAST(object_size AS integer))/1024/1024 AS downloadtotal_mib,
  SUM(CAST(bytes_sent AS integer) + CAST(object_size AS integer))/1024/1024 AS total_mib
FROM dl_s3_access_optimus
WHERE user_agent = 'Amazon CloudFront'
LIMIT 10

-- Hits today
SELECT time,COUNT(*) AS hits FROM dl_cloudfront_raw
WHERE date = CAST(current_date AS varchar)
GROUP BY 1
ORDER BY 1 DESC
LIMIT 10

```

## Clipboard Stats

```sql
SELECT metadata.clipboard.source, COUNT(*) FROM dl_life
WHERE event = 'clipboard_copy'
GROUP BY 1
ORDER BY 2 DESC;

SELECT metadata.clipboard.destination, COUNT(*) FROM dl_life
WHERE event = 'clipboard_copy'
GROUP BY 1
ORDER BY 2 DESC;

SELECT CONCAT(metadata.clipboard.source, ' --> ', metadata.clipboard.destination), COUNT(*)
FROM dl_life
WHERE event = 'clipboard_copy'
GROUP BY 1
ORDER BY 2 DESC;
```

## Github most-viewed repositories

- Sample data

```sql
SELECT CONCAT(partition_0, '/', partition_1) AS repo, *
FROM "dcortesi"."dl_views"
WHERE cardinality(views) > 0
limit 10;
```

- Top viewed repos

```sql
SELECT CONCAT(partition_0, '/', partition_1) AS repo, sum(count) AS total_views
FROM "dcortesi"."dl_views"
GROUP BY 1 
ORDER BY 2 DESC
LIMIT 10
```

- Views per day per repo

```sql
WITH repo_data AS (
  SELECT CONCAT(partition_0, '/', partition_1) AS repo, views
  FROM "dcortesi"."dl_views"
  WHERE cardinality(views) > 0
)

SELECT repo,
  view_counts.timestamp,
  MAX(view_counts.count) AS count,
  MAX(view_counts.uniques) AS uniques
FROM repo_data
CROSS JOIN UNNEST(views) AS t(view_counts)
GROUP BY 1,2
LIMIT 10
```
