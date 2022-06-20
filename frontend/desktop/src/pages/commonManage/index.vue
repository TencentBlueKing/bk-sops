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
    <div class="loading-page">
        <router-view v-if="hasViewPerm" router-type="layoutContent"></router-view>
    </div>
</template>
<script>
    import { mapActions, mapState } from 'vuex'
    import permission from '@/mixins/permission.js'
    import bus from '@/utils/bus.js'

    export default {
        name: 'layoutContent',
        mixins: [permission],
        data () {
            return {
                permissionLoading: true,
                hasViewPerm: false
            }
        },
        computed: {
            ...mapState({
                permissionMeta: state => state.permissionMeta
            })
        },
        created () {
            this.queryViewPerm()
        },
        methods: {
            ...mapActions([
                'queryUserCommonPermission'
            ]),
            // 查询用户是否有公共流程管理页面权限
            async queryViewPerm () {
                try {
                    const res = await this.queryUserCommonPermission()
                    if (res.data.is_allow) {
                        this.permissionLoading = false
                        this.hasViewPerm = true
                    } else {
                        this.showPermissionApplyPage()
                    }
                } catch (e) {
                    console.log(e)
                }
            },
            /**
             * 切换到权限申请页
             */
            showPermissionApplyPage () {
                const { actions, resources, system } = this.permissionMeta
                const bksops = system.find(item => item.id === 'bk_sops')
                const { id: systemId, name: systemName } = bksops
                const actionsData = this.assembleActionsData(['common_flow_create'], [], {}, actions, resources, systemId, systemName)

                const permissions = {
                    system_id: systemId,
                    system_name: systemName,
                    actions: actionsData
                }

                bus.$emit('togglePermissionApplyPage', true, 'other', permissions)
            }
        }
    }
</script>
<style lang="scss" scoped>
.loading-page {
    width: 100%;
    height: 100%;
}
</style>
