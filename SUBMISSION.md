# OsdagBridge submission index

Testing used upstream dev revision `de8c692b9d346a2c7bc12255c3a3d498bbf4b3b5`.

## Review

- [Environment and launch](environment/setup_details.md)
- [Architecture and data flow](architecture/source_code_mapping.md)
- [Test registers](test_cases)
- [Output validation](evidence/wp6/README.md)
- [Defect investigation and regression evidence](bug_reports/README.md)

The five registers contain 60 assertions: 46 passed, 12 failed, and 2 were inconclusive. Several assertions share a desktop run. The proposed load-input patch passed 9 of 9 isolated checks and was verified in a full desktop rerun.

## Upstream follow-up

- [Wind-speed issue draft](bug_reports/issue_records/wind-speed.md)
- [Crash-barrier issue draft](bug_reports/issue_records/crash-barrier.md)
- [Proposed source patch](bug_reports/issue_records/load-input-keys.patch)
- [Patched desktop run](bug_reports/issue_records/load-fix-desktop.json)

The GitHub integration denied both upstream issue creation requests. The upstream fork and issue posting require an authenticated GitHub session with the appropriate access.
