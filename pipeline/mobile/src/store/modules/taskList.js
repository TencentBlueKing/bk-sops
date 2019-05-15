import http from '@/api'

export default {
    namespaced: true,
    state: {},
    mutations: {},
    actions: {
        getTaskStatus ({ commit, rootState }, params) {
            const url = `${AJAX_URL_PREFIX}/weixin/taskflow/api/status/${rootState.bizId}/?instance_id=${params.id}`
            return http.get(url).then(response => {
                return response.result ? response.data : {}
            })
        },

        getTaskList ({ commit, rootState, dispatch }, params) {
            const url = `${AJAX_URL_PREFIX}/weixin/api/v3/taskflow/?limit=${params.limit}&offset=${params.offset}
                            &business__cc_id=${rootState.bizId}`
            return http.get(url).then(response => response)
        }
    }
}
