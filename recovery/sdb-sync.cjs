'use strict';
// Samsung SYNC framing, reviewed against TizenSdb.Core 1.1.8, commit
// 95f6492c3413f0c98e0e6696b369e3382d280e81 (MIT). Uses Vetro's existing SDB connection.
function packet(id, payload) {
    const data = Buffer.from(payload);
    const head = Buffer.alloc(8);
    head.write(id, 0, 4, 'ascii');
    head.writeUInt32LE(data.length, 4);
    return Buffer.concat([head, data]);
}
function pull(client, remotePath, options = {}) {
    if (!/^\/home\/owner\/share\/tmp\/sdk_tools\/[A-Za-z0-9._-]+$/.test(remotePath)) {
        return Promise.reject(Error('Path outside the selected TV staging folder'));
    }
    const limit = options.limit || 2 * 1024 * 1024;
    return new Promise((resolve, reject) => {
        const stream = client.createStream('sync:');
        let buffer = Buffer.alloc(0), size = 0, ended = false;
        const chunks = [];
        const timer = setTimeout(() => finish(Error('SDB pull timed out; remote state unknown')), options.timeout || 8000);
        function finish(error, bytes) {
            if (ended) return;
            ended = true;
            clearTimeout(timer);
            stream.removeAllListeners();
            try { stream.close(); } catch (_) {}
            if (error) reject(error); else resolve(bytes);
        }
        stream.on('data', data => {
            buffer = Buffer.concat([buffer, data]);
            while (buffer.length >= 8 && !ended) {
                const id = buffer.toString('ascii', 0, 4), length = buffer.readUInt32LE(4);
                if (length > limit) return finish(Error('SDB response exceeds bound'));
                if (buffer.length < 8 + length) return;
                const payload = buffer.subarray(8, 8 + length);
                buffer = buffer.subarray(8 + length);
                if (id === 'DATA') {
                    size += payload.length;
                    if (size > limit) return finish(Error('Remote file exceeds bound'));
                    chunks.push(payload);
                } else if (id === 'DONE') return finish(null, Buffer.concat(chunks));
                else if (id === 'FAIL') {
                    const error = Error(payload.toString('utf8'));
                    error.code = 'SDB_SYNC_FAIL';
                    return finish(error);
                } else return finish(Error('Unexpected SDB SYNC response'));
            }
        });
        stream.on('error', e => finish(e));
        stream.on('end', () => finish(Error('SDB stream ended before DONE')));
        stream.on('close', () => finish(Error('SDB stream closed before DONE')));
        stream.write(packet('RECV', Buffer.from(remotePath)), e => {if (e) finish(e);});
    });
}
function push(client, remotePath, data, options = {}) {
    if (!/^\/home\/owner\/share\/tmp\/sdk_tools\/[A-Za-z0-9._-]+$/.test(remotePath) || !Buffer.isBuffer(data) || data.length > 2 * 1024 * 1024) {
        return Promise.reject(Error('Invalid or oversized staging upload'));
    }
    return new Promise((resolve, reject) => {
        const stream = client.createStream('sync:');
        let buffer = Buffer.alloc(0), ended = false;
        const timer = setTimeout(() => finish(Error('Upload timed out; remote file may exist')), options.timeout || 15000);
        function finish(error) {
            if (ended) return;
            ended = true;
            clearTimeout(timer);
            stream.removeAllListeners();
            try {stream.close();} catch (_) {}
            if (error) reject(error); else resolve();
        }
        stream.on('data', chunk => {
            buffer = Buffer.concat([buffer, chunk]);
            if (buffer.length < 8) return;
            const id = buffer.toString('ascii', 0, 4), size = buffer.readUInt32LE(4);
            if (size > 65536) return finish(Error('Oversized SYNC status'));
            if (buffer.length < 8 + size) return;
            if (id === 'OKAY') finish();
            else if (id === 'FAIL') finish(Error('SYNC upload refused: ' + buffer.subarray(8, 8 + size).toString()));
            else finish(Error('Unexpected upload status'));
        });
        stream.on('error', finish);
        stream.on('end', () => finish(Error('Upload ended without success')));
        stream.on('close', () => finish(Error('Upload closed without success')));
        const write = bytes => new Promise((ok, fail) => stream.write(bytes, e => e ? fail(e) : ok()));
        (async () => {
            await write(packet('SEND', Buffer.from(remotePath)));
            for (let offset = 0; offset < data.length; offset += 65536) {
                if (ended) return;
                await write(packet('DATA', data.subarray(offset, offset + 65536)));
            }
            const mtime = Buffer.alloc(4);
            mtime.writeUInt32LE(Math.floor(Date.now() / 1000));
            if (!ended) await write(packet('DONE', mtime));
        })().catch(finish);
    });
}
module.exports = {packet, pull, push};
