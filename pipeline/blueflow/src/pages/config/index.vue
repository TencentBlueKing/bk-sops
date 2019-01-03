/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="config-page">
        <div class="page-container">
            <h3 class="page-title">{{i18n.title}}</h3>
            <div class="page-content">
                <div class="common-form-item">
                    <label>{{i18n.executorLabel}}</label>
                    <div class="common-form-content">
                        <BaseInput v-model="executor" :placeholder="i18n.placeholder"/>
                    </div>
                </div>
                <div class="operation-wrapper">
                    <bk-button type="success" @click="onSaveExecutor" :loading="pending">{{i18n.save}}</bk-button>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
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
            i18n: {
                title: gettext('业务配置'),
                executorLabel: gettext('任务执行者'),
                placeholder: gettext('该字段在非运维人员执行任务时生效，为空则从配置平台(CMDB)获取运维身份'),
                save: gettext("保存")
            }
        }
    },
    methods: {
        ...mapActions('config/', [
            'configBizExecutor'
        ]),
        async onSaveExecutor () {
            if (this.pending) return
            this.pending = true
            try {
                const data = {
                    executor: this.executor
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
    padding: 20px 60px 0;
    min-width: 1320px;
    min-height: calc(100% - 60px);
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
        text-align: center;
        background: $whiteDefault;
        .common-form-item {
            margin: 0 auto 30px;
            width: 800px;
        }
    }
}
</style>


