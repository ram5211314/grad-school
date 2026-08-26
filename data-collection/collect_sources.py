"""Fetch configured public sources with provenance snapshots.
This collector intentionally does not invent normalized admissions fields. Parsers must emit
records only after a human-reviewed official catalogue/notice mapping is configured.
"""
from __future__ import annotations
import argparse, hashlib, json, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent

def allowed(host: str, rules: list[str]) -> bool:
    host = (host or "").lower()
    return any(host == r or (r.startswith("*.") and host.endswith(r[1:])) for r in rules)

def fetch(source, policy, snapshots: Path):
    url = source["url"]; host = urlparse(url).hostname
    if not allowed(host, policy["allowedDomains"]):
        return {"id": source["id"], "status": "REJECTED", "reason": "domain not allowlisted"}
    collected_at = datetime.now(timezone.utc).isoformat()
    try:
        request = Request(url, headers={"User-Agent": policy["userAgent"], "Accept": "text/html,application/pdf;q=0.9,*/*;q=0.1"})
        with urlopen(request, timeout=30) as response:
            body = response.read(10 * 1024 * 1024)
            content_type = response.headers.get_content_type()
            final_url = response.url
        digest = hashlib.sha256(body).hexdigest()
        suffix = ".pdf" if content_type == "application/pdf" else ".html"
        file_name = f"{source['id']}-{digest[:12]}{suffix}"
        (snapshots / file_name).write_bytes(body)
        return {"id": source["id"], "name": source["name"], "status": "SNAPSHOT_CAPTURED", "sourceUrl": url, "finalUrl": final_url, "applicableYear": source["applicableYear"], "collectedAt": collected_at, "contentType": content_type, "sha256": digest, "snapshot": f"snapshots/{file_name}", "publicationStatus": "DISCOVERY"}
    except Exception as exc:
        return {"id": source["id"], "name": source["name"], "status": "FAILED", "sourceUrl": url, "collectedAt": collected_at, "reason": str(exc)}

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--config", type=Path, default=ROOT / "sources.json"); parser.add_argument("--out", type=Path, default=ROOT / "runs")
    args = parser.parse_args(); config = json.loads(args.config.read_text(encoding="utf-8")); run = args.out / datetime.now().strftime("%Y%m%d-%H%M%S"); snapshots = run / "snapshots"; snapshots.mkdir(parents=True)
    results = []
    for source in config["sources"]:
        results.append(fetch(source, config["policy"], snapshots)); time.sleep(config["policy"]["requestDelaySeconds"])
    manifest = {"collectorVersion": "0.1", "generatedAt": datetime.now(timezone.utc).isoformat(), "records": results, "normalizedRecords": 0, "note": "Snapshots require source-specific parser mapping and review before publication."}
    (run / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()