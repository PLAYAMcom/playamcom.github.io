#!/usr/bin/env python3
"""Safe, offline checks for the Report Player frontend. No Supabase calls are made."""
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import tempfile

HTML = Path("index.html").read_text(encoding="utf-8")
MOCK_HTML = Path("tests/report-player-isolated.html").read_text(encoding="utf-8")
ADMIN_HTML = Path("admin playam .html").read_text(encoding="utf-8")
STAGING_ADMIN_HTML = Path("admin-playam-staging.html").read_text(encoding="utf-8")

class Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_script = False
        self.external = False
        self.current = []
        self.items = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "script":
            self.in_script = True
            self.external = any(k.lower() == "src" for k, _ in attrs)
            self.current = []
    def handle_data(self, data):
        if self.in_script and not self.external:
            self.current.append(data)
    def handle_endtag(self, tag):
        if tag.lower() == "script" and self.in_script:
            if not self.external:
                self.items.append("".join(self.current))
            self.in_script = False
            self.external = False

parser = Scripts()
parser.feed(HTML)
assert parser.items, "No inline JavaScript blocks found"

required = {
    "report dialog": 'id="reportPlayerOverlay"',
    "report target selector": 'id="reportTarget"',
    "report reason selector": 'id="reportReason"',
    "report details field": 'id="reportDetails"',
    "report submit button": 'id="submitReportButton"',
    "room-target RPC": "list_room_report_targets",
    "report-submit RPC": "submit_player_report",
    "details length guard": "details.length>2000",
    "submission lock": "if(reportSubmitting)return",
    "success duplicate guard": "reportSubmitted",
    "Escape-key close": 'event.key==="Escape"',
}
for label, needle in required.items():
    if needle not in HTML:
        raise SystemExit(f"FAIL: missing {label} ({needle})")

admin_required = {
    "MFA assurance-level gate": "currentLevel==='aal2'",
    "TOTP enrollment": "mfa.enroll({factorType:'totp'",
    "MFA challenge": "mfa.challenge({factorId:mfaFactorId})",
    "MFA verification": "mfa.verify({factorId:mfaFactorId,challengeId:mfaChallengeId,code})",
    "dashboard MFA panel": 'id="mfaPanel"',
}
for label, needle in admin_required.items():
    if needle not in ADMIN_HTML:
        raise SystemExit(f"FAIL: admin dashboard missing {label} ({needle})")

if "erjxmesxmmmaxivvmbsi.supabase.co" in STAGING_ADMIN_HTML or "sb_publishable_8GZmo3tsiGphFbgsCmbdgA_A7blmyc0" in STAGING_ADMIN_HTML:
    raise SystemExit("FAIL: staging admin page contains production Supabase configuration")
if "https://pwnjrdedeoxbmtfywhkk.supabase.co" not in STAGING_ADMIN_HTML:
    raise SystemExit("FAIL: staging admin page is not configured for the PLAYAM-Staging project")
if "const SUPABASE_KEY='sb_publishable_" not in STAGING_ADMIN_HTML:
    raise SystemExit("FAIL: staging admin page is missing a publishable-key configuration")
if "__PLAYAM_STAGING_PROJECT_URL__" in STAGING_ADMIN_HTML or "__PLAYAM_STAGING_PUBLISHABLE_KEY__" in STAGING_ADMIN_HTML:
    raise SystemExit("FAIL: staging admin page still contains configuration placeholders")
for label, needle in {
    "fail-closed staging configuration": "if(!stagingConfigReady)",
    "AAL2 gate": "currentLevel==='aal2'",
}.items():
    if needle not in STAGING_ADMIN_HTML:
        raise SystemExit(f"FAIL: staging admin page missing {label} ({needle})")

staging_parser = Scripts()
staging_parser.feed(STAGING_ADMIN_HTML)
assert staging_parser.items, "No inline JavaScript in staging admin dashboard"
for i, source in enumerate(staging_parser.items, 1):
    with tempfile.NamedTemporaryFile("w", suffix=f"-staging-admin-{i}.js", encoding="utf-8") as tmp:
        tmp.write(source)
        tmp.flush()
        result = subprocess.run(["node", "--check", tmp.name], text=True, capture_output=True)
    if result.returncode:
        raise SystemExit(f"FAIL: staging admin script {i} has a JavaScript syntax error:\\n{result.stderr}")

admin_parser = Scripts()
admin_parser.feed(ADMIN_HTML)
assert admin_parser.items, "No inline JavaScript in admin dashboard"
for i, source in enumerate(admin_parser.items, 1):
    with tempfile.NamedTemporaryFile("w", suffix=f"-admin-{i}.js", encoding="utf-8") as tmp:
        tmp.write(source)
        tmp.flush()
        result = subprocess.run(["node", "--check", tmp.name], text=True, capture_output=True)
    if result.returncode:
        raise SystemExit(f"FAIL: admin dashboard script {i} has a JavaScript syntax error:\n{result.stderr}")

for i, source in enumerate(parser.items, 1):
    with tempfile.NamedTemporaryFile("w", suffix=f"-{i}.js", encoding="utf-8") as tmp:
        tmp.write(source)
        tmp.flush()
        result = subprocess.run(["node", "--check", tmp.name], text=True, capture_output=True)
    if result.returncode:
        raise SystemExit(f"FAIL: inline script {i} has a JavaScript syntax error:\\n{result.stderr}")

mock_parser = Scripts()
mock_parser.feed(MOCK_HTML)
assert mock_parser.items, "No inline JavaScript in isolated mock page"
for i, source in enumerate(mock_parser.items, 1):
    with tempfile.NamedTemporaryFile("w", suffix=f"-mock-{i}.js", encoding="utf-8") as tmp:
        tmp.write(source)
        tmp.flush()
        result = subprocess.run(["node", "--check", tmp.name], text=True, capture_output=True)
    if result.returncode:
        raise SystemExit(f"FAIL: isolated mock script {i} has a JavaScript syntax error:\\n{result.stderr}")

print(f"PASS: {len(parser.items)} main app inline JavaScript block(s) parsed successfully.")
print(f"PASS: {len(admin_parser.items)} admin dashboard inline JavaScript block(s) parsed successfully.")
print(f"PASS: {len(staging_parser.items)} staging admin JavaScript block(s) parsed successfully.")
print("PASS: staging admin has no production Supabase configuration and fails closed until configured.")
print(f"PASS: {len(admin_required)} admin MFA checks passed.")
print(f"PASS: {len(mock_parser.items)} isolated mock JavaScript block(s) parsed successfully.")
print(f"PASS: {len(required)} Report Player wiring/safety checks passed.")
print("NOTE: These are static checks only; they do not submit reports or contact Supabase.")
