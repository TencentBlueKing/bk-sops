export const mergeIamPermissionData = (current, incoming) => {
    if (!current || !incoming || current.system_id !== incoming.system_id) {
        return current
    }
    const actions = (current.actions || []).map(action => ({
        ...action,
        related_resource_types: (action.related_resource_types || []).map(resource => ({
            ...resource,
            instances: [...(resource.instances || [])]
        }))
    }))
    let changed = false
    for (const incomingAction of incoming.actions || []) {
        const action = actions.find(item => item.id === incomingAction.id)
        if (!action) {
            actions.push(incomingAction)
            changed = true
            continue
        }
        for (const incomingResource of incomingAction.related_resource_types || []) {
            const resource = action.related_resource_types.find(item => (
                item.system_id === incomingResource.system_id && item.type === incomingResource.type
            ))
            if (!resource) {
                action.related_resource_types.push(incomingResource)
                changed = true
                continue
            }
            const existing = new Set(resource.instances.map(chain => JSON.stringify(
                chain.map(item => [item.type, String(item.id)])
            )))
            for (const chain of incomingResource.instances || []) {
                const key = JSON.stringify(chain.map(item => [item.type, String(item.id)]))
                if (!existing.has(key)) {
                    resource.instances.push(chain)
                    existing.add(key)
                    changed = true
                }
            }
        }
    }
    return changed ? { ...current, actions } : current
}

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
