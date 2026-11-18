'use strict';
// READ ONLY: no push, installer, root, launch, stop, or settings commands.
const fs = require('fs');
const path = require('path');
const net = require('net');
const crypto = require('crypto');
const sdb = require('../rooting/service/sdb.js');
const sync = require('./sdb-sync.cjs');
async function main() {
    const host = process.argv[2];
    if (net.isIP(host) !== 4) throw Error('Provide the single approved TV IPv4 address');
    const root = path.resolve(__dirname, '../../recovery/private/tv-baselines');
    fs.mkdirSync(root, {recursive: true, mode: 0o700});
    const directory = fs.mkdtempSync(path.join(root, 'before-install-'));
    fs.chmodSync(directory, 0o700);
    const write = (name, data) => fs.writeFileSync(path.join(directory, name), data, {flag: 'wx', mode: 0o600});
    let client;
    try {
        client = await sdb.connect({host, timeout: 5000});
        const capabilities = await sdb.exec(client, 'capability:', {timeout: 5000});
        if (!capabilities.split('\n').some(line => line.trim() === 'sdk_toolpath:/home/owner/share/tmp/sdk_tools')) {
            throw Error('Unexpected staging path; do not assume a default');
        }
        const apps = await sdb.exec(client, 'shell:0 vd_applist', {timeout: 8000});
        write('apps.txt', apps);
        let profile;
        try {
            const bytes = await sync.pull(client, '/home/owner/share/tmp/sdk_tools/device-profile.xml');
            write('device-profile.xml', bytes);
            profile = {state: 'present', bytes: bytes.length, sha256: crypto.createHash('sha256').update(bytes).digest('hex')};
        } catch (e) {
            // Never turn permission errors/timeouts into evidence that a file is absent.
            write('profile-read-error.txt', String(e.code || '') + ': ' + e.message);
            profile = e.code === 'SDB_SYNC_FAIL' && e.message.trim() === 'No such file or directory'
                ? {state: 'absent', evidence: 'explicit SDB file-not-found response'}
                : {state: 'unknown', reason: 'read failed; no overwrite authorized'};
        }
        const result = {completed: true, readOnly: true, appListBytes: Buffer.byteLength(apps),
            appListNonempty: !!apps.trim(), vetroMentioned: /vetrotvapp/.test(apps),
            originalDeviceProfile: profile, installed: false};
        write('BASELINE.json', JSON.stringify(result, null, 2) + '\n');
        console.log(JSON.stringify(result, null, 2));
    } finally {if (client) sdb.close(client);}
}
main().catch(e => {console.error(e.message.replace(/(?:\d{1,3}\.){3}\d{1,3}/g, 'TV_IP')); process.exitCode = 1;});
