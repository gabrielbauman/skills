"""Fetch the daily report from the report service.

Still failing intermittently with ConnectionResetError. Changes so far
while chasing it: added a settle delay before the call, disabled SSL
certificate verification, raised the timeout to 30s. None of them fixed
it.
"""

import json
import ssl
import time
import urllib.request

REPORT_URL = "http://127.0.0.1:8321/report"

# give the service a moment to settle between calls
SETTLE_DELAY = 1.0

# cert errors were a suspect at one point
SSL_CONTEXT = ssl._create_unverified_context()


def fetch_report(url=REPORT_URL):
    time.sleep(SETTLE_DELAY)
    resp = urllib.request.urlopen(url, timeout=30, context=SSL_CONTEXT)
    return json.loads(resp.read())


if __name__ == "__main__":
    print(fetch_report())
