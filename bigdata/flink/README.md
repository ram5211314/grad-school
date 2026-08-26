# Real-time metrics job

The job accepts UTF-8, pipe-delimited behavior events:

```text
event_time|event_type|program_id|university_name|major_name|keyword
2026-08-25T08:00:00Z|VIEW|3|NUIST|Big Data Technology and Engineering|
2026-08-25T08:00:10Z|FAVORITE|3|NUIST|Big Data Technology and Engineering|
2026-08-25T08:00:15Z|SEARCH||||big data
```

`event_type` supports `SEARCH`, `VIEW`, `FAVORITE`, and `RECOMMENDATION_OPEN`.
Program heat uses weights of 1, 3, and 2 for `VIEW`, `FAVORITE`, and
`RECOMMENDATION_OPEN`. Both metrics use five-minute event-time windows and
allow one minute of out-of-order events.

Run locally:

```powershell
cd bigdata/flink
mvn test
mvn exec:exec -Devents.file=events.txt
```

The job prints `hot-program` and `hot-keyword` metrics. In production, replace
the file source and print sinks with Kafka sources and the selected analytical
sink; event parsing and window aggregation remain unchanged.
