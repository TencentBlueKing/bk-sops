/* eslint-disable */
import http from '@/api'
import qs from 'qs'

export default {
    namespaced: true,
    state: {
        id: ''
    },
    mutations: {
        setTemplateId (state, id) {
            state.id = id
        },
    },
    actions: {
        getTemplate ({ commit, state }, templateId) {
            const url = `${AJAX_URL_PREFIX}/api/v3/template/${templateId}/`
            commit('setTemplateId', templateId)
            return http.get(url).then(response => response)
        },

        collectTemplate ({ commit, state, dispatch }, isFavorite = false) {
            // 接口需开发
            template.is_favorite = !isFavorite
            return !isFavorite
        },

        getSchemes({ commit, state, rootState }) {
            const url = `${AJAX_URL_PREFIX}/api/v3/schemes/?biz_cc_id=${rootState.bizId}&template__template_id=${state.id}`
            console.log(url)
            return http.get(url).then(response => {
                const data = response.objects || []
                data.map(o => o.text = o.name)
                return data
            })
        },

        getScheme( { commit, state }, id ) {
            const url = `${AJAX_URL_PREFIX}/api/v3/schemes/${id}/`
            return http.get(url).then(response => response)
        },

        getPreviewTaskTree({ rootState }, params) {
            const url = `${AJAX_URL_PREFIX}/taskflow/api/preview_task_tree/${rootState.bizId}/`
            return http.post(url, qs.stringify(params), { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }).then(response => {
                return response.data.pipeline_tree
            })
        },

        createTask({ rootState,state }, data) {
            const url = `${AJAX_URL_PREFIX}/api/v3/taskflow/`
            const requestData = {
                'business': `api/v3/business/${rootState.bizId}/`,
                'template_id': state.id,
                'creator': rootState.user.username,
                'name': data.name,
                'description': data.description,
                'pipeline_tree': data.exec_data,
                'create_method': 'api',
                'create_info': 'mobile', // 移动端应该是什么
                'flow_type': 'common'
            }
            return http.post(url, requestData, { headers: { 'Content-Type': 'application/json;charset=UTF-8' } }).then(response => response)
        }
    }
}
