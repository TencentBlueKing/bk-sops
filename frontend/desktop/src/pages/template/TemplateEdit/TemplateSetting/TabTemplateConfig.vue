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
    <bk-sideslider
        :title="$t('基础信息')"
        :is-show="true"
        :quick-close="false"
        :width="800"
        :before-close="closeTab">
        <div class="config-wrapper" slot="content">
            <bk-form class="form-area" :model="formData" :label-width="140" :rules="rules" ref="configForm">
                <bk-form-item property="category" :label="$t('分类')" :required="true">
                    <bk-select
                        v-model="formData.category"
                        class="category-select"
                        :clearable="false">
                        <bk-option
                            v-for="(item, index) in taskCategories"
                            :key="index"
                            :id="item.id"
                            :name="item.name">
                        </bk-option>
                    </bk-select>
                </bk-form-item>
                <bk-form-item :label="$t('通知方式')">
                    <bk-checkbox-group v-model="formData.notifyType" v-bkloading="{ isLoading: notifyTypeLoading, opacity: 1 }">
                        <template v-for="item in notifyTypeList">
                            <bk-checkbox
                                v-if="item.is_active"
                                :key="item.type"
                                :value="item.type">
                                <img class="notify-icon" :src="`data:image/png;base64,${item.icon}`" />
                                <span style="word-break: break-all;">{{item.label}}</span>
                            </bk-checkbox>
                        </template>
                    </bk-checkbox-group>
                </bk-form-item>
                <bk-form-item :label="$t('通知分组')">
                    <bk-checkbox-group v-model="formData.receiverGroup" v-bkloading="{ isLoading: notifyGroupLoading, opacity: 1 }">
                        <bk-checkbox
                            v-for="item in notifyGroup"
                            :key="item.id"
                            :value="item.id">
                            {{item.name}}
                        </bk-checkbox>
                    </bk-checkbox-group>
                </bk-form-item>
                <bk-form-item :label="$t('执行代理人')">
                    <member-select
                        :multiple="false"
                        :value="formData.executorProxy"
                        @change="formData.executorProxy = $event">
                    </member-select>
                </bk-form-item>
                <bk-form-item property="notifyType" :label="$t('备注')">
                    <bk-input type="textarea" v-model.trim="formData.description" :rows="5" :placeholder="$t('请输入流程模板备注信息')"></bk-input>
                </bk-form-item>
            </bk-form>
            <div class="btn-wrap">
                <bk-button class="save-btn" theme="primary" :disabled="notifyTypeLoading || notifyGroupLoading" @click="onConfirm">{{ $t('保存') }}</bk-button>
                <bk-button theme="default" @click="closeTab">{{ $t('取消') }}</bk-button>
            </div>
        </div>
    </bk-sideslider>
</template>

<script>
    import { mapState, mapMutations, mapActions } from 'vuex'
    import MemberSelect from '@/components/common/Individualization/MemberSelect.vue'
    import i18n from '@/config/i18n/index.js'
    import { errorHandler } from '@/utils/errorHandler.js'

    export default {
        name: 'TabTemplateConfig',
        components: {
            MemberSelect
        },
        props: {
            projectInfoLoading: Boolean,
            isTemplateConfigValid: Boolean,
            isShow: Boolean,
            common: [String, Number]
        },
        data () {
            const { category, notify_type, notify_receivers, description, executor_proxy } = this.$store.state.template
            return {
                formData: {
                    category,
                    description,
                    executorProxy: executor_proxy ? [executor_proxy] : [],
                    receiverGroup: notify_receivers.receiver_group.slice(0),
                    notifyType: notify_type.slice(0)
                },
                rules: {
                    category: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        }
                    ]
                    // description: [
                    //     {
                    //         max: 300,
                    //         message: i18n.t('备注信息不能多于300个字符'),
                    //         trigger: 'blur'
                    //     }
                    // ]
                },
                notifyTypeList: [],
                projectNotifyGroup: [],
                notifyTypeLoading: false,
                notifyGroupLoading: false
            }
        },
        computed: {
            ...mapState({
                'projectBaseInfo': state => state.template.projectBaseInfo,
                'timeout': state => state.template.time_out
            }),
            notifyGroup () {
                let list = []
                if (this.projectBaseInfo.notify_group) {
                    const defaultList = list.concat(this.projectBaseInfo.notify_group.map(item => {
                        return {
                            id: item.value,
                            name: item.text
                        }
                    }))
                    list = defaultList.concat(this.projectNotifyGroup)
                }
                return list
            },
            taskCategories () {
                if (this.projectBaseInfo.task_categories) {
                    return this.projectBaseInfo.task_categories.map(item => {
                        return {
                            id: item.value,
                            name: item.name
                        }
                    })
                }
                return []
            }
        },
        created () {
            this.getNotifyTypeList()
            if (!this.common) {
                this.getProjectNotifyGroup()
            }
        },
        mounted () {
            if (!this.isTemplateConfigValid) {
                this.$refs.configForm.validate()
            }
        },
        methods: {
            ...mapMutations('template/', [
                'setTplConfig'
            ]),
            ...mapActions([
                'getNotifyTypes',
                'getNotifyGroup'
            ]),
            async getNotifyTypeList () {
                try {
                    this.notifyTypeLoading = true
                    const res = await this.getNotifyTypes()
                    this.notifyTypeList = res.data
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.notifyTypeLoading = false
                }
            },
            async getProjectNotifyGroup () {
                try {
                    this.notifyGroupLoading = true
                    const res = await this.getNotifyGroup({ project_id: this.$route.params.project_id })
                    this.projectNotifyGroup = res.data
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.notifyGroupLoading = false
                }
            },
            onConfirm () {
                this.$refs.configForm.validate().then(result => {
                    if (result) {
                        const { category, description, executorProxy, receiverGroup, notifyType } = this.formData
                        const data = {
                            category,
                            description,
                            executor_proxy: executorProxy.length === 1 ? executorProxy[0] : '',
                            receiver_group: receiverGroup,
                            notify_type: notifyType
                        }
                        this.setTplConfig(data)
                        this.closeTab()
                        this.$emit('templateDataChanged')
                    }
                })
            },
            closeTab () {
                this.$emit('closeTab')
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.config-wrapper {
    height: calc(100vh - 60px);
    background: none;
    border: none;
    .form-area {
        padding: 30px 30px 0;
        height: calc(100% - 49px);
        overflow-y: auto;
        @include scrollbar;
    }
    .btn-wrap {
        padding: 8px 30px;
        border-top: 1px solid #cacedb;
        .bk-button {
            margin-right: 10px;
            padding: 0 25px;
        }
    }
    /deep/ .bk-label {
        font-size: 12px;
    }
    .bk-form-checkbox {
        margin-right: 20px;
        margin-bottom: 6px;
        min-width: 96px;
        /deep/ .bk-checkbox-text {
            color: $greyDefault;
            font-size: 12px;
        }
    }
    /deep/ .bk-checkbox-text {
        display: inline-flex;
        align-items: center;
        width: 100px;
    }
    .notify-icon {
        margin-right: 4px;
        width: 18px;
    }
    .user-selector {
        display: block;
    }
}
</style>
