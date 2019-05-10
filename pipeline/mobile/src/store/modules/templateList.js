import http from '@/api'

export default {
    namespaced: true,
    actions: {
        getCollectTemplateList ({ commit, state, dispatch }, params, config) {
            return []
        },
        getTemplateList ({ rootState }, params) {
            const url = `${AJAX_URL_PREFIX}/api/v3/template/?limit=${params.limit}&offset=${params.offset}&business__cc_id=${rootState.bizId}`
            console.log(url)
            return http.get(
                url
            ).then(response => response)
        }
    }
}
