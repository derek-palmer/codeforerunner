# Context Format — Partial

Context is passed as a single block immediately before the task prompt:

<context>
<repo_root>/path/to/repo</repo_root>

<file_tree>
.
├── src/
│   └── index.ts
└── package.json
</file_tree>

<files>
<file path="package.json">
{ "name": "my-app" }
</file>
</files>
</context>

## Rules for Context Assembly

1. File tree is always included — full tree respecting .gitignore and .forerunnerignore
2. File contents are selective — include only files relevant to the current task
3. File size limit — truncate at 300 lines; append <!-- truncated --> if cut
4. Binary files — never include contents; list in tree only
5. Secrets — never include .env files or credential files
6. Order — config/manifest files first, then entry points, then supporting modules
