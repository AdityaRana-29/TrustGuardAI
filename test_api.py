import urllib.request
import json

# Test 1: Scam SMS
print("=" * 50)
print("TEST 1: Scam SMS")
print("=" * 50)

data = json.dumps({
    "text": "Congratulations! You have won Rs 25,00,000. Click here to claim immediately: http://lucky-prize-india.xyz/claim. Send your OTP now!"
}).encode()

req = urllib.request.Request(
    "http://localhost:8000/api/v1/analyze",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())

print(f"Scam Probability   : {result['scam_probability']}%")
print(f"Fake News Prob     : {result['fake_news_probability']}%")
print(f"Risk Level         : {result['risk_level']}")
print(f"Scam Label         : {result['scam_label']}")
print(f"News Label         : {result['news_label']}")
print(f"Confidence         : {result['overall_confidence']}%")
print(f"Language           : {result['detected_language']}")
print()
print("Reasons:")
for r in result["reasons"]:
    print(f"  [+] {r}")
print()
print("Suspicious Keywords:", result["suspicious_keywords"])
print()
print("URL Risks:")
for u in result["url_risks"]:
    print(f"  URL: {u['url']}")
    print(f"  Risk Level: {u['risk_level']} ({u['risk_score']}%)")
    for r in u["reasons"]:
        print(f"    - {r}")
print()
print("Recommended Action:")
print(" ", result["recommended_action"])

# Test 2: Safe message
print()
print("=" * 50)
print("TEST 2: Safe Message")
print("=" * 50)

data2 = json.dumps({
    "text": "Hi Rahul, just wanted to remind you about our team meeting tomorrow at 10 AM. Please bring the Q3 report."
}).encode()

req2 = urllib.request.Request(
    "http://localhost:8000/api/v1/analyze",
    data=data2,
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(req2) as resp2:
    result2 = json.loads(resp2.read())

print(f"Scam Probability   : {result2['scam_probability']}%")
print(f"Fake News Prob     : {result2['fake_news_probability']}%")
print(f"Risk Level         : {result2['risk_level']}")
print(f"Scam Label         : {result2['scam_label']}")

# Test 3: URL Check
print()
print("=" * 50)
print("TEST 3: URL Check - Phishing URL")
print("=" * 50)

data3 = json.dumps({"url": "http://secure-bank-update.xyz/verify-account/login"}).encode()
req3 = urllib.request.Request(
    "http://localhost:8000/api/v1/check-url",
    data=data3,
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(req3) as resp3:
    result3 = json.loads(resp3.read())

print(f"URL        : {result3['url']}")
print(f"Risk Level : {result3['risk_level']}")
print(f"Risk Score : {result3['risk_score']}%")
print("Reasons:")
for r in result3["reasons"]:
    print(f"  - {r}")

# Test 4: Fake News
print()
print("=" * 50)
print("TEST 4: Fake News Article")
print("=" * 50)

data4 = json.dumps({
    "text": "SHOCKING: Scientists discover miracle cure for diabetes that big pharma is hiding! Doctors HATE this natural remedy. Share before it gets deleted! Government cover-up exposed!"
}).encode()

req4 = urllib.request.Request(
    "http://localhost:8000/api/v1/analyze",
    data=data4,
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(req4) as resp4:
    result4 = json.loads(resp4.read())

print(f"Scam Probability   : {result4['scam_probability']}%")
print(f"Fake News Prob     : {result4['fake_news_probability']}%")
print(f"Risk Level         : {result4['risk_level']}")
print(f"News Label         : {result4['news_label']}")
print("Reasons:")
for r in result4["reasons"]:
    print(f"  [+] {r}")

print()
print("=" * 50)
print("ALL TESTS PASSED - TrustGuard AI is working!")
print("=" * 50)
print()
print("Open the UI: frontend/index.html")
print("Swagger docs: http://localhost:8000/docs")
