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
        <div class="page-container">
            <h3 class="page-title">{{i18n.title}}</h3>
            <div class="page-content" v-bkloading="{isLoading: configLoading, opacity: 1}">
                <div class="common-form-item">
                    <label>{{i18n.executorLabel}}</label>
                    <div class="common-form-content">
                        <BaseInput v-model="executor"/>
                        <bk-tooltip placement="right" width="400" class="desc-tooltip">
                            <i class="bk-icon icon-info-circle"></i>
                            <div slot="content" style="white-space: normal;">
                                <div>{{i18n.executorTips}}</div>
                            </div>
                        </bk-tooltip>
                    </div>
                </div>
                <div class="common-form-item executor-switch">
                    <label>{{i18n.alwaysUseExecutorLabel}}</label>
                    <div class="common-form-content">
                        <bk-switcher
                            :selected="alwaysUseExecutor"
                            :is-square="true"
                            @change="onSwitchChange">
                        </bk-switcher>
                        <bk-tooltip placement="right" width="400" class="desc-tooltip">
                            <i class="bk-icon icon-info-circle"></i>
                            <div slot="content" style="white-space: normal;">
                                <div>{{i18n.alwaysUseTips}}</div>
                            </div>
                        </bk-tooltip>
                    </div>
                </div>
                <div class="operation-wrapper">
                    <bk-button type="success" @click="onSaveConfig" :loading="pending">{{i18n.save}}</bk-button>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapActions } from 'vuex'
import { errorHandler } from '@/utils/errorHandler.js'
import BaseInput from '@/components/common/base/BaseInput.vue'

export default {
    name: 'configPage',
    components: {
        BaseInput
    },
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
                save: gettext("保存")
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
        },
        onSwitchChange (selected) {
            this.alwaysUseExecutor = selected
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.config-page {
    padding: 20px 60px 0;
    min-width: 1320px;
    min-height: calc(100% - 50px);
    background: $whiteNodeBg;
}
.page-container {
    border: 1px solid $commonBorderColor;
    .page-title {
        margin: 0;
        padding: 15px;
        font-size: 16px;
        font-weight: normal;
        border-bottom: 1px solid $commonBorderColor;
    }
    .page-content {
        padding: 100px 0 60px;
        text-align: left;
        background: $whiteDefault;
        .common-form-item {
            margin: 0 auto 30px;
            width: 800px;
            right: 30px;
            position: relative;
            .common-form-content {
                margin-right: 30px
            }
            .executor-switch {
                position: absolute;
            }
            .desc-tooltip {
                position: absolute;
                top: 6px;
                text-align: right;
                right: 0px;
                .icon-info-circle {
                    color:#c4c6cc;
                    cursor: pointer;
                    &:hover {
                        color:#f4aa1a;
                    }
                }
            }
        }
        .operation-wrapper {
            text-align: center
        }
    }
}
</style>


