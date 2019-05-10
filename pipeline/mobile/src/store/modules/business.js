import http from '@/api'

export default {
    namespaced: true,
    state: {},
    mutations: {},
    actions: {
        getBusinessList ({ commit, state, dispatch }, params, config) {
            const url = `${AJAX_URL_PREFIX}/api/v3/business/?limit=${params.limit}&offset=${params.offset}`
            return http.get(
                url
            ).then(response => response)
        }
    }
}
