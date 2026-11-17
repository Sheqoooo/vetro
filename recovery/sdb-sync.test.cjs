'use strict';
const assert = require('assert').strict;
const EventEmitter = require('events');
const {packet, pull, push} = require('./sdb-sync.cjs');
function client(response) {
    return {createStream(service) {
        assert.equal(service, 'sync:');
        const stream = new EventEmitter();
        stream.close = () => {};
        stream.write = (request, done) => {
            assert.equal(request.toString('ascii', 0, 4), 'RECV');
            // Deliberately split both headers and payloads across transport chunks.
            setImmediate(() => {
                for (let i = 0; i < response.length; i += 3) stream.emit('data', response.subarray(i, i + 3));
            });
            done();
        };
        return stream;
    }};
}
(async () => {
    const file = '/home/owner/share/tmp/sdk_tools/device-profile.xml';
    assert.equal((await pull(client(Buffer.concat([packet('DATA', Buffer.from('original')), packet('DONE', Buffer.alloc(0))])), file)).toString(), 'original');
    await assert.rejects(pull(client(packet('FAIL', Buffer.from('No such file or directory'))), file),
        e => e.code === 'SDB_SYNC_FAIL' && e.message === 'No such file or directory');
    await assert.rejects(pull(client(packet('FAIL', Buffer.from('Permission denied'))), file), /Permission denied/);
    await assert.rejects(pull(client(packet('DATA', Buffer.from('too much'))), file, {limit: 2}), /exceeds bound/);
    await assert.rejects(pull({}, '/etc/passwd'), /outside/);
    for (const rejected of [false, true]) {
        const sent = [];
        const fake = {createStream() {
            const stream = new EventEmitter();
            stream.close = () => {};
            stream.write = (bytes, done) => {
                sent.push(bytes);
                done();
                if (bytes.toString('ascii', 0, 4) === 'DONE') setImmediate(() =>
                    stream.emit('data', packet(rejected ? 'FAIL' : 'OKAY', Buffer.from(rejected ? 'refused' : ''))));
            };
            return stream;
        }};
        const pending = push(fake, file, Buffer.alloc(70000, 42));
        if (rejected) await assert.rejects(pending, /refused/); else await pending;
        assert.deepEqual(sent.map(b => b.toString('ascii', 0, 4)), ['SEND', 'DATA', 'DATA', 'DONE']);
        assert.equal(sent[1].length - 8, 65536);
        assert.equal(sent[2].length - 8, 4464);
    }
    await assert.rejects(push({}, '/etc/passwd', Buffer.from('x')), /Invalid/);
    const {absent, deviceMatches} = require('./deploy_signed.cjs');
    assert.equal(deviceMatches('FAKETV001', 'URI:URN:tizen:deviceid=FAKETV001'), true);
    assert.equal(deviceMatches('0009FAKETV001', 'URI:URN:tizen:deviceid=FAKETV001'), true);
    assert.equal(deviceMatches('DIFFERENTTV', 'URI:URN:tizen:deviceid=FAKETV001'), false);
    assert.equal(deviceMatches('UNTRUSTEDFAKETV001', 'URI:URN:tizen:deviceid=FAKETV001'), false);
    await absent(client(packet('FAIL', Buffer.from('No such file or directory'))), file);
    await assert.rejects(absent(client(packet('FAIL', Buffer.from('Permission denied'))), file), /no overwrite/);
    await assert.rejects(absent(client(packet('DONE', Buffer.alloc(0))), file), /already exists/);
    console.log('PASS SYNC read/write mocks and deployment no-overwrite guards; no TV writes performed');
})().catch(e => {console.error(e.message); process.exitCode = 1;});
