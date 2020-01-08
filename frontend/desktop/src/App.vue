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
    <div id="app">
        <navigator
            v-if="!hideHeader"
            :appmaker-data-loading="appmakerDataLoading" />
        <div class="main-container">
            <router-view v-if="isRouterAlive"></router-view>
        </div>
        <UserLoginModal ref="userLogin"></UserLoginModal>
        <ErrorCodeModal ref="errorModal"></ErrorCodeModal>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapMutations, mapActions } from 'vuex'
    import bus from '@/utils/bus.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    import UserLoginModal from '@/components/common/modal/UserLoginModal.vue'
    import ErrorCodeModal from '@/components/common/modal/ErrorCodeModal.vue'
    import Navigator from '@/components/layout/Navigator.vue'

    export default {
        name: 'App',
        components: {
            Navigator,
            UserLoginModal,
            ErrorCodeModal
        },
        provide () {
            return {
                reload: this.reload
            }
        },
        data () {
            return {
                isRouterAlive: true,
                appmakerDataLoading: false // 轻应用加载 app 详情
            }
        },
        computed: {
            ...mapState({
                'hideHeader': state => state.hideHeader,
                'viewMode': state => state.view_mode,
                'appId': state => state.app_id
            })
        },
        created () {
            /**
             * 兼容标准插件配置项里，异步请求用到的全局弹窗提示
             */
            window.show_msg = (message, type) => {
                this.$bkMessage({
                    message,
                    theme: type
                })
            }

            if (this.viewMode === 'appmaker') {
                this.getAppmakerDetail()
            }
        },
        mounted () {
            bus.$on('showLoginModal', (src) => {
                this.$refs.userLogin.show(src)
            })
            bus.$on('showErrorModal', (type, responseText, title) => {
                this.$refs.errorModal.show(type, responseText, title)
            })
            bus.$on('showMessage', (info) => {
                this.$bkMessage({
                    message: info.message,
                    theme: info.theme || 'error'
                })
            })
        },
        methods: {
            ...mapActions('appmaker/', [
                'loadAppmakerDetail'
            ]),
            ...mapMutations([
                'setTemplateId'
            ]),
            async getAppmakerDetail () {
                this.appmakerDataLoading = true
                try {
                    const data = await this.loadAppmakerDetail(this.appId)
                    this.setTemplateId(data.template_id)
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.appmakerDataLoading = false
                }
            },
            reload () {
                this.isRouterAlive = false
                this.$nextTick(() => {
                    this.isRouterAlive = true
                })
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
    #app {
        width: 100%;
        height: 100%;
        overflow-x: hidden;
        min-width: 1320px;
    }
    .main-container {
        width: 100%;
        height: calc(100% - 50px);
        min-width: 1320px;
        min-height: calc(100% - 50px);
        overflow-x: hidden;
    }
</style>
