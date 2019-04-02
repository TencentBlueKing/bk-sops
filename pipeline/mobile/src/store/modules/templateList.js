import http from '@/api'
// import { json2Query } from '@/common/util'

export default {
    namespaced: true,
    state: {
    },
    mutations: {
    },
    actions: {
        getTemplateList ({ commit, state, dispatch }, params, config) {
            return http.get(
                `${AJAX_URL_PREFIX}/api/v3/template/?limit=15&offset=0&business__cc_id=2`
            ).then(response => {
                const data = response.objects || []
                return data
            })
        }
    }
}
