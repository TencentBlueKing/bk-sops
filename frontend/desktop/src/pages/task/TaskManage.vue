/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="task-manage" style="height: 100%;">
        <router-view></router-view>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState } from 'vuex'

    export default {
        name: 'TaskManage',
        inject: ['reload'],
        computed: {
            ...mapState('project', {
                project_id: state => state.project_id
            }),
            titleTabList () {
                return [
                    { name: i18n.t('任务记录'), routerName: 'taskList', params: { project_id: this.project_id } },
                    { name: i18n.t('周期任务'), routerName: 'periodicTemplate', params: { project_id: this.project_id } }
                ]
            }
        },
        methods: {
            onTabChange (router) {
                if (this.$route.name === router.routerName) {
                    if (Object.keys(this.$route.query).length === 0) {
                        this.reload()
                    } else { // 如果路由中有 query 参数，则清除 query 参数再刷新
                        this.$router.push({ name: router.routerName, params: router.params }).then(() => {
                            this.reload()
                        })
                    }
                } else {
                    this.$router.push({ name: router.routerName, params: router.params })
                }
            }
        }
    }
</script>
