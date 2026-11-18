'use strict';
const assert = require('assert').strict;
const fs = require('fs');
const path = require('path');
const repo = path.resolve(__dirname, '..');
const signing = require('module').createRequire(path.join(repo, 'rooting/on-boot-probe/package.json'));
const JSZip = signing('jszip');
const {verify} = require('./verify_signed.cjs');
const tmp = fs.mkdtempSync(path.join(repo, '../recovery/private/tool-tmp/verify-negative-'));
(async () => {
    const original = fs.readFileSync(path.join(repo, 'dist/vetro-integration-SIGNED.wgt'));
    const payload = await JSZip.loadAsync(original);
    payload.file('index.html', Buffer.from('tampered test fixture'));
    const payloadFile = path.join(tmp, 'payload-tampered.wgt');
    fs.writeFileSync(payloadFile, await payload.generateAsync({type: 'nodebuffer'}));
    await assert.rejects(verify(payloadFile), /Payload bytes differ/);
    const signature = await JSZip.loadAsync(original);
    const xml = await signature.file('author-signature.xml').async('string');
    signature.file('author-signature.xml', xml.replace(/(<SignatureValue>\s*)([A-Za-z0-9+\/])/, (_, prefix, first) => prefix + (first === 'A' ? 'B' : 'A')));
    const signatureFile = path.join(tmp, 'signature-tampered.wgt');
    fs.writeFileSync(signatureFile, await signature.generateAsync({type: 'nodebuffer'}));
    await assert.rejects(verify(signatureFile), /RSA signature verification failed/);
    console.log('PASS verifier rejects changed payload and changed RSA signature');
})().catch(e => {console.error(e.message); process.exitCode = 1;})
    .finally(() => fs.rmSync(tmp, {recursive: true, force: true}));
