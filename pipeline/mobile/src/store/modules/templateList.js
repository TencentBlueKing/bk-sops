// import http from '@/api'
// import { json2Query } from '@/common/util'

export default {
    namespaced: true,
    state: {},
    mutations: {},
    actions: {
        getCollectTemplateList ({ commit, state, dispatch }, params, config) {
            return [templateList.objects[0]]
        },
        getTemplateList ({ commit, state, dispatch }, params, config) {
            return templateList.objects
            // return http.get(
            //     `${AJAX_URL_PREFIX}/api/v3/template/?limit=15&offset=0&business__cc_id=` + state.bizId
            // ).then(response => {
            //     const data = response.objects || []
            //     console.log(data)
            //     return data
            // })
        }
    }
}

const templateList = {
    'meta': { 'limit': 15, 'next': null, 'offset': 0, 'previous': null, 'total_count': 3 },
    'objects': [{
        'business': {
            'cc_company': '',
            'cc_id': 2,
            'cc_name': '蓝鲸',
            'cc_owner': '',
            'executor': '',
            'id': 1,
            'life_cycle': '2',
            'resource_uri': '/o/bk_sops/api/v3/business/2/',
            'time_zone': 'Asia/Shanghai'
        },
        'category': 'DevTools',
        'category_name': '开发工具',
        'create_time': '2019-03-26 10:27:37 +0800',
        'creator_name': 'admin',
        'edit_time': '2019-03-26 11:03:44 +0800',
        'editor_name': 'admin',
        'id': 59,
        'is_add': 0,
        'is_deleted': false,
        'name': 'add_app_token',
        'notify_receivers': '{\'receiver_group\':[\'Maintainers\'],\'more_receiver\':\'\'}',
        'notify_type': '[\'email\']',
        'pipeline_template': '',
        'resource_uri': '/o/bk_sops/api/v3/template/59/',
        'subprocess_has_update': false,
        'template_id': 59,
        'time_out': 20,
        'version': '58d1a270b272ff9b81cbe0144fffb965'
    }, {
        'business': {
            'cc_company': '',
            'cc_id': 2,
            'cc_name': '蓝鲸',
            'cc_owner': '',
            'executor': '',
            'id': 1,
            'life_cycle': '2',
            'resource_uri': '/o/bk_sops/api/v3/business/2/',
            'time_zone': 'Asia/Shanghai'
        },
        'category': 'OpsTools',
        'category_name': '运维工具',
        'create_time': '2018-12-13 13:53:14 +0800',
        'creator_name': 'Jason',
        'edit_time': '2018-12-13 13:53:14 +0800',
        'editor_name': '',
        'id': 3,
        'is_add': 0,
        'is_deleted': false,
        'name': '发布蓝鲸演示环境到公网',
        'notify_receivers': '{\'receiver_group\':[],\'more_receiver\':\'\'}',
        'notify_type': '[]',
        'pipeline_template': '',
        'resource_uri': '/o/bk_sops/api/v3/template/3/',
        'subprocess_has_update': false,
        'template_id': 3,
        'time_out': 20,
        'version': 'e54748db0d588976f2936efd5607d822'
    }, {
        'business': {
            'cc_company': '',
            'cc_id': 2,
            'cc_name': '蓝鲸',
            'cc_owner': '',
            'executor': '',
            'id': 1,
            'life_cycle': '2',
            'resource_uri': '/o/bk_sops/api/v3/business/2/',
            'time_zone': 'Asia/Shanghai'
        },
        'category': 'Other',
        'category_name': '其它',
        'create_time': '2018-11-15 20:00:31 +0800',
        'creator_name': 'tufeixiang',
        'edit_time': '2018-11-16 10:10:47 +0800',
        'editor_name': 'tufeixiang',
        'id': 1,
        'is_add': 0,
        'is_deleted': false,
        'name': '违规断网',
        'notify_receivers': '{\'receiver_group\':[],\'more_receiver\':\'\'}',
        'notify_type': '[]',
        'pipeline_template': '',
        'resource_uri': '/o/bk_sops/api/v3/template/1/',
        'subprocess_has_update': false,
        'template_id': 1,
        'time_out': 20,
        'version': '37ef69cd018ed4b93d140cb7f9d940be'
    }]
}
