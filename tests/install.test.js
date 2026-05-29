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

const { slugsFromTasksJson, loadTaskSkillSlugs } = require(INSTALL_JS);

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

test('loadTaskSkillSlugs reads the real tasks.json from a local checkout', async () => {
  const slugs = await loadTaskSkillSlugs(REPO_ROOT);
  assert.ok(Array.isArray(slugs) && slugs.length > 0, 'expected a non-empty slug list');
  assert.equal(slugs[0], 'codeforerunner');
  assert.ok(slugs.includes('forerunner-scan'));
});

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
