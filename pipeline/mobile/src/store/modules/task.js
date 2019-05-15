import http from '@/api'
import qs from 'qs'

export default {
    namespaced: true,
    state: {},
    mutations: {},
    actions: {
        getTask ({ commit, state, dispatch } = {}, params) {
            const url = `${AJAX_URL_PREFIX}/weixin/api/v3/taskflow/${params.id}/`
            return http.get(url).then(response => response)
        },

        getTaskStatus ({ commit, rootState }, params) {
            const url = `${AJAX_URL_PREFIX}/weixin//taskflow/api/status/${rootState.bizId}/?instance_id=${params.id}`
            return http.get(url).then(response => response)
        },

        instanceStart ({ commit, rootState }, params) {
            const data = qs.stringify({ instance_id: params.id })
            const url = `${AJAX_URL_PREFIX}/weixin//taskflow/api/action/start/${rootState.bizId}/`
            return http.post(url, data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' } }).then(response => response)
        },

        instanceRevoke ({ commit, rootState }, params) {
            const data = qs.stringify({ instance_id: params.id })
            const url = `${AJAX_URL_PREFIX}/weixin//taskflow/api/action/revoke/${rootState.bizId}/`
            return http.post(url, data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' } }).then(response => response)
        },

        instancePause ({ commit, rootState }, params) {
            const data = qs.stringify({ instance_id: params.id })
            const url = `${AJAX_URL_PREFIX}/weixin//taskflow/api/action/pause/${rootState.bizId}/`
            return http.post(url, data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' } }).then(response => response)
        },

        instanceNodeSkip ({ commit, rootState }, params) {
            const data = qs.stringify({ instance_id: params.id, node_id: params.nodeId })
            const url = `${AJAX_URL_PREFIX}/weixin//taskflow/api/nodes/action/skip/${rootState.bizId}/`
            return http.post(url, data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' } }).then(response => response)
        },

        getNodeDetail ({ rootState }, params) {
            const url = `${AJAX_URL_PREFIX}/weixin//taskflow/api/nodes/detail/${rootState.bizId}/?instance_id=${params.taskId}&node_id=${params.nodeId}&component_code=${params.componentCode}&subprocess_stack=[]`
            return http.get(url).then(response => response)
        },

        getNodeRetryData ({ rootState }, params) {
            const url = `${AJAX_URL_PREFIX}/weixin//taskflow/api/nodes/data/${rootState.bizId}/?instance_id=${params.taskId}&node_id=${params.nodeId}&component_code=${params.componentCode}&subprocess_stack=[]`
            return http.get(url).then(response => response)
        }
    }
}
