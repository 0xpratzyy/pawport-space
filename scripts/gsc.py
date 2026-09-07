#!/usr/bin/env python3
"""Search Console snapshot for pawport.space.
Needs: gcloud auth application-default login --scopes=https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/cloud-platform
Usage: python3 scripts/gsc.py [days]
"""
import json, subprocess, sys, urllib.request, datetime as dt
SITE = "https://pawport.space/"
QUOTA_PROJECT = "gen-lang-client-0171366009"
days = int(sys.argv[1]) if len(sys.argv) > 1 else 28
tok = subprocess.check_output(["gcloud", "auth", "application-default", "print-access-token"], text=True).strip()
def call(path, body=None):
    req = urllib.request.Request(path, data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {tok}", "x-goog-user-project": QUOTA_PROJECT, "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))
end = dt.date.today() - dt.timedelta(days=2)   # GSC lags ~2 days
start = end - dt.timedelta(days=days)
base = f"https://www.googleapis.com/webmasters/v3/sites/{urllib.parse.quote(SITE, safe='')}/searchAnalytics/query"
def q(dims, limit=15):
    return call(base, {"startDate": str(start), "endDate": str(end), "dimensions": dims, "rowLimit": limit}).get("rows", [])
tot = q([], 1)
print(f"Window {start} to {end}")
if tot:
    t = tot[0]; print(f"TOTAL clicks={t['clicks']} impressions={t['impressions']} ctr={t['ctr']*100:.1f}% pos={t['position']:.1f}")
else:
    print("TOTAL: no data")
print("\nDAILY")
for r in q(["date"], 60): print(f"  {r['keys'][0]} clicks={r['clicks']} imp={r['impressions']} pos={r['position']:.0f}")
print("\nTOP QUERIES")
for r in q(["query"]): print(f"  {r['clicks']:>3} clicks {r['impressions']:>5} imp pos {r['position']:>5.1f}  {r['keys'][0]}")
print("\nTOP PAGES")
for r in q(["page"]): print(f"  {r['clicks']:>3} clicks {r['impressions']:>5} imp pos {r['position']:>5.1f}  {r['keys'][0].replace(SITE,'/')}")
print("\nCOUNTRIES")
for r in q(["country"], 8): print(f"  {r['clicks']:>3} clicks {r['impressions']:>5} imp  {r['keys'][0]}")
print("\nSITEMAPS")
for s in call(f"https://www.googleapis.com/webmasters/v3/sites/{urllib.parse.quote(SITE, safe='')}/sitemaps").get("sitemap", []):
    print(f"  {s['path']} lastSubmitted={s.get('lastSubmitted','?')[:10]} errors={s.get('errors')} warnings={s.get('warnings')} contents={[(c['type'],c.get('submitted'),c.get('indexed')) for c in s.get('contents',[])]}")
