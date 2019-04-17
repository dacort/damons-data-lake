# Athena Life Stats Query 

😁

```sql
WITH minute_stats AS (
  SELECT
    from_iso8601_timestamp(ts) AT TIME ZONE 'America/Los_Angeles' as ts,
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