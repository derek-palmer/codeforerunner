# Keep the source-available license; accept the Socket License-score cap

codeforerunner ships under a homegrown source-available license (the Codeforerunner Source-Available License, SPDX `LicenseRef-Codeforerunner-SAL-0.1`) whose purpose is a commercial moat: it permits personal, internal, and commercial *use* and internal modification, but forbids selling, hosting, or offering the software or its derivatives as a competing product or service. Third-party supply-chain scorecards — Socket.dev in particular — reward OSI/permissive licenses in their License subscore, so a source-available license is structurally capped there regardless of how it is declared.

We evaluated relicensing to lift that subscore and rejected it. A permissive license (MIT/Apache) would raise the score but explicitly permits the fork-rebrand-sell behavior the moat exists to prevent. Copyleft (AGPL) is OSI-recognized but still allows a competing hosted offering as long as source is shared, and brings its own network-copyleft consumer risk — it does not reproduce our intent either. No OSI license reproduces the anti-compete grant, so the capped License subscore is an inherent, accepted cost of the business model, not a defect to fix. We therefore keep the license source-available and instead declare it machine-readably via its SPDX `LicenseRef` id, harvest the genuinely cheap metadata/quality wins, and acknowledge the inherent capability alerts (network/filesystem/process access, all core to an installer) in Socket's own triage rather than chasing them in code.

A future reader who sees a non-OSI license sitting next to a low Socket License subscore should not re-open "why not MIT?": the score cap is known and accepted. If recognition (not subscore) ever becomes the goal, the parked option is migrating the bespoke SAL to a recognized source-available license with a real SPDX id — `PolyForm-Shield-1.0.0` is the closest match to this intent — which is a legal-review decision, not a scorecard one.

## Status

accepted
