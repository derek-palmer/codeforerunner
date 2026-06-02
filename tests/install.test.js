'use strict';

// Behavior tests for the installer's Task Registry slug loading.
// Run: node --test tests/install.test.js
//
// Scope is deliberately the public, exported surface of bin/install.js
// (slugsFromTasksJson, loadTaskSkillSlugs) plus the observable CLI behavior
// when the registry cannot be read. No internal/private functions are touched,
// so these survive refactors of the install machinery.

const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const os = require('node:os');
const { spawnSync } = require('node:child_process');

const REPO_ROOT = path.resolve(__dirname, '..');
const INSTALL_JS = path.join(REPO_ROOT, 'bin', 'install.js');

const https = require('node:https');

const { slugsFromTasksJson, loadTaskSkillSlugs, fetchRawText, shellEscape } = require(INSTALL_JS);

// Swap https.get for a fake; returns a restore fn. install.js holds the same
// cached https module object, so mutating .get here is visible to fetchRawText.
function stubHttpsGet(handler) {
  const real = https.get;
  https.get = handler;
  return () => { https.get = real; };
}

// Build a minimal response/request pair good enough for fetchRawText.
function fakeExchange({ statusCode, location, body }) {
  return (_url, cb) => {
    const res = {
      statusCode,
      headers: location === undefined ? {} : { location },
      resume() {},
      on(ev, fn) {
        if (ev === 'data' && body != null) process.nextTick(() => fn(body));
        if (ev === 'end') process.nextTick(fn);
        return res;
      },
    };
    process.nextTick(() => cb(res));
    const req = { on() { return req; }, setTimeout() { return req; }, destroy() {} };
    return req;
  };
}

test('slugsFromTasksJson lists the canonical skill slug first', () => {
  const slugs = slugsFromTasksJson(JSON.stringify({
    canonical_skill_slug: 'codeforerunner',
    tasks: [{ name: 'scan', skill_slug: 'forerunner-scan' }],
  }));
  assert.equal(slugs[0], 'codeforerunner');
});

test('slugsFromTasksJson does not repeat a task slug equal to the canonical', () => {
  const slugs = slugsFromTasksJson(JSON.stringify({
    canonical_skill_slug: 'codeforerunner',
    tasks: [
      { name: 'self', skill_slug: 'codeforerunner' },
      { name: 'scan', skill_slug: 'forerunner-scan' },
    ],
  }));
  assert.deepEqual(slugs, ['codeforerunner', 'forerunner-scan']);
});

test('slugsFromTasksJson skips tasks with no skill_slug', () => {
  const slugs = slugsFromTasksJson(JSON.stringify({
    canonical_skill_slug: 'codeforerunner',
    tasks: [
      { name: 'scan', skill_slug: 'forerunner-scan' },
      { name: 'internal', skill_slug: null },
      { name: 'also-internal' },
    ],
  }));
  assert.deepEqual(slugs, ['codeforerunner', 'forerunner-scan']);
});

test('slugsFromTasksJson preserves registry (tasks array) order', () => {
  const slugs = slugsFromTasksJson(JSON.stringify({
    canonical_skill_slug: 'codeforerunner',
    tasks: [
      { name: 'b', skill_slug: 'forerunner-b' },
      { name: 'a', skill_slug: 'forerunner-a' },
      { name: 'c', skill_slug: 'forerunner-c' },
    ],
  }));
  assert.deepEqual(slugs, ['codeforerunner', 'forerunner-b', 'forerunner-a', 'forerunner-c']);
});

test('slugsFromTasksJson throws on malformed JSON', () => {
  assert.throws(() => slugsFromTasksJson('{ not json'));
});

test('slugsFromTasksJson throws when canonical_skill_slug is missing', () => {
  // Mirrors Python's KeyError — a registry with no canonical slug is invalid,
  // not a slug list of [undefined].
  assert.throws(() => slugsFromTasksJson(JSON.stringify({
    tasks: [{ name: 'scan', skill_slug: 'forerunner-scan' }],
  })));
});

test('fetchRawText resolves null on a redirect loop instead of recursing forever', async () => {
  // Every request 301s back to the same URL. Without a cap this overflows the
  // stack / fans out requests unbounded; with a cap it must resolve null.
  const restore = stubHttpsGet(fakeExchange({ statusCode: 301, location: 'https://x/loop' }));
  try {
    const out = await fetchRawText('https://x/loop');
    assert.equal(out, null);
  } finally {
    restore();
  }
});

test('fetchRawText follows a finite redirect chain within the cap and returns the body', async () => {
  // 3 hops (< cap of 5) then a 200 with a body.
  let hops = 0;
  const restore = stubHttpsGet((_url, cb) => {
    const step = hops++;
    const res = {
      statusCode: step < 3 ? 302 : 200,
      headers: step < 3 ? { location: `https://x/hop${step}` } : {},
      resume() {},
      on(ev, fn) {
        if (ev === 'data' && step >= 3) process.nextTick(() => fn('PAYLOAD'));
        if (ev === 'end') process.nextTick(fn);
        return res;
      },
    };
    process.nextTick(() => cb(res));
    const req = { on() { return req; }, setTimeout() { return req; }, destroy() {} };
    return req;
  });
  try {
    assert.equal(await fetchRawText('https://x/start'), 'PAYLOAD');
  } finally {
    restore();
  }
});

test('fetchRawText resolves null on a redirect with no Location header', async () => {
  const restore = stubHttpsGet(fakeExchange({ statusCode: 302, location: undefined }));
  try {
    assert.equal(await fetchRawText('https://x/'), null);
  } finally {
    restore();
  }
});

test('loadTaskSkillSlugs reads the real tasks.json from a local checkout', async () => {
  const slugs = await loadTaskSkillSlugs(REPO_ROOT);
  assert.ok(Array.isArray(slugs) && slugs.length > 0, 'expected a non-empty slug list');
  assert.equal(slugs[0], 'codeforerunner');
  assert.ok(slugs.includes('forerunner-scan'));
});

// ── shellEscape ────────────────────────────────────────────────────────────

test('shellEscape wraps plain string in single quotes', () => {
  assert.equal(shellEscape('claude'), "'claude'");
});

test('shellEscape escapes embedded single quotes', () => {
  // "it's" → 'it'"'"'s'   (end quote, escaped quote, re-open quote)
  assert.equal(shellEscape("it's"), "'it'\\''s'");
});

test('shellEscape output is syntactically valid shell (sh -c)', () => {
  const { spawnSync: spawn } = require('node:child_process');
  for (const input of ['hello', "with spaces", "single'quote", "double\"quote", "semi;colon"]) {
    const quoted = shellEscape(input);
    // printf '%s' <quoted> prints the value without a newline; compare to input.
    const r = spawn('sh', ['-c', `printf '%s' ${quoted}`], { encoding: 'utf8' });
    assert.equal(r.status, 0, `sh syntax error for input: ${JSON.stringify(input)}`);
    assert.equal(r.stdout, input, `round-trip failed for: ${JSON.stringify(input)}`);
  }
});

test('shellEscape output allows command -v to find an existing binary', () => {
  const { spawnSync: spawn } = require('node:child_process');
  // 'sh' is always present; use it as a known-good detection target.
  const r = spawn('sh', ['-c', `command -v ${shellEscape('sh')}`], { stdio: 'ignore' });
  assert.equal(r.status, 0, 'command -v sh should exit 0 with correct shellEscape');
});

// ── CLI dry-run: global install ────────────────────────────────────────────

test('global dry-run passes --agent <profile> --skill * to npx skills add (not --all)', () => {
  // Run with --only cursor since Cursor is always detected (macapp:Cursor on this machine).
  const r = spawnSync(
    process.execPath,
    [INSTALL_JS, '--dry-run', '--global', '--non-interactive', '--no-color', '--only', 'cursor'],
    { encoding: 'utf8' },
  );
  const out = (r.stdout || '') + (r.stderr || '');
  assert.match(out, /--agent cursor/, 'expected --agent cursor in dry-run output');
  assert.match(out, /--skill \*/, 'expected --skill * in dry-run output');
  assert.doesNotMatch(out, /--all/, '--all should not appear (overrides agent filter)');
});

test('global dry-run includes -g flag for npx skills add', () => {
  const r = spawnSync(
    process.execPath,
    [INSTALL_JS, '--dry-run', '--global', '--non-interactive', '--no-color', '--only', 'cursor'],
    { encoding: 'utf8' },
  );
  assert.match((r.stdout || ''), / -g(\s|$)/, 'expected -g flag in global dry-run for skills add');
});

test('local dry-run does NOT pass -g to npx skills add', () => {
  // Local mode calls writeSkillsLocal (direct file writes), not installViaSkills.
  // So -g must never appear in local dry-run output.
  const r = spawnSync(
    process.execPath,
    [INSTALL_JS, '--dry-run', '--local', '--non-interactive', '--no-color'],
    { encoding: 'utf8', cwd: os.tmpdir() },
  );
  assert.doesNotMatch((r.stdout || ''), / -g(\s|$)/, '-g must not appear in local dry-run');
});

// ── CLI dry-run: local install paths ──────────────────────────────────────

test('local dry-run writes to cwd not home dir', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'cfr-test-'));
  try {
    const r = spawnSync(
      process.execPath,
      [INSTALL_JS, '--dry-run', '--local', '--non-interactive', '--no-color'],
      { encoding: 'utf8', cwd: tmpDir },
    );
    const out = r.stdout || '';
    assert.ok(out.includes(tmpDir), `expected cwd (${tmpDir}) in local dry-run output`);
    assert.ok(!out.includes(os.homedir() + path.sep + '.claude'), 'local install must not target home .claude');
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
});

test('local dry-run targets .claude/skills/ and .agents/skills/', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'cfr-test-'));
  try {
    const r = spawnSync(
      process.execPath,
      [INSTALL_JS, '--dry-run', '--local', '--non-interactive', '--no-color'],
      { encoding: 'utf8', cwd: tmpDir },
    );
    const out = r.stdout || '';
    assert.match(out, /\.claude[/\\]skills/, 'expected .claude/skills path in local dry-run');
    assert.match(out, /\.agents[/\\]skills/, 'expected .agents/skills path in local dry-run');
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
});

// ── CLI: --only filter ─────────────────────────────────────────────────────

test('--only with unknown agent id exits non-zero with error', () => {
  const r = spawnSync(
    process.execPath,
    [INSTALL_JS, '--only', 'does-not-exist', '--no-color'],
    { encoding: 'utf8' },
  );
  assert.notEqual(r.status, 0);
  assert.match((r.stderr || ''), /unknown agent/);
});

// ── CLI: non-interactive defaults ─────────────────────────────────────────

test('--non-interactive with --local does not prompt and exits cleanly', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'cfr-test-'));
  try {
    const r = spawnSync(
      process.execPath,
      [INSTALL_JS, '--dry-run', '--local', '--non-interactive', '--no-color'],
      { encoding: 'utf8', cwd: tmpDir },
    );
    assert.equal(r.status, 0);
    assert.match(r.stdout || '', /local install/);
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
});

// ── local install exits non-zero with a clear error when the registry is unreadable ──

test('local install exits non-zero with a clear error when the registry is unreadable', () => {
  // Preload stub: poison every tasks.json read path (local file + HTTPS) so
  // loadTaskSkillSlugs() resolves null, exercising writeSkillsLocal's guard.
  // readFileSync throws (local candidates fail); https.get errors (remote fails).
  const stub = path.join(os.tmpdir(), `cfr-stub-${process.pid}-${Date.now()}.js`);
  fs.writeFileSync(stub, `
    const fs = require('fs');
    // Poison only tasks.json reads — Node's module loader uses readFileSync to
    // load install.js itself, so a blanket stub would crash before our guard runs.
    const realReadFileSync = fs.readFileSync;
    fs.readFileSync = function (p, ...rest) {
      if (typeof p === 'string' && p.includes('tasks.json')) throw new Error('blocked by test stub');
      return realReadFileSync.call(this, p, ...rest);
    };
    const https = require('https');
    https.get = function () {
      const req = {
        on(ev, cb) { if (ev === 'error') process.nextTick(() => cb(new Error('blocked'))); return req; },
        setTimeout() { return req; },
        destroy() {},
      };
      return req;
    };
  `, 'utf8');

  try {
    const res = spawnSync(
      process.execPath,
      ['--require', stub, INSTALL_JS, '--local', '--non-interactive', '--no-color'],
      { encoding: 'utf8', cwd: os.tmpdir() },
    );
    assert.notEqual(res.status, 0, 'expected a non-zero exit');
    assert.match((res.stderr || '') + (res.stdout || ''), /tasks\.json/);
  } finally {
    fs.rmSync(stub, { force: true });
  }
});
