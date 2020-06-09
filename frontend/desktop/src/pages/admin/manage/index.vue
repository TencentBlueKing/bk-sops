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
    <div class="page-manage" v-bkloading="{ isLoading: viewPermLoading, opacity: 0 }">
        <template v-if="hasViewPerm">
            <base-title
                class="title"
                type="router"
                :tab-list="routers"
                :title="title">
            </base-title>
            <router-view :has-edit-perm="hasEditPerm" :edit-perm-loading="editPermLoading"></router-view>
        </template>
    </div>
</template>
<script>
    import { mapActions, mapState } from 'vuex'
    import bus from '@/utils/bus.js'
    import i18n from '@/config/i18n/index.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    const ROUTERS = [
        {
            name: i18n.t('搜索'),
            routerName: 'adminSearch'
        },
        {
            name: i18n.t('周期任务'),
            routerName: 'adminPeriodic'
        },
        {
            name: i18n.t('远程插件包源管理'),
            routerName: 'sourceManage'
        },
        {
            name: i18n.t('远程插件同步'),
            routerName: 'sourceSync'
        }
    ]

    export default {
        name: 'Manage',
        components: {
            BaseTitle
        },
        data () {
            return {
                viewPermLoading: true,
                editPermLoading: true,
                hasViewPerm: false,
                hasEditPerm: false
            }
        },
        computed: {
            ...mapState({
                permissionMeta: state => state.permissionMeta
            }),
            routers () {
                return ['packageEdit', 'cacheEdit'].includes(this.$route.name) ? [] : ROUTERS
            },
            title () {
                return ['packageEdit', 'cacheEdit'].includes(this.$route.name) ? i18n.t('编辑包源') : i18n.t('后台管理')
            }
        },
        created () {
            this.queryViewPerm()
            this.queryEditPerm()
        },
        methods: {
            ...mapActions([
                'queryUserPermission'
            ]),
            // 查询用户是否有后台管理查看权限
            async queryViewPerm () {
                try {
                    const res = await this.queryUserPermission({
                        action: 'admin_view'
                    })
                    if (res.data.is_allow) {
                        this.viewPermLoading = false
                        this.hasViewPerm = true
                    } else {
                        this.showPermissionApplyPage()
                    }
                } catch (error) {
                    errorHandler(error, this)
                }
            },
            // 查询用户是否有后台管理编辑权限
            async queryEditPerm () {
                try {
                    const res = await this.queryUserPermission({
                        action: 'admin_edit'
                    })
                    this.hasEditPerm = res.data.is_allow
                    this.editPermLoading = false
                } catch (error) {
                    errorHandler(error, this)
                }
            },
            /**
             * 切换到权限申请页
             */
            showPermissionApplyPage () {
                const action = 'admin_view'
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
    .page-manage {
        padding: 0 60px;
        min-width: 1320px;
        height: 100%;
        background: #f4f7fa;
        .header-wrapper {
            margin: 0 60px 0;
        }
    }
</style>
