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
    <div id="app">
        <notice-component
            v-if="enableNoticeCenter"
            :api-url="apiUrl"
            @show-alert-change="hasAlertNotice = $event"
        />
        <navigation v-if="!hideHeader" :class="['sops-layout-navigation', { 'with-system-notice': hasAlertNotice }]">
            <template slot="page-content">
                <div :class="['main-container with-navigation', { 'with-system-notice': hasAlertNotice }]">
                    <router-view v-if="isRouterViewShow"></router-view>
                </div>
                <bk-exception v-if="isProjectDisabled" class="project-exception-wrap" type="404">
                    <span class="exception-title">{{ $t('当前项目不存在或已归档') }}</span>
                    <div class="text-wrap">
                        <router-link :to="{ name: 'home' }" class="link-btn">{{ $t('返回首页') }}</router-link>
                    </div>
                </bk-exception>
                <permissionApply
                    v-else-if="permissinApplyShow"
                    ref="permissionApply"
                    :permission-data="permissionData">
                </permissionApply>
            </template>
        </navigation>
        <template v-else>
            <div :class="['main-container', { 'with-system-notice': hasAlertNotice }]">
                <router-view v-if="isRouterViewShow"></router-view>
            </div>
            <bk-exception v-if="isProjectDisabled" class="project-exception-wrap" type="404">
                <span class="exception-title">{{ $t('当前项目不存在或已归档') }}</span>
                <div class="text-wrap">
                    <router-link :to="{ name: 'home' }" class="link-btn">{{ $t('返回首页') }}</router-link>
                </div>
            </bk-exception>
            <permissionApply
                v-else-if="permissinApplyShow"
                ref="permissionApply"
                :permission-data="permissionData">
            </permissionApply>
        </template>
        <ErrorCodeModal ref="errorModal"></ErrorCodeModal>
        <PermissionModal ref="permissionModal"></PermissionModal>
    </div>
</template>
<script>
    import { mapState, mapMutations, mapActions } from 'vuex'
    import bus from '@/utils/bus.js'
    import isCrossOriginIFrame from '@/utils/isCrossOriginIFrame.js'
    import { setConfigContext } from '@/config/setting.js'
    import permission from '@/mixins/permission.js'
    import ErrorNotify from '@/utils/errorNotify.js'
    import Navigation from '@/components/layout/Navigation.vue'
    import ErrorCodeModal from '@/components/common/modal/ErrorCodeModal.vue'
    import PermissionModal from '@/components/common/modal/PermissionModal.vue'
    import permissionApply from '@/components/layout/permissionApply.vue'
    import NoticeComponent from '@blueking/notice-component-vue2'
    import '@blueking/notice-component-vue2/dist/style.css'

    export default {
        name: 'App',
        components: {
            Navigation,
            ErrorCodeModal,
            permissionApply,
            PermissionModal,
            NoticeComponent
        },
        mixins: [permission],
        provide () {
            return {
                reload: this.reload
            }
        },
        data () {
            return {
                enableNoticeCenter: window.ENABLE_NOTICE_CENTER,
                apiUrl: `${window.SITE_URL}notice/announcements/`,
                hasAlertNotice: false,
                footerLoading: false,
                permissinApplyShow: false,
                permissionData: {
                    type: 'project', // 无权限类型: project、other
                    permission: null
                },
                isRouterAlive: false,
                projectDetailLoading: false, // 项目详情加载
                appmakerDataLoading: false, // 轻应用加载 app 详情,
                isUseSnapshot: false, // 登录成功时是否使用快照
                isProjectDisabled: false, // 当前项目是否禁用
                errorMsgList: [] // message报错实例
            }
        },
        computed: {
            ...mapState({
                'hideHeader': state => state.hideHeader,
                'viewMode': state => state.view_mode,
                'appId': state => state.app_id,
                'site_url': state => state.site_url
            }),
            ...mapState('project', {
                'project_id': state => state.project_id,
                'userProjectList': state => state.userProjectList
            }),
            isRouterViewShow () {
                return !this.permissinApplyShow && this.isRouterAlive && !this.projectDetailLoading && !this.isProjectDisabled
            }
        },
        watch: {
            '$route' (val, oldVal) {
                const prevRouterProjectId = oldVal.params.project_id
                const id = prevRouterProjectId || prevRouterProjectId === 0 ? Number(prevRouterProjectId) : undefined
                this.handleRouteChange(id)
                if (this.isProjectDisabled && !val.meta.project) {
                    this.isProjectDisabled = false
                    // 重新设置默认项目
                    this.setProjectId(this.userProjectList[0].id)
                }
                // 路由发生变化时清空失败message列表
                if (val.name !== oldVal.name && this.errorMsgList.length) {
                    this.errorMsgList.forEach(msgInstance => {
                        msgInstance.close()
                    })
                    this.errorMsgList = []
                }
            }
        },
        async created () {
            window.msg_list = []
            bus.$on('showLoginModal', args => {
                const { has_plain, login_url, width, height, method } = args
                if (has_plain) {
                    const topWindow = isCrossOriginIFrame() ? window : window.top
                    topWindow.BLUEKING.corefunc.open_login_dialog(login_url, width, height, method)
                }
            })
            bus.$on('showErrorModal', (type, responseText, title) => {
                this.$refs.errorModal.show(type, responseText, title)
            })
            bus.$on('togglePermissionApplyPage', (show, type, permission) => {
                this.permissinApplyShow = show
                this.permissionData = {
                    type,
                    permission
                }
                if (!show) {
                    this.isRouterAlive = true
                }
            })
            bus.$on('showPermissionModal', data => {
                this.$refs.permissionModal.show(data)
            })
            bus.$on('showErrMessage', info => {
                const msg = typeof info.message === 'string' ? info.message : JSON.stringify(info.message)
                window.show_msg(msg, 'error', '', info.traceId, info.errorSource)
            })
            // 登录成功后使用快照
            bus.$on('useSnapshot', data => {
                this.isUseSnapshot = true
            })

            /**
             * 兼容标准插件配置项里，异步请求用到的全局弹窗提示
             */
            window.show_msg = (msg, type = 'error', title = '', traceId, errorSource = '') => {
                const index = window.msg_list.findIndex(item => item.msg === msg)
                if (index > -1) {
                    if (traceId && !window.msg_list[index].traceId) {
                        window.msg_list[index] = { msg, type, title, traceId, errorSource }
                    } else {
                        return
                    }
                } else {
                    window.msg_list.push({ msg, type, title, traceId, errorSource })
                }
                setTimeout(() => { // 异步执行,可以把前端报错的trace_id同步上
                    const info = window.msg_list.find(item => item.msg === msg && item.traceId === traceId)
                    if (!info) return
                    this.$nextTick(() => {
                        /* eslint-disable-next-line */
                        new ErrorNotify(info, this)
                    })
                })
            }
            await this.getPageFooter()
            this.getGlobalConfig()
            window.addEventListener('message', this.messageHandler, false)
        },
        mounted () {
            this.initData()
        },
        methods: {
            ...mapActions([
                'getPermissionMeta',
                'queryUserPermission',
                'getFooterContent',
                'getFooterInfo',
                'getGlobalConfig'
            ]),
            ...mapActions('appmaker/', [
                'loadAppmakerDetail'
            ]),
            ...mapActions('project', [
                'loadProjectDetail',
                'getUserProjectConfigs',
                'changeDefaultProject'
            ]),
            ...mapMutations('appmaker/', [
                'setAppmakerTemplateId',
                'setAppmakerDetail'
            ]),
            ...mapMutations('atomForm/', [
                'clearAtomForm'
            ]),
            ...mapMutations('project', [
                'setTimeZone',
                'setProjectName',
                'setProjectActions',
                'setProjectId',
                'setBizId',
                'setProjectConfig'
            ]),
            ...mapMutations([
                'setFooterInfo',
                'setAdminPerm',
                'setStatisticsPerm'
            ]),
            async initData () {
                if (this.$route.meta.project && this.project_id !== '' && !isNaN(this.project_id)) {
                    await this.getProjectDetail()
                }
                await this.getPermissionMeta()
                if (this.viewMode === 'appmaker') {
                    this.getAppmakerDetail()
                } else {
                    this.queryAdminPerm()
                    this.queryStatisticsPerm()
                }
            },
            async getProjectDetail () {
                try {
                    this.projectDetailLoading = true
                    const projectDetail = await this.loadProjectDetail(this.project_id)
                    const projectConfig = await this.getUserProjectConfigs(this.project_id)
                    const { name, id, bk_biz_id, auth_actions, is_disable } = projectDetail
                    this.isProjectDisabled = is_disable
                    this.setProjectId(id)
                    this.setBizId(bk_biz_id)
                    this.setProjectName(name)
                    this.setProjectActions(auth_actions)
                    this.setProjectConfig(projectConfig.data)
                    this.clearAtomForm() // notice: 清除标准插件配置项里的全局变量缓存
                    this.setTimeZone(projectDetail.time_zone)
                    if (this.$route.name === 'templateEdit' && this.$route.query.common) {
                        setConfigContext(this.site_url)
                    } else {
                        setConfigContext(this.site_url, projectDetail)
                    }
                    this.changeDefaultProject(this.project_id)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.projectDetailLoading = false
                }
            },
            async getAppmakerDetail () {
                this.appmakerDataLoading = true
                try {
                    const res = await this.loadAppmakerDetail(this.appId)
                    this.setProjectName(res.project.name)
                    this.setAppmakerDetail(res)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.appmakerDataLoading = false
                }
            },
            async queryAdminPerm () {
                try {
                    const res = await this.queryUserPermission({
                        action: 'admin_view'
                    })

                    this.setAdminPerm(res.data.is_allow)
                } catch (e) {
                    console.log(e)
                }
            },
            async queryStatisticsPerm () {
                try {
                    const res = await this.queryUserPermission({
                        action: 'statistics_view'
                    })

                    this.setStatisticsPerm(res.data.is_allow)
                } catch (e) {
                    console.log(e)
                }
            },
            // 动态获取页面 footer
            async getPageFooter () {
                try {
                    this.footerLoading = true
                    const resp = await this.getFooterInfo()
                    if (resp.result) {
                        this.setFooterInfo(resp.data)
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.footerLoading = false
                }
            },
            handleRouteChange (preProjectId) {
                this.isRouterAlive = true
                if (!this.$route.meta.project) {
                    this.permissinApplyShow = false
                    setConfigContext(this.site_url)
                } else {
                    // 项目上下文页面
                    if (this.project_id !== '' && !isNaN(this.project_id)) {
                        if (this.project_id !== preProjectId) {
                            this.getProjectDetail()
                        }
                        this.permissinApplyShow = false
                    } else { // 需要项目id页面，id为空时，显示无权限页面
                        this.permissinApplyShow = true
                    }
                }
                if (this.$route.query.template_id !== undefined) {
                    this.setAppmakerTemplateId(this.$route.query.template_id)
                }
            },
            reload () {
                this.isRouterAlive = false
                this.$nextTick(() => {
                    this.isRouterAlive = true
                })
            },
            // 绑定跨域通信事件
            messageHandler (message) {
                const data = message.data // message.data为另一个页面传递的数据
                if (data && data === 'login') {
                    window.loginWindow.close() // 关闭弹出的窗口
                    window.loginWindow = null
                    if (this.isUseSnapshot) { // 使用模板快照
                        this.isUseSnapshot = false
                        localStorage.setItem('useSnapshot', true)
                    }
                    // 刷新页面(公共流程模板页面登录后路由需要单独挂载)
                    if (this.$route.query.common) {
                        this.reload()
                    }
                    this.initData()
                }
            }
        }
    }
</script>
<style lang="scss">
    @import './scss/app.scss';
    @import '@/scss/config.scss';

    html,body {
        height:100%;
    }
    body.bk-dialog-shown {
        overflow: hidden;
    }
    #app {
        .sops-layout-navigation.with-system-notice {
            height: calc(100vh - 40px);
            .container-content {
                max-height: calc(100vh - 92px)!important;
            }
            .nav-slider-list {
                height: calc(100vh - 148px) !important;
            }
        }
        .main-container {
            width: 100%;
            height: 100vh;
            &.with-navigation {
                height: calc(100vh - 52px);
            }
            &.with-system-notice {
                height: calc(100vh - 92px);
            }
        }
    }
    .interface-exception-notify-message {
        .message-detail .message-copy {
            top: 0 !important;
            right: 0 !important;
        }
    }
    .project-exception-wrap {
        position: absolute !important;
        top: 30%;
        left: 0;
        width: 100%;
        .link-btn {
            font-size: 14px;
            color: #3a84ff;
            margin-top: 12px;
        }
    }
</style>
