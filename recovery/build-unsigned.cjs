'use strict';
// Offline packaging only: uses the unchanged upstream file collectors and ZIP
// builder. Does not execute packaged TV payloads or generate signing material.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const child = require('child_process');
const repo = path.resolve(__dirname, '..');
const git = '/Library/Developer/CommandLineTools/usr/bin/git';
const env = Object.assign({}, process.env, {GIT_CONFIG_NOSYSTEM: '1', GIT_CONFIG_GLOBAL: '/dev/null'});
function gitRead(args) {
    return child.execFileSync(git, ['-C', repo].concat(args), {env, encoding: 'utf8'}).trim();
}
const revision = gitRead(['rev-parse', 'HEAD']);
if (!/^[a-f0-9]{40}$/.test(revision)) throw Error('Unknown source revision');
if (gitRead(['status', '--porcelain', '--', 'app', 'rooting', 'dock'])) {
    throw Error('App/integration/dock sources have local changes; commit/review them before packaging');
}
const app = require('../app/build.cjs');
const integration = require('../rooting/build.cjs');
const sets = [
    {name: 'vetro-app-only-UNSIGNED.wgt', mode: 'app-only', files: app.collectFiles()},
    {name: 'vetro-integration-UNSIGNED.wgt', mode: 'tv-integration', files: integration.collectIntegration()}
];
const out = path.join(repo, 'dist');
fs.mkdirSync(out, {recursive: true});
const artifacts = [];
for (const set of sets) {
    const names = set.files.map(f => decodeURIComponent(f.uri));
    if (new Set(names).size !== names.length) throw Error('Duplicate package paths');
    for (const name of names) {
        if (name.startsWith('/') || name.split('/').includes('..') || /(?:^|\/)(?:author-signature\.xml|signature\d*\.xml)$/.test(name) || /\.(p12|pfx|key)$/.test(name)) {
            throw Error('Unsafe or signed/private entry: ' + name);
        }
    }
    const bytes = app.zip(set.files);
    const target = path.join(out, set.name);
    if (fs.existsSync(target)) {
        if (!fs.readFileSync(target).equals(bytes)) throw Error('Existing artifact differs; preserve and review it before rebuilding');
    } else fs.writeFileSync(target, bytes, {flag: 'wx'});
    artifacts.push({file: set.name, mode: set.mode, signed: false, bytes: bytes.length,
        sha256: crypto.createHash('sha256').update(bytes).digest('hex'), entries: names.length});
}
const manifest = {sourceRevision: revision, sourceChanges: false, version: require('../app/package.json').version,
    hardwareTested: false, installReady: false, artifacts};
fs.writeFileSync(path.join(out, 'OFFLINE-BUILD.json'), JSON.stringify(manifest, null, 2) + '\n');
console.log(JSON.stringify(manifest, null, 2));
