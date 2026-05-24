# FORMAT.md

Repo spec format = caveman-compressed Markdown. Use for `SPEC.md` and spec-adjacent notes. Do not use for code, error strings, commit messages, PR descriptions, or user-facing prose that needs normal English.

## Grammar

- Drop articles: a, an, the.
- Drop filler: just, really, basically, simply, actually.
- Drop aux verbs where fragment works: is, are, was, were, being.
- Drop pleasantries and hedging.
- Fragments OK.
- Short words preferred: fix > implement, big > extensive, run > execute.
- Keep any word needed to preserve fact.

## Symbols

```text
→   leads to / becomes / on
∴   therefore / fix
∀   for all / every
∃   exists / some
!   must / required
?   may / optional / unknown
⊥   never / forbidden / nil
≠   not equal
∈   in
∉   not in
≤   at most
≥   at least
&   and
|   or
§   section reference
```

## Preserve Verbatim

- Code blocks, snippets, and inline code.
- Paths: `src/codeforerunner/cli.py`.
- URLs.
- Identifiers: function names, variables, env vars.
- Numbers and versions.
- Error strings.
- SQL, regex, JSON, YAML.
- Quoted strings.

## Shapes

Invariant:

```text
V<n>: <subject> <relation> <condition>
V1: ∀ req → auth check before handler
```

Interface:

```text
<kind>: <name> → <shape>
api: POST /x → 200 {id:string}
cmd: `foo bar <arg>` → stdout JSON
env: FOO_KEY ! set
```

Task row:

```text
id|status|phase|task|cites
T3|x|P1|add auth mw|V1,I.api
```

Status:

```text
x done
~ wip
. todo
```

Bug row:

```text
id|date|cause|fix
B1|2026-04-20|token `<` not `≤`|V2
```

Escape literal `|` in tables as `\|`.

## Boundaries

- External review docs, RFCs, pitches → normal English.
- Commit messages → normal English, 1 line unless user asks otherwise.
- Code comments → normal English.
- Security warnings and irreversible-action confirmations → normal English.
