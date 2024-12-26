
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
        uploadFileToUrl ({ commit }, params) {
            const { upload_url, blob } = params
            return axios({
                url: upload_url,
                method: 'put',
                data: blob, // 直接将 File 对象作为请求体
                withCredentials: false,
                headers: {
                    'content-Type': blob.type // 使用文件本身的类型
                    // 如果需要添加额外的请求头，可以在这里添加
                    // 'Authorization': 'Bearer your-token',
                }
            })
        },
        createLabel ({ commit }, params) {
            return axios.post('/template_market/api/templates_scene/add_scene_label/', params).then(response => response.data)
        },
        loadSharedTemplateRecord ({ commit }) {
            return axios.get('/template_market/api/templates_scene/get_scene_template_list/').then(response => response.data)
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
