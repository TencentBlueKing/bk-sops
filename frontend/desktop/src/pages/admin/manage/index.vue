/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="page-manage" v-bkloading="{ isLoading: hasAdminPerm === null, opacity: 0, zIndex: 100 }">
        <template v-if="hasViewPerm">
            <page-header v-if="!hideRoutersNav" :tab-list="routers"></page-header>
            <div :class="['page-manage-content', { 'has-nav': !hideRoutersNav }]">
                <router-view :has-edit-perm="hasEditPerm" :edit-perm-loading="editPermLoading"></router-view>
            </div>
        </template>
    </div>
</template>
<script>
    import { mapActions, mapState } from 'vuex'
    import bus from '@/utils/bus.js'
    import i18n from '@/config/i18n/index.js'
    import PageHeader from '@/components/layout/PageHeader.vue'
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
            PageHeader
        },
        data () {
            return {
                editPermLoading: true,
                hasViewPerm: false,
                hasEditPerm: false,
                routers: ROUTERS
            }
        },
        computed: {
            ...mapState({
                hasAdminPerm: state => state.hasAdminPerm,
                permissionMeta: state => state.permissionMeta
            }),
            hideRoutersNav () {
                return ['packageEdit', 'cacheEdit'].includes(this.$route.name)
            }
        },
        watch: {
            hasAdminPerm (val) {
                if (val) {
                    this.hasViewPerm = true
                    this.queryEditPerm()
                } else {
                    this.showPermissionApplyPage()
                }
            }
        },
        created () {
            if (this.hasAdminPerm !== null) {
                if (this.hasAdminPerm === false) {
                    this.showPermissionApplyPage()
                } else {
                    this.hasViewPerm = true
                    this.queryEditPerm()
                }
            }
        },
        methods: {
            ...mapActions([
                'queryUserPermission'
            ]),
            // 查询用户是否有后台管理编辑权限
            async queryEditPerm () {
                try {
                    const res = await this.queryUserPermission({
                        action: 'admin_edit'
                    })
                    this.hasEditPerm = res.data.is_allow
                    this.editPermLoading = false
                } catch (e) {
                    console.log(e)
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
    @import '@/scss/mixins/scrollbar.scss';

    .page-manage {
        height: calc(100vh - 52px);
        background: #f4f7fa;
        .page-manage-content {
            height: 100%;
            overflow: auto;
            @include scrollbar;
            &.has-nav {
                height: calc(100vh - 100px);
            }
        }
    }
</style>
