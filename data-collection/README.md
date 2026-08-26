# Official public-source collector

Run `py -3 collect_sources.py`. The collector accepts only allowlisted `edu.cn` and `yz.chsi.com.cn` sources, waits between requests, and writes a timestamped raw snapshot plus SHA-256 manifest.

A snapshot is **not** a published admission record. Add a source-specific parser only after confirming the official page/PDF and mapping its year, program fields, and publication status. Imports must include the source name, source URL, applicable year, collection time, and a `PUBLISHED` status before records appear in student search.

Do not use it to bypass robots, access controls, rate limits, copyright restrictions, or pages that prohibit collection.