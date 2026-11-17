'use strict';
// Offline checks only. No private keys needed and no TV connection.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const child = require('child_process');
const repo = path.resolve(__dirname, '..');
const requireSigning = require('module').createRequire(path.join(repo, 'rooting/on-boot-probe/package.json'));
const JSZip = requireSigning('jszip');
const {DOMParser} = requireSigning('@xmldom/xmldom');
const NS = 'http://www.w3.org/2000/09/xmldsig#';
function exactlyOne(parent, name) {
    const matches = parent.getElementsByTagNameNS(NS, name);
    if (matches.length !== 1) throw Error('Expected exactly one ' + name);
    return matches[0];
}
function canonical(node, mode = '--exc-c14n') {
    const copy = node.cloneNode(true);
    copy.setAttribute('xmlns', NS);
    return child.execFileSync('/usr/bin/xmllint', ['--nocatalogs', '--nonet', mode, '-'],
        {input: copy.toString()});
}
async function verify(input = path.join(repo, 'dist/vetro-integration-SIGNED.wgt')) {
    const zip = await JSZip.loadAsync(fs.readFileSync(input), {checkCRC32: true});
    const names = Object.keys(zip.files).filter(n => !zip.files[n].dir);
    const receipt = JSON.parse(fs.readFileSync(path.join(__dirname, 'SIGNED-BUILD.json'), 'utf8'));
    if (!/^[a-f0-9]{40}$/.test(receipt.source_revision)) throw Error('Missing pinned build revision');
    // Documentation-only commits change HEAD, but not the package sources. Check
    // those sources against the pinned build commit instead of requiring HEAD.
    child.execFileSync('/Library/Developer/CommandLineTools/usr/bin/git',
        ['-C', repo, 'diff', '--quiet', receipt.source_revision, '--', 'app', 'rooting', 'dock'],
        {env: Object.assign({}, process.env, {GIT_CONFIG_NOSYSTEM: '1', GIT_CONFIG_GLOBAL: '/dev/null'})});
    const original = require('../rooting/build.cjs').collectIntegration();
    const originalNames = original.map(f => decodeURIComponent(f.uri));
    const actualPayloadNames = names.filter(n => !['author-signature.xml', 'signature1.xml'].includes(n));
    if (JSON.stringify(actualPayloadNames.slice().sort()) !== JSON.stringify(originalNames.slice().sort())) {
        throw Error('Signed package file set differs from the upstream collector');
    }
    for (const file of original) {
        const name = decodeURIComponent(file.uri);
        const bytes = await zip.file(name).async('nodebuffer');
        if (name === 'service/build-info.js') {
            const parseMetadata = data => {
                const match = /module\.exports = (\{[^\n]*\});\s*$/.exec(data.toString('utf8'));
                if (!match) throw Error('Unexpected build metadata format');
                return JSON.parse(match[1]);
            };
            const embedded = parseMetadata(bytes), current = parseMetadata(file.data);
            const expected = Object.assign({}, current, {sourceRevision: receipt.source_revision, sourceDirty: false});
            if (JSON.stringify(embedded) !== JSON.stringify(expected)) throw Error('Pinned build metadata differs');
        } else if (!bytes.equals(file.data)) {
            throw Error('Payload bytes differ from upstream collector');
        }
    }
    const profile = path.join(repo, '../recovery/private/apps2samsung/Certificate/Jelly2Sams - Partner');
    const results = [];
    for (const [name, kind] of [['author-signature.xml', 'author'], ['signature1.xml', 'distributor']]) {
        const errors = [];
        const doc = new DOMParser({errorHandler: {warning() {}, error(e) { errors.push(e); }, fatalError(e) { errors.push(e); }}})
            .parseFromString(await zip.file(name).async('string'), 'application/xml');
        if (errors.length) throw Error('Invalid signature XML');
        const root = doc.documentElement;
        const info = exactlyOne(root, 'SignedInfo');
        const method = exactlyOne(info, 'SignatureMethod').getAttribute('Algorithm');
        if (method !== 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha512') throw Error('Unexpected signature algorithm');
        if (exactlyOne(info, 'CanonicalizationMethod').getAttribute('Algorithm') !== 'http://www.w3.org/2001/10/xml-exc-c14n#') {
            throw Error('Unexpected SignedInfo canonicalization');
        }
        const cert = new crypto.X509Certificate(fs.readFileSync(path.join(profile, 'signed_' + kind + '.cer')));
        const embedded = [...Array(root.getElementsByTagNameNS(NS, 'X509Certificate').length).keys()].map(i =>
            new crypto.X509Certificate(Buffer.from(root.getElementsByTagNameNS(NS, 'X509Certificate')[i].textContent.replace(/\s/g, ''), 'base64')));
        if (!embedded.some(c => c.raw.equals(cert.raw))) throw Error('Issued Samsung certificate missing from signature');
        if (!crypto.verify('RSA-SHA512', Buffer.from(canonical(info)), cert.publicKey,
            Buffer.from(exactlyOne(root, 'SignatureValue').textContent.replace(/\s/g, ''), 'base64'))) {
            throw Error('RSA signature verification failed');
        }
        const now = Date.now();
        if (now < Date.parse(cert.validFrom) || now > Date.parse(cert.validTo)) throw Error('Certificate is not currently valid');
        const refs = info.getElementsByTagNameNS(NS, 'Reference');
        const covered = new Set();
        for (let i = 0; i < refs.length; i++) {
            const ref = refs[i], uri = ref.getAttribute('URI');
            if (covered.has(uri)) throw Error('Duplicate signature reference');
            covered.add(uri);
            if (exactlyOne(ref, 'DigestMethod').getAttribute('Algorithm') !== 'http://www.w3.org/2001/04/xmlenc#sha512') {
                throw Error('Unexpected digest algorithm');
            }
            let bytes;
            if (uri === '#prop') {
                if (exactlyOne(ref, 'Transform').getAttribute('Algorithm') !== 'http://www.w3.org/2006/12/xml-c14n11') {
                    throw Error('Unexpected property transform');
                }
                bytes = canonical(exactlyOne(root, 'Object'), '--c14n11');
            }
            else {
                const target = decodeURIComponent(uri);
                if (!zip.file(target) || target.startsWith('/') || target.split('/').includes('..')) throw Error('Invalid reference target');
                bytes = await zip.file(target).async('nodebuffer');
            }
            const expected = exactlyOne(ref, 'DigestValue').textContent.replace(/\s/g, '');
            if (crypto.createHash('sha512').update(bytes).digest('base64') !== expected) throw Error('Digest mismatch for ' + uri);
        }
        const required = originalNames.concat(kind === 'distributor' ? ['author-signature.xml'] : []).map(encodeURIComponent);
        required.push('#prop');
        if (required.length !== covered.size || required.some(n => !covered.has(n))) throw Error('Incomplete signature coverage');
        results.push({signature: name, rsa: 'verified against issued certificate', references: covered.size, digests: 'verified'});
    }
    console.log(JSON.stringify({file: path.basename(input), files: names.length, payloadMatchesCollector: true,
        signatureChecks: results, tvAcceptanceTested: false, certificateChainTrustIndependentlyVerified: false}, null, 2));
}
module.exports = {verify};
if (require.main === module) verify(process.argv[2]).catch(e => {console.error(e.message); process.exitCode = 1;});
