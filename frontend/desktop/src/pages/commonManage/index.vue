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
    <div class="loading-page" v-bkloading="{ isLoading: !crtCommonSpace }">
        <router-view v-if="hasViewPerm" router-type="layoutContent"></router-view>
        <div class="space-guide-wrap" v-else-if="crtCommonSpace && crtCommonSpace !== -1">
            <div class="guide-item">
                <img class="desc-img" :src="notPermissionUrl" alt="">
                <p>{{ $t('可申请管理空间内的所有流程') }}</p>
                <bk-button @click="onSpacePermissionCheck(['common_space_join'], spaceInfo)">{{ $t('申请空间成员') }}</bk-button>
            </div>
            <div class="guide-item">
                <img class="desc-img" :src="notPermissionUrl" alt="">
                <p>{{ $t('可申请管理空间配置') }}</p>
                <p>{{ $t('及管理空间内的所有流程') }}</p>
                <bk-button @click="onSpacePermissionCheck(['common_space_manage'], spaceInfo)">{{ $t('申请空间管理员') }}</bk-button>
            </div>
            <div class="guide-item">
                <img class="desc-img" :src="addBizUrl" alt="">
                <p>{{ $t('需要有新建空间的权限') }}</p>
                <bk-button @click="applyForPermission(['common_space_create'])">{{ $t('新建空间') }}</bk-button>
            </div>
        </div>
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
                hasViewPerm: false,
                notPermissionUrl: require('@/assets/images/not-permission.png'),
                addBizUrl: require('@/assets/images/add-biz.png')
            }
        },
        computed: {
            ...mapState({
                permissionMeta: state => state.permissionMeta,
                commonSpaceList: state => state.template.commonSpaceList,
                crtCommonSpace: state => state.template.crtCommonSpace
            }),
            spaceInfo () {
                return this.commonSpaceList.find(item => item.id === this.crtCommonSpace)
            }
        },
        watch: {
            crtCommonSpace: {
                handler (val) {
                    if (val === -1) {
                        if (this.permissionLoading) { // 只判断一次
                            this.queryViewPerm()
                        }
                    } else if (val) {
                        this.hasViewPerm = this.spaceInfo.auth_actions.length
                    }
                },
                deep: true,
                immediate: true
            }
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
            },
            /**
             * 单个空间操作项点击时校验
             * @params {Array} required 需要的权限
             * @params {Object} template 空间数据对象
             */
            onSpacePermissionCheck (required, spaceInfo) {
                const curPermission = spaceInfo.auth_actions.slice(0)
                const permissionData = {
                    common_space: [{
                        id: spaceInfo.id,
                        name: spaceInfo.name
                    }]
                }
                this.applyForPermission(required, curPermission, permissionData)
            }
        }
    }
</script>
<style lang="scss" scoped>
.loading-page {
    width: 100%;
    height: 100%;
}
.space-guide-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    background: #f5f7fa;
    .guide-item {
        width: 280px;
        height: 400px;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding-top: 62px;
        font-size: 12px;
        color: #979ba5;
        line-height: 20px;
        background: #ffffff;
        border-radius: 2px;
        box-shadow: 0px 2px 4px 0px rgba(25,25,41,0.05);
        img {
            width: 200px;
            height: 200px;
            margin-bottom: 18px;
        }
        .bk-button {
            width: 180px;
            margin-top: 36px;
        }
        &:not(:last-child) {
            margin-right: 32px;
        }
        &:nth-child(2) {
            img {
                margin-bottom: 8px;
            }
            .bk-button {
                margin-top: 26px;
            }
        }
    }
}
</style>
