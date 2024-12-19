
import axios from 'axios'

const templateMarket = {
    namespaced: true,
    actions: {
        loadMarkedServiceCategory ({ commit }) {
            return axios.get('/template_market/api/templates_scene/get_service_category/').then(response => response.data)
        },
        loadMarkedSceneLabel ({ commit }) {
            return axios.get('/template_market/api/templates_scene/get_scene_label/').then(response => response.data)
        },
        loadMarkedRiskLevel ({ commit }) {
            return axios.get('/template_market/api/templates_scene/get_risk_level/').then(response => response.data)
        },
        getFileUploadAddr ({ commit }, params) {
            return axios.get('/template_market/api/templates_scene/get_file_upload_addr/', { params }).then(response => response.data.data)
        },
        createLabel ({ commit }, params) {
            return axios.post('/template_market/api/templates_scene/create_scene_label/', params).then(response => response.data)
        },
        loadSharedTemplateRecord ({ commit }) {
            return axios.get('/template_market/api/templates_scene/').then(response => response.data)
        },
        sharedTemplateRecord ({ commit }, params) {
            const { id } = params
            const baseUrl = '/template_market/api/templates_scene/'
            const url = id ? `${baseUrl}${id}/` : baseUrl
            const method = id ? 'patch' : 'post'
            return axios[method](url, params).then(response => response.data)
        },
        loadTemplatePreviewData ({ commit }, params) {
            return axios.get('/template_market/api/template_preview/', { params }).then(response => response.data)
        }
    }
}

export default templateMarket
