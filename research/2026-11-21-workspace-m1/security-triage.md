# Workspace Linux security gate: unresolved

Candidate: 58fbde8cb9cbab0b4a77ee25042fd9a9169d4615.
Workflow: 44879804326, source ebe454df6547a99e33862432f5d80f5bfc230f18.
Unchanged approved policy source: desk460914c40ec02ddb8509be1994d5642174937469.
Policy verdict FAIL: unlisted finding in contrib/deepsignal/workspace/browser_smoke.py.
This is source triage, not independent review, policy acceptance or release approval.

Raw221 findings include33 in new workspace files:

- B101 LOW,30 occurrences in mcp_smoke.py: assertions are test oracles. Python
  optimization can remove them; review how to keep acceptance checks mandatory.
  Do not silently exclude the smoke file or change the scanner gate.
- B404 LOW at browser_smoke.py:7 and B603 LOW at26: subprocess import and launch.
  Source uses a list with no shell, explicit operator-provided server Python,
  fixed module and owned temporary state. Verify trusted interpreter selection,
  inherited environment, timeout and owned process cleanup during review.
- B310 MEDIUM at browser_smoke.py:34: readiness URL uses a constructed loopback
  HTTP base and bounded timeout. Review redirect/proxy behavior and endpoint
  restriction rather than treating a fixed initial URL as complete assurance.

No finding disposition is auto-approved here. Preserve raw scan, original FAIL
and tests. Any source repair needs its affected Relay checks and exact Linux gate;
any exception needs the governing independent review/approval process. Do not
move harnesses or suppress findings merely to change the count. The remaining188
findings are outside the new workspace; this is not a fresh risk review of them.

Artifact: workspace-security-evidence, id14696948453. Private saved raw/policy:
/private/tmp/deepsignal/product-m1-evidence/linux-44879804326/workspace-security-evidence/.
Raw envelope SHA256 c3eda651f14865ac286d2e890defa9dc05e814c3c8a407eddc15b1ed790e7841.
Policy SHA256 4a83d80929ea3111f6d410b232866769acf55b090d5db26087071a32586833b9.
The separate workspace job passed. Whole-module science/security/usability review,
real OpenRVDAS demo and full scope remain incomplete.

## Follow-up at6cba5716, Linux44881969262

Affected harness checks PASS. Unchanged policy FAIL remains with190 total findings
and2 workspace findings: B404/B603 subprocess import/call in browser_smoke.py.
The30 B101 removable checks are now mandatory, proven RED then PASS under Python
-O through actual SDK. B310 readiness now uses fixed-host HTTPConnection with no
proxy/redirect handling. No nosec, excluded path, policy or severity change.
Raw envelope SHA256265e6385d67bd58da8f3e7d67c24204a14e6c6a08bb7ebc6dfdb158de8f50348.
Full independent security disposition remains pending; fewer findings is not
production security qualification. New read-only mode is a separate source change.

## Read-only analysis follow-up

Linux44883447788 atce22f377: affected harness PASS; unchanged policy FAIL. Raw scan190 total,2 workspace findings B404/browser_smoke.py:9 and B603/browser_smoke.py:27, both LOW. Raw envelope SHA25609152353b6b9f1e852883f45569d3a0841494c05b517f715217aaddf50af7dd6. No suppression, policy change or independent disposition. Original raw artifacts retained under product-m1-evidence/linux-44883447788.

Final candidate6dec349867ab5c3bb6033824481c0da290409a0e Linux44884254104: affected checks including repository style PASS. Unchanged security policy FAIL;190 findings total,2 workspace B404 atbrowser_smoke.py:10 and B603 at:28, both LOW. Raw envelope SHA25637b78f044e469271ac86b6657800b0acc924ee10c9ac513fdd7202b94df33daf. Findings remain unresolved; see adjacent scan summary and job snapshot.
