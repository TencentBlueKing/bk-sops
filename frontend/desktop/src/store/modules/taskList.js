/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
import axios from 'axios'
import store from '@/store/index.js'

const taskList = {
    namespaced: true,
    state: {
        taskListData: []
    },
    mutations: {
        setTaskListData (state, data) {
            state.taskListData = data
        }
    },
    actions: {
        loadTaskList ({ commit }, data) {
            const { common, template_id } = data
            const querystring = Object.assign({}, data)
            if (template_id) {
                querystring['template_source'] = 'project'
            }
            if (common) {
                querystring['template_source'] = 'common'
            }
            return axios.get('api/v3/taskflow/', {
                params: querystring
            }).then(response => response.data)
        },
        deleteTask ({ commit }, task_id) {
            return axios.delete(`api/v3/taskflow/${task_id}/`).then(response => response.data.objects)
        },
        cloneTask ({ commit }, data) {
            const { task_id, name } = data
            const { app_id, view_mode, project } = store.state
            const projectId = project.project_id
            const dataJson = {
                name,
                instance_id: task_id,
                create_method: view_mode === 'appmaker' ? 'app_maker' : 'app',
                create_info: app_id,
                test: 1
            }
            return axios.post(`taskflow/api/clone/${projectId}/`, dataJson).then(response => response.data)
        }
    }
}

export default taskList
