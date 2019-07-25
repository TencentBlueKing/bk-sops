/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="config-page">
        <div class="list-wrapper-title">
            <span class="list-wrapper-border">|</span>
            <span class="page-title">{{i18n.title}}</span>
        </div>
        <div class="page-content" v-bkloading="{ isLoading: configLoading, opacity: 1 }">
            <div class="common-form-item">
                <label>{{i18n.executorLabel}}</label>
                <div class="common-form-content">
                    <!-- <BaseInput v-model="executor" /> -->
                    <bk-input class="bk-input-inline" :clearable="true" v-model="executor"></bk-input>
                    <i
                        class="bk-icon icon-info-circle desc-tooltip"
                        v-bk-tooltips="{
                            content: i18n.executorTips,
                            placements: ['right']
                        }">
                    </i>
                </div>
            </div>
            <div class="common-form-item executor-switch">
                <label>{{i18n.alwaysUseExecutorLabel}}</label>
                <div class="common-form-content">
                    <bk-switcher v-model="alwaysUseExecutor"></bk-switcher>
                    <i
                        class="bk-icon icon-info-circle desc-tooltip"
                        v-bk-tooltips="{
                            content: i18n.alwaysUseTips,
                            placements: ['right']
                        }">
                    </i>
                </div>
            </div>
        </div>
        <div class="operation-wrapper">
            <bk-button theme="primary" @click="onSaveConfig" :loading="pending" :disabled="configLoading">{{i18n.save}}</bk-button>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'

    export default {
        name: 'configPage',
        data () {
            return {
                executor: undefined,
                pending: false,
                alwaysUseExecutor: false,
                configLoading: false,
                i18n: {
                    title: gettext('执行者配置'),
                    executorLabel: gettext('任务执行者'),
                    alwaysUseExecutorLabel: gettext('强制生效'),
                    executorTips: gettext('该字段默认在非运维人员执行任务时生效，为空则从配置平台(CMDB)随机获取运维身份'),
                    alwaysUseTips: gettext('开启后，所有任务都使用任务执行者身份来执行'),
                    save: gettext('保存')
                }
            }
        },
        created () {
            this.getConfig()
        },
        methods: {
            ...mapActions('config/', [
                'loadBizConfig',
                'configBizExecutor'
            ]),
            async getConfig () {
                this.configLoading = true
                try {
                    const resp = await this.loadBizConfig()
                    if (resp.result) {
                        this.executor = resp.data.executor
                        this.alwaysUseExecutor = resp.data.always_use_executor
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.configLoading = false
                }
            },
            async onSaveConfig () {
                if (this.pending) return
                this.pending = true
                this.executor = this.executor.trim()
                try {
                    const data = {
                        executor: this.executor,
                        always_use_executor: this.alwaysUseExecutor
                    }
                    const resp = await this.configBizExecutor(data)
                    if (resp.result) {
                        this.$bkMessage({
                            message: gettext('保存成功'),
                            theme: 'success'
                        })
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.pending = false
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.config-page {
    padding: 0px 60px 0 60px;
    min-width: 1320px;
    min-height: calc(100% - 50px);
    background: #f4f7fa;
    .list-wrapper-title {
        height: 60px;
        line-height: 60px;
        border-bottom: 1px solid #dde4eb;
    }
    .list-wrapper-border {
        color: #a3c5fd;
    }
    .page-title {
        margin-left: 10px;
        font-size: 14px;
        font-weight: 600;
        color: #313238;
    }
    .page-content {
        margin: 30px 0;
        padding: 30px 0 30px 35px;
        background: #fff;
        border:1px solid #dde4eb;
    }
    .base-input {
        width: 500px;
    }
    .executor-switch {
        margin: 30px 0 0 0;
    }
    .common-form-content {
        margin-left: 180px;
    }
    .common-form-item > label {
        text-align: left;
    }
    .desc-tooltip {
        color: #c4c6cc;
        position: relative;
        top: 3px;
        left: 6px;
    }
    .force-tooltip {
        position: relative;
    }
    .icon-info-circle:hover {
        color: #f4aa1a
    }
    .bk-button {
        width:140px;
        height:32px;
        line-height: 32px;
    }
    .bk-input-inline {
        display: inline-block;
        width: 500px;
    }
}
</style>
