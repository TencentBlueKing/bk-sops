export const isValidIamApplyUrl = (url) => {
    if (typeof url !== 'string') {
        return false
    }
    try {
        const parsed = new URL(url)
        return ['http:', 'https:'].includes(parsed.protocol) && Boolean(parsed.hostname)
    } catch (e) {
        return false
    }
}

export const normalizeIamApplyUrlResponse = (response, fallbackMessage) => {
    const url = response && response.data && response.data.url
    if (response && response.result && isValidIamApplyUrl(url)) {
        return { url, error: '' }
    }
    const requestId = response && (response.request_id || response.trace_id)
    return {
        url: '',
        error: `${(response && response.message) || fallbackMessage}${requestId ? ` (trace-id: ${requestId})` : ''}`
    }
}

export const normalizeIamApplyUrlError = (error, fallbackMessage) => {
    const data = error && (error.data || (error.response && error.response.data))
    const requestId = data && (data.request_id || data.trace_id)
    return `${fallbackMessage}${requestId ? ` (trace-id: ${requestId})` : ''}`
}

export const openIamApplyUrl = (url) => {
    if (!isValidIamApplyUrl(url)) {
        return false
    }
    window.open(url, '_blank', 'noopener')
    return true
}
