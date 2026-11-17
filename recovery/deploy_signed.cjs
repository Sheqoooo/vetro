'use strict';
// Explicitly gated deployment. Default is a local plan, not a TV connection.
// Transport/install commands follow the reviewed TizenSdb.Core 1.1.8 engine.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const net = require('net');
const sdb = require('../rooting/service/sdb.js');
const sync = require('./sdb-sync.cjs');
const {verify} = require('./verify_signed.cjs');
const repo = path.resolve(__dirname, '..');
const privateRoot = path.resolve(repo, '../recovery/private');
const receipt = JSON.parse(fs.readFileSync(path.join(__dirname, 'SIGNED-BUILD.json')));
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
const remoteDir = '/home/owner/share/tmp/sdk_tools';
const remoteWgt = remoteDir + '/vetro-' + receipt.sha256.slice(0, 16) + '.wgt';
const remoteProfile = remoteDir + '/device-profile.xml';
const plan = {appId: 'vetrotvapp.app', packageId: 'vetrotvapp', sha256: receipt.sha256,
    writes: [remoteProfile, remoteWgt],
    installCommand: 'shell:0 vd_appinstall vetrotvapp.app ' + remoteWgt,
    explicitlyLaunchesApp: false, changesDeveloperHostIP: false,
    warning: 'Integration includes an on-boot/auto-restart service and root components; installing is not a guarantee of zero background execution',
    rollbackVerified: false};
function deviceMatches(raw, altNames) {
    const covered = [...String(altNames).matchAll(/URN:tizen:deviceid=([A-Za-z0-9_-]+)/gi)].map(m => m[1]);
    const reply = String(raw).trim();
    return covered.some(id => reply.endsWith(id) && /^[0-9a-fA-F]{0,4}$/.test(reply.slice(0, -id.length)));
}
async function absent(client, filename) {
    try {await sync.pull(client, filename);}
    catch (e) {
        if (e.code === 'SDB_SYNC_FAIL' && e.message.trim() === 'No such file or directory') return;
        throw Error('Cannot establish absence of staging file; no overwrite allowed');
    }
    throw Error('Staging file already exists; preserve it and review before writing');
}
async function execute(host) {
    if (net.isIP(host) !== 4) throw Error('One approved TV IPv4 address required');
    const file = path.join(repo, 'dist/vetro-integration-SIGNED.wgt');
    const wgt = fs.readFileSync(file);
    if (hash(wgt) !== receipt.sha256) throw Error('Signed package hash changed');
    await verify(file);
    const profile = fs.readFileSync(path.join(privateRoot, 'apps2samsung/Certificate/Jelly2Sams - Partner/device-profile.xml'));
    if (profile.length < 1 || profile.length > 1024 * 1024) throw Error('Invalid local device profile size');
    const journalRoot = path.join(privateRoot, 'deployments');
    fs.mkdirSync(journalRoot, {recursive: true, mode: 0o700});
    const dir = fs.mkdtempSync(path.join(journalRoot, 'install-'));
    const journal = data => fs.appendFileSync(path.join(dir, 'journal.jsonl'), JSON.stringify(data) + '\n', {mode: 0o600});
    let client;
    try {
        client = await sdb.connect({host, timeout: 5000});
        const issuedDistributor = new crypto.X509Certificate(fs.readFileSync(path.join(privateRoot,
            'apps2samsung/Certificate/Jelly2Sams - Partner/signed_distributor.cer')));
        const identity = await sdb.exec(client, 'shell:0 getduid', {timeout: 5000});
        if (!deviceMatches(identity, issuedDistributor.subjectAltName)) throw Error('TV identity is not covered by the issued distributor certificate');
        const caps = await sdb.exec(client, 'capability:', {timeout: 5000});
        if (!caps.split('\n').some(l => l.trim() === 'sdk_toolpath:' + remoteDir)) throw Error('Unexpected TV staging path');
        const before = await sdb.exec(client, 'shell:0 vd_applist', {timeout: 8000});
        fs.writeFileSync(path.join(dir, 'apps-before.txt'), before, {flag: 'wx', mode: 0o600});
        if (!before.trim() || /vetrotvapp/.test(before)) throw Error('Existing Vetro or unreadable app list; stop instead of updating');
        await absent(client, remoteProfile);
        await absent(client, remoteWgt);
        journal({stage: 'checked-before-write', plan});
        for (const [name, bytes] of [[remoteProfile, profile], [remoteWgt, wgt]]) {
            journal({stage: 'upload-submitting', remote: name, sha256: hash(bytes)});
            await sync.push(client, name, bytes);
            const readback = await sync.pull(client, name);
            if (hash(readback) !== hash(bytes)) throw Error('Upload readback differs; do not install');
            journal({stage: 'upload-readback-verified', remote: name});
        }
        journal({stage: 'install-submitting'});
        const reply = await sdb.exec(client, plan.installCommand, {timeout: 120000});
        fs.writeFileSync(path.join(dir, 'install-reply.txt'), reply, {flag: 'wx', mode: 0o600});
        const after = await sdb.exec(client, 'shell:0 vd_applist', {timeout: 8000});
        fs.writeFileSync(path.join(dir, 'apps-after.txt'), after, {flag: 'wx', mode: 0o600});
        const confirmed = /install completed/i.test(reply) && !/install failed|\berror\b|\bfail\b/i.test(reply) && /vetrotvapp/.test(after);
        journal({stage: confirmed ? 'installation-confirmed' : 'installation-state-unknown', explicitlyLaunched: false});
        if (!confirmed) throw Error('Installation not conclusively confirmed; preserve journal and do not retry automatically');
        console.log(JSON.stringify({installed: true, explicitlyLaunched: false, rollbackVerified: false}));
    } catch (e) {
        journal({stage: 'stopped', reason: String(e.message).replace(/(?:\d{1,3}\.){3}\d{1,3}/g, 'TV_IP'), automaticRetry: false});
        throw e;
    } finally {if (client) sdb.close(client);}
}
if (require.main === module) {
    if (process.argv.length === 2 || (process.argv.length === 3 && process.argv[2] === '--plan')) console.log(JSON.stringify(plan, null, 2));
    else if (process.argv.length === 4 && process.argv[2] === '--confirm-install') {
        execute(process.argv[3]).catch(e => {console.error(e.message); process.exitCode = 1;});
    } else {console.error('Use --plan; execute only after owner approval with --confirm-install TV_IP'); process.exitCode = 2;}
}
module.exports = {plan, absent, deviceMatches};
