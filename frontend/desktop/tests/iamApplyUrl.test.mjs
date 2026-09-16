import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

const source = await readFile(new URL('../src/utils/iamApplyUrl.js', import.meta.url), 'utf8')
const moduleUrl = `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`
const {
    isValidIamApplyUrl,
    normalizeIamApplyUrlError,
    normalizeIamApplyUrlResponse,
    openIamApplyUrl
} = await import(moduleUrl)

test('normalizes a successful IAM apply URL', () => {
    assert.deepEqual(
        normalizeIamApplyUrlResponse(
            { result: true, data: { url: 'https://iam.example.com/apply?id=1' } },
            'fallback'
        ),
        { url: 'https://iam.example.com/apply?id=1', error: '' }
    )
})

test('rejects failed or malformed IAM apply URLs with request ID', () => {
    assert.deepEqual(
        normalizeIamApplyUrlResponse(
            { result: true, data: { url: 'javascript:alert(1)' }, request_id: 'req-1' },
            'invalid URL'
        ),
        { url: '', error: 'invalid URL (trace-id: req-1)' }
    )
    assert.equal(isValidIamApplyUrl('https://'), false)
    assert.equal(isValidIamApplyUrl('about:blank'), false)
})

test('normalizes both direct and Axios-style error payloads', () => {
    assert.equal(normalizeIamApplyUrlError({ data: { trace_id: 'trace-1' } }, 'failed'), 'failed (trace-id: trace-1)')
    assert.equal(
        normalizeIamApplyUrlError({ response: { data: { request_id: 'req-2' } } }, 'failed'),
        'failed (trace-id: req-2)'
    )
})

test('opens only HTTP(S) URLs', () => {
    const calls = []
    globalThis.window = { open: (...args) => calls.push(args) }

    assert.equal(openIamApplyUrl('about:blank'), false)
    assert.equal(openIamApplyUrl('https://iam.example.com/apply'), true)
    assert.deepEqual(calls, [['https://iam.example.com/apply', '_blank', 'noopener']])
})
