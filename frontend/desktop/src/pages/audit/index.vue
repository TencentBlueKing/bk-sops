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
<template>
    <div v-bkloading="{ isLoading: permissionLoading, opacity: 0 }" class="loading-page">
        <router-view v-if="hasViewPerm" router-type="audit"></router-view>
    </div>
</template>
<script>
    import { mapActions, mapState } from 'vuex'
    import bus from '@/utils/bus.js'
    import { errorHandler } from '@/utils/errorHandler.js'

    export default {
        name: 'audit',
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
                'queryUserPermission'
            ]),
            // 查询用户是否有审计中心查看权限
            async queryViewPerm () {
                try {
                    const res = await this.queryUserPermission({
                        action: 'audit_view'
                    })
                    if (res.data.is_allow) {
                        this.permissionLoading = false
                        this.hasViewPerm = true
                    } else {
                        this.showPermissionApplyPage()
                    }
                } catch (error) {
                    errorHandler(error, this)
                }
            },
            /**
             * 切换到权限申请页
             */
            showPermissionApplyPage () {
                const action = 'audit_view'
                const bksops = this.permissionMeta.system.find(item => item.id === 'bk_sops')
                const name = this.permissionMeta.actions.find(item => item.id === action).name
                const { id: systemId, name: systemName } = bksops
                const permissions = {
                    system_id: systemId,
                    system_name: systemName,
                    actions: [{
                        id: action,
                        name,
                        related_resource_types: []
                    }]
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
