# Pilot operator quick-start (T-CON-13)

The DeepSignal lead approved this non-critical design on November 20 with recorded Astra Ultra concurrence. The combination rehearsal passed 265 of 266 cases and all ten Chromium modules. The missing trusted installer reference was the only failure.

## Fixed target

The opening console README identifies the trusted root-owned installer and links to the canonical install and installed-site verification sections. Operators know that the check uses all the original site options. The guide owns the executable examples. The README identifies the checks for Django and React and UDP. Preserve the current ship settings, browser instructions and demo.

## Acceptance tests

Run through the desk launcher, from the product root, with its DeepSignal Python environment.

```sh
python3 -m pytest -q contrib/deepsignal/test/console/test_operator_quickstart.py contrib/deepsignal/console/install/test_nginx_site.py::test_readme_routes_initial_setup_through_the_relay_gate
python3 -m flake8 --config .flake8 contrib/deepsignal/test/console/test_operator_quickstart.py
```

Prove the old guide handoff fails on the real README. Check both links and their targets. Render the documented HTTP example and a valid HTTPS variation with the packaged renderer. Reject copied or incomplete shell examples, unsupported flags, hidden substitutes and untrusted installer paths. Preserve the baseline install assertion. Retain red and green receipts.

## Prerequisites and scope

Start from the pilot re-cut onto fork integration bff54ec. Only console/README.md and test/console/test_operator_quickstart.py may change. The canonical guide, production code, installer, security owner files, four redesign tickets, ship operations and release decisions are outside this fix.
