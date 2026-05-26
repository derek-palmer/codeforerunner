#!/usr/bin/env node
// codeforerunner — unified cross-platform installer.
//
// Installs forerunner's prompt-pack skills into every detected agent CLI
// so documentation slash commands (/forerunner-scan, /forerunner-readme,
// etc.) are available without a separate API key.
//
// Distribution:
//   Local clone:  node bin/install.js [flags]
//   curl|bash:    delegated from install.sh shim → npx -y github:derek-palmer/codeforerunner -- [flags]
//   Windows:      pwsh install.ps1 [flags] → same npx delegation
//
// Pure stdlib, zero npm runtime deps.
// Modelled on JuliusBrussee/caveman bin/install.js.

'use strict';

const fs             = require('fs');
const os             = require('os');
const path           = require('path');
const child_process  = require('child_process');

const REPO     = 'derek-palmer/codeforerunner';
const RAW_BASE = `https://raw.githubusercontent.com/${REPO}/main`;

// ── Argv ──────────────────────────────────────────────────────────────────

function parseArgs(argv) {
  const opts = {
    dryRun: false, force: false, skipSkills: false,
    all: false, minimal: false, listOnly: false, noColor: false,
    only: [], uninstall: false, help: false,
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    switch (a) {
      case '--dry-run':   opts.dryRun   = true;  break;
      case '--force':     opts.force    = true;  break;
      case '--skip-skills': opts.skipSkills = true; break;
      case '--all':       opts.all      = true;  break;
      case '--minimal':   opts.minimal  = true;  break;
      case '--list':      opts.listOnly = true;  break;
      case '--no-color':  opts.noColor  = true;  break;
      case '--uninstall': case '-u': opts.uninstall = true; break;
      case '-h': case '--help': opts.help = true; break;
      case '--': break; // npx may forward a literal --
      case '--only': {
        const v = argv[++i];
        if (!v) die('error: --only requires an argument');
        opts.only.push(v);
        break;
      }
      default:
        die(`error: unknown flag: ${a}\nrun with --help for usage`);
    }
  }
  if (opts.all && opts.minimal) die('error: --all and --minimal are mutually exclusive');
  if (opts.only.length) {
    const known = new Set(PROVIDERS.map(p => p.id));
    for (const id of opts.only) {
      if (!known.has(id)) die(`error: unknown agent: ${id}\n  see --list for valid ids`);
    }
  }
  return opts;
}

function die(msg) { process.stderr.write(msg + '\n'); process.exit(2); }

// ── Color helpers ─────────────────────────────────────────────────────────

function makeChalk(noColor) {
  const use = !noColor && process.stdout.isTTY && !process.env.NO_COLOR;
  const wrap = (c) => (s) => use ? `\x1b[${c}m${s}\x1b[0m` : s;
  return {
    green:  wrap('32'),
    yellow: wrap('33'),
    red:    wrap('31'),
    dim:    wrap('2'),
    bold:   wrap('1'),
    cyan:   wrap('36'),
  };
}

// ── Provider matrix ───────────────────────────────────────────────────────
// Same detection rules as caveman/bin/install.js:
//   command:<bin>          — binary on PATH
//   dir:<path>             — directory exists (soft-only; avoid false positives)
//   file:<path>            — file exists
//   macapp:<Name>          — /Applications/<Name>.app present
//   vscode-ext:<needle>    — VS Code / Cursor / Windsurf extension dir match
//   cursor-ext:<needle>    — Cursor extension dir match only
//   jetbrains-plugin:<n>   — JetBrains plugin dir walk
//
// `soft: true` → excluded from auto-detect; only installs with --only <id>.
// `profile`    → npx skills add profile slug (https://github.com/vercel-labs/skills)

const PROVIDERS = [
  { id: 'claude',      label: 'Claude Code',          mech: 'claude plugin install',           detect: 'command:claude' },
  { id: 'gemini',      label: 'Gemini CLI',           mech: 'gemini extensions install',       detect: 'command:gemini' },
  { id: 'opencode',    label: 'opencode',             mech: 'npx skills add (opencode)',        detect: 'command:opencode',        profile: 'opencode' },
  { id: 'codex',       label: 'Codex CLI',            mech: 'npx skills add (codex)',           detect: 'command:codex',           profile: 'codex' },

  { id: 'cursor',      label: 'Cursor',               mech: 'npx skills add (cursor)',          detect: 'command:cursor||macapp:Cursor',   profile: 'cursor' },
  { id: 'windsurf',    label: 'Windsurf',             mech: 'npx skills add (windsurf)',        detect: 'command:windsurf||macapp:Windsurf', profile: 'windsurf' },
  { id: 'cline',       label: 'Cline',                mech: 'npx skills add (cline)',           detect: 'vscode-ext:cline',        profile: 'cline' },
  { id: 'continue',    label: 'Continue',             mech: 'npx skills add (continue)',        detect: 'vscode-ext:continue.continue||vscode-ext:continue', profile: 'continue' },
  { id: 'kilo',        label: 'Kilo Code',            mech: 'npx skills add (kilo)',            detect: 'vscode-ext:kilocode',     profile: 'kilo' },
  { id: 'roo',         label: 'Roo Code',             mech: 'npx skills add (roo)',             detect: 'vscode-ext:roo||vscode-ext:rooveterinaryinc.roo-cline||cursor-ext:roo', profile: 'roo' },
  { id: 'augment',     label: 'Augment Code',         mech: 'npx skills add (augment)',         detect: 'vscode-ext:augment||jetbrains-plugin:augment', profile: 'augment' },

  { id: 'copilot',     label: 'GitHub Copilot',       mech: 'npx skills add (github-copilot)', detect: 'command:copilot',         profile: 'github-copilot', soft: true },

  { id: 'aider-desk',  label: 'Aider Desk',           mech: 'npx skills add (aider-desk)',      detect: 'command:aider',           profile: 'aider-desk' },
  { id: 'amp',         label: 'Sourcegraph Amp',      mech: 'npx skills add (amp)',             detect: 'command:amp',             profile: 'amp' },
  { id: 'bob',         label: 'IBM Bob',              mech: 'npx skills add (bob)',             detect: 'command:bob',             profile: 'bob' },
  { id: 'crush',       label: 'Crush',                mech: 'npx skills add (crush)',           detect: 'command:crush',           profile: 'crush' },
  { id: 'devin',       label: 'Devin (terminal)',     mech: 'npx skills add (devin)',           detect: 'command:devin',           profile: 'devin' },
  { id: 'droid',       label: 'Droid (Factory)',      mech: 'npx skills add (droid)',           detect: 'command:droid',           profile: 'droid' },
  { id: 'forgecode',   label: 'ForgeCode',            mech: 'npx skills add (forgecode)',       detect: 'command:forge',           profile: 'forgecode' },
  { id: 'goose',       label: 'Block Goose',          mech: 'npx skills add (goose)',           detect: 'command:goose',           profile: 'goose' },
  { id: 'iflow',       label: 'iFlow CLI',            mech: 'npx skills add (iflow-cli)',       detect: 'command:iflow',           profile: 'iflow-cli' },
  { id: 'kiro',        label: 'Kiro CLI',             mech: 'npx skills add (kiro-cli)',        detect: 'command:kiro',            profile: 'kiro-cli' },
  { id: 'mistral',     label: 'Mistral Vibe',         mech: 'npx skills add (mistral-vibe)',    detect: 'command:mistral',         profile: 'mistral-vibe' },
  { id: 'openhands',   label: 'OpenHands',            mech: 'npx skills add (openhands)',       detect: 'command:openhands',       profile: 'openhands' },
  { id: 'qwen',        label: 'Qwen Code',            mech: 'npx skills add (qwen-code)',       detect: 'command:qwen',            profile: 'qwen-code' },
  { id: 'rovodev',     label: 'Atlassian Rovo Dev',   mech: 'npx skills add (rovodev)',         detect: 'command:rovodev',         profile: 'rovodev' },
  { id: 'tabnine',     label: 'Tabnine CLI',          mech: 'npx skills add (tabnine-cli)',     detect: 'command:tabnine',         profile: 'tabnine-cli' },
  { id: 'trae',        label: 'Trae',                 mech: 'npx skills add (trae)',            detect: 'command:trae',            profile: 'trae' },
  { id: 'warp',        label: 'Warp',                 mech: 'npx skills add (warp)',            detect: 'command:warp',            profile: 'warp' },
  { id: 'replit',      label: 'Replit Agent',         mech: 'npx skills add (replit)',          detect: 'command:replit',          profile: 'replit' },

  { id: 'junie',       label: 'JetBrains Junie',      mech: 'npx skills add (junie)',           detect: 'jetbrains-plugin:junie',  profile: 'junie',       soft: true },
  { id: 'qoder',       label: 'Qoder',                mech: 'npx skills add (qoder)',           detect: 'dir:$HOME/.qoder',        profile: 'qoder',       soft: true },
  { id: 'antigravity', label: 'Google Antigravity',   mech: 'npx skills add (antigravity)',     detect: 'dir:$HOME/.gemini/antigravity', profile: 'antigravity', soft: true },
];

// ── Detection helpers ─────────────────────────────────────────────────────

const IS_WIN = process.platform === 'win32';

function shellEscape(s) { return `'${String(s).replace(/'/g, `'\\''`)}`; }

function expandHome(p) {
  return String(p).replace(/^\$HOME(?=\/|$)/, os.homedir()).replace(/^~(?=\/|$)/, os.homedir());
}

function hasCmd(cmd) {
  try {
    if (IS_WIN) {
      return child_process.spawnSync('where', [cmd], { stdio: 'ignore' }).status === 0;
    }
    return child_process.spawnSync('sh', ['-c', `command -v ${shellEscape(cmd)}`], { stdio: 'ignore' }).status === 0;
  } catch (_) { return false; }
}

function safeStat(p, method) {
  try { return fs.statSync(p)[method](); } catch (_) { return false; }
}

function macAppPresent(name) {
  if (process.platform !== 'darwin') return false;
  return [
    `/Applications/${name}.app`,
    path.join(os.homedir(), 'Applications', `${name}.app`),
  ].some(p => fs.existsSync(p));
}

function vscodeExtPresent(needle) {
  const roots = [
    path.join(os.homedir(), '.vscode/extensions'),
    path.join(os.homedir(), '.vscode-server/extensions'),
    path.join(os.homedir(), '.cursor/extensions'),
    path.join(os.homedir(), '.windsurf/extensions'),
  ];
  const lc = needle.toLowerCase();
  for (const r of roots) {
    if (!fs.existsSync(r)) continue;
    let entries; try { entries = fs.readdirSync(r); } catch (_) { continue; }
    if (entries.some(e => e.toLowerCase().includes(lc))) return true;
  }
  return false;
}

function cursorExtPresent(needle) {
  const dir = path.join(os.homedir(), '.cursor/extensions');
  if (!fs.existsSync(dir)) return false;
  const lc = needle.toLowerCase();
  try { return fs.readdirSync(dir).some(e => e.toLowerCase().includes(lc)); } catch (_) { return false; }
}

function walkDir(root, depth) {
  if (depth < 0) return [];
  const out = [];
  let entries; try { entries = fs.readdirSync(root, { withFileTypes: true }); } catch (_) { return out; }
  for (const e of entries) {
    const full = path.join(root, e.name);
    if (e.isDirectory()) { out.push(full); out.push(...walkDir(full, depth - 1)); }
  }
  return out;
}

function jetbrainsPluginPresent(needle) {
  const roots = [
    path.join(os.homedir(), 'Library/Application Support/JetBrains'),
    path.join(os.homedir(), '.config/JetBrains'),
  ];
  const re = new RegExp(needle, 'i');
  for (const r of roots) {
    if (!fs.existsSync(r)) continue;
    if (walkDir(r, 4).some(p => re.test(path.basename(p)))) return true;
  }
  return false;
}

// detectMatch — parse `||`-delimited probe specs and return true on first match.
// Handles bash-3.2-style `||` splitting cleanly even with whitespace around delimiters.
function detectMatch(spec) {
  if (!spec) return false;
  for (const clause of spec.split('||')) {
    const c = clause.trim();
    if (!c) continue;
    const colon = c.indexOf(':');
    const kind  = colon === -1 ? c : c.slice(0, colon);
    const val   = colon === -1 ? '' : expandHome(c.slice(colon + 1));
    let ok = false;
    switch (kind) {
      case 'command':          ok = hasCmd(val);                      break;
      case 'dir':              ok = safeStat(val, 'isDirectory');     break;
      case 'file':             ok = safeStat(val, 'isFile');          break;
      case 'macapp':           ok = macAppPresent(val);               break;
      case 'vscode-ext':       ok = vscodeExtPresent(val);            break;
      case 'cursor-ext':       ok = cursorExtPresent(val);            break;
      case 'jetbrains-plugin': ok = jetbrainsPluginPresent(val);      break;
    }
    if (ok) return true;
  }
  return false;
}

// ── Platform spawn helpers ────────────────────────────────────────────────

function quoteWinArg(a) {
  if (!IS_WIN) return a;
  if (a === '' || /[\s"]/.test(a)) {
    return '"' + String(a).replace(/\\(?=\\*"|$)/g, '\\\\').replace(/"/g, '\\"') + '"';
  }
  return a;
}

function spawnXplat(cmd, args, opts) {
  if (IS_WIN) {
    return child_process.spawnSync(cmd, args, opts || {});
  }
  return child_process.spawnSync(cmd, args, opts || {});
}

function runSpawn(cmd, args, dryRun, c) {
  const line = `${cmd} ${args.join(' ')}`;
  if (dryRun) { process.stdout.write(`  ${c.dim('would run:')} ${line}\n`); return { status: 0 }; }
  process.stdout.write(`  ${c.dim('$')} ${line}\n`);
  return spawnXplat(cmd, args, { stdio: 'inherit' });
}

function captureSpawn(cmd, args) {
  try { return spawnXplat(cmd, args, { encoding: 'utf8' }); }
  catch (_) { return { status: 1, stdout: '', stderr: '' }; }
}

// ── Repo root detection ───────────────────────────────────────────────────

function detectRepoRoot() {
  const here = path.dirname(__filename);
  const root = path.resolve(here, '..');
  if (fs.existsSync(path.join(root, 'skills')) &&
      fs.existsSync(path.join(root, 'plugins', 'codeforerunner', 'skills'))) {
    return root;
  }
  return null;
}

// ── Per-provider install logic ────────────────────────────────────────────

function installClaude(opts, results, c) {
  results.detected++;
  process.stdout.write(`\n${c.bold('→ Claude Code')}\n`);

  if (!opts.force) {
    const r = captureSpawn('claude', ['plugin', 'list']);
    if (r.status === 0 && /codeforerunner/i.test(r.stdout || '')) {
      process.stdout.write(`  ${c.dim('codeforerunner plugin already installed (use --force to reinstall)')}\n`);
      results.skipped.push({ id: 'claude', why: 'already installed' });
      return;
    }
  }
  const r1 = runSpawn('claude', ['plugin', 'marketplace', 'add', REPO], opts.dryRun, c);
  const r2 = runSpawn('claude', ['plugin', 'install', 'codeforerunner@codeforerunner'], opts.dryRun, c);
  if ((r1.status || 0) === 0 && (r2.status || 0) === 0) results.installed.push('claude');
  else results.failed.push({ id: 'claude', why: 'claude plugin install failed' });
}

function installGemini(opts, results, c) {
  results.detected++;
  process.stdout.write(`\n${c.bold('→ Gemini CLI')}\n`);

  if (!opts.force) {
    const r = captureSpawn('gemini', ['extensions', 'list']);
    if (r.status === 0 && /codeforerunner/i.test(r.stdout || '')) {
      process.stdout.write(`  ${c.dim('codeforerunner extension already installed (use --force to reinstall)')}\n`);
      results.skipped.push({ id: 'gemini', why: 'already installed' });
      return;
    }
  }
  const r = runSpawn('gemini', ['extensions', 'install', `https://github.com/${REPO}`], opts.dryRun, c);
  if ((r.status || 0) === 0) results.installed.push('gemini');
  else results.failed.push({ id: 'gemini', why: 'gemini extensions install failed' });
}

function installViaSkills(prov, opts, results, c) {
  results.detected++;
  process.stdout.write(`\n${c.bold(`→ ${prov.label}`)}\n`);
  // --yes --all: skip the upstream skill-selection TUI. Without these, curl|bash
  // (no TTY on stdin) renders an empty checkbox list and exits 0 with nothing installed.
  const args = ['-y', 'skills', 'add', REPO, '-a', prov.profile, '--yes', '--all'];
  const r = runSpawn('npx', args, opts.dryRun, c);
  if ((r.status || 0) === 0) results.installed.push(prov.id);
  else results.failed.push({ id: prov.id, why: `npx skills add (${prov.profile}) failed` });
}

// ── Help / list ───────────────────────────────────────────────────────────

function printHelp() {
  process.stdout.write(`\
codeforerunner installer — adds /forerunner-* slash commands to agent CLIs

Usage:
  node bin/install.js [flags]

Flags:
  --all            Install to every detected agent (default mode)
  --minimal        Install without any extras
  --only <id>      Install to a specific agent only (repeatable)
  --force          Reinstall even if already installed
  --skip-skills    Skip the npx skills add step
  --dry-run        Print what would run; write nothing
  --list           Show all supported agents and detection status
  --no-color       Disable colored output
  --uninstall, -u  Remove codeforerunner from detected agents
  -h, --help       Show this help

Agents (${PROVIDERS.length}):
${PROVIDERS.map(p => `  ${p.id.padEnd(14)} ${p.label}`).join('\n')}
`);
}

function printList(c) {
  process.stdout.write(`codeforerunner installer — ${PROVIDERS.length} supported agents\n\n`);
  const maxId = Math.max(...PROVIDERS.map(p => p.id.length));
  const maxLabel = Math.max(...PROVIDERS.map(p => p.label.length));
  for (const p of PROVIDERS) {
    const detected = detectMatch(p.detect);
    const status = p.soft && !detected
      ? c.dim('soft (--only ' + p.id + ')')
      : detected
        ? c.green('✓ detected')
        : c.dim('not found');
    const soft = p.soft ? c.dim(' [soft]') : '';
    process.stdout.write(
      `  ${p.id.padEnd(maxId + 2)}${p.label.padEnd(maxLabel + 2)}${status}${soft}\n`
    );
  }
  process.stdout.write('\n');
}

// ── Uninstall ─────────────────────────────────────────────────────────────

function uninstall(opts, c) {
  process.stdout.write('codeforerunner — uninstalling\n\n');
  const targets = opts.only.length ? opts.only : ['claude'];
  for (const id of targets) {
    if (id === 'claude') {
      process.stdout.write(`${c.bold('→ Claude Code')}\n`);
      runSpawn('claude', ['plugin', 'uninstall', 'codeforerunner'], opts.dryRun, c);
    } else {
      process.stdout.write(`  ${c.yellow('warn:')} uninstall for ${id} not yet automated — remove manually\n`);
    }
  }
  process.stdout.write('\ndone\n');
}

// ── Summary ───────────────────────────────────────────────────────────────

function printSummary(results, c) {
  process.stdout.write('\n─────────────────────────────────\n');
  if (results.installed.length) {
    process.stdout.write(c.green(`✓ installed: ${results.installed.join(', ')}\n`));
  }
  if (results.skipped.length) {
    const ids = results.skipped.map(s => `${s.id} (${s.why})`).join(', ');
    process.stdout.write(c.yellow(`– skipped:   ${ids}\n`));
  }
  if (results.failed.length) {
    const ids = results.failed.map(s => `${s.id} (${s.why})`).join(', ');
    process.stdout.write(c.red(`✗ failed:    ${ids}\n`));
  }
  if (!results.installed.length && !results.skipped.length && !results.failed.length) {
    process.stdout.write(c.yellow('no agents detected\n'));
    process.stdout.write(c.dim('  use --list to see all supported agents\n'));
    process.stdout.write(c.dim('  use --only <id> to install for a specific agent\n'));
  }
  process.stdout.write('\n');
  process.stdout.write(c.dim(`  docs: https://github.com/${REPO}\n`));
  process.stdout.write(c.dim('  to configure drift rules: forerunner doctor --fix\n'));
}

// ── Main ──────────────────────────────────────────────────────────────────

function main() {
  const opts    = parseArgs(process.argv.slice(2));
  const c       = makeChalk(opts.noColor);

  if (opts.help)     { printHelp();       return; }
  if (opts.listOnly) { printList(c);      return; }
  if (opts.uninstall){ uninstall(opts,c); return; }

  const results = { detected: 0, installed: [], skipped: [], failed: [] };

  process.stdout.write(c.bold('codeforerunner') + c.dim(' — installing skills into detected agents\n'));
  if (opts.dryRun) process.stdout.write(c.yellow('  (dry-run — no files written)\n'));

  for (const prov of PROVIDERS) {
    // soft providers only install when explicitly requested via --only
    if (prov.soft && !opts.only.includes(prov.id)) continue;
    // --only filter
    if (opts.only.length && !opts.only.includes(prov.id)) continue;

    const detected = detectMatch(prov.detect);
    if (!detected) continue;

    if (opts.skipSkills && prov.profile) continue;

    if (prov.id === 'claude')  { installClaude(opts, results, c);          continue; }
    if (prov.id === 'gemini')  { installGemini(opts, results, c);          continue; }
    if (prov.profile)          { installViaSkills(prov, opts, results, c); continue; }
  }

  printSummary(results, c);
  if (results.failed.length) process.exit(1);
}

main();
