import http from '@/api'

export default {
    namespaced: true,
    state: {},
    mutations: {},
    actions: {
        getBusinessList ({ commit, state, dispatch }, params) {
            const url = `${AJAX_URL_PREFIX}/weixin/api/v3/business/?limit=${params.limit}&offset=${params.offset}`
            return http.get(url).then(response => response)
        }
    }
}
