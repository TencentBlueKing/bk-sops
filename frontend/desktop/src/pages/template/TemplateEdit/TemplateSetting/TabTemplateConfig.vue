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
        :quick-close="true"
        :width="800"
        :before-close="closeTab">
        <div class="config-wrapper" slot="content">
            <div class="common-form-item">
                <label class="required">{{ $t('分类') }}</label>
                <div class="common-form-content">
                    <bk-select
                        class="category-select"
                        v-model="category"
                        @change="onChangeTaskCategories">
                        <bk-option
                            v-for="(item, index) in taskCategories"
                            :key="index"
                            :id="item.id"
                            :name="item.name">
                        </bk-option>
                    </bk-select>
                    <span v-show="!isTemplateConfigValid" class="common-error-tip error-msg">{{ $t('必填项')}}</span>
                </div>
            </div>
            <div class="common-form-item">
                <label> {{$t('通知方式')}} </label>
                <div class="common-form-content" v-bkloading="{ isLoading: notifyTypeLoading, opacity: 1 }">
                    <bk-checkbox-group v-model="notifyType">
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
                </div>
            </div>
            <div class="common-form-item">
                <label>{{ $t('通知分组') }}</label>
                <div class="common-form-content">
                    <bk-checkbox-group v-model="receiverGroup">
                        <bk-checkbox
                            v-for="item in notifyGroup"
                            :key="item.id"
                            :value="item.id">
                            {{item.name}}
                        </bk-checkbox>
                    </bk-checkbox-group>
                </div>
            </div>
        </div>
    </bk-sideslider>
</template>

<script>
    import { mapState, mapMutations, mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'

    export default {
        name: 'TabTemplateConfig',
        props: {
            projectInfoLoading: Boolean,
            isTemplateConfigValid: Boolean,
            isShow: Boolean
        },
        data () {
            return {
                selectedTaskCategory: '',
                notifyTypeLoading: false,
                notifyTypeList: []
            }
        },
        computed: {
            ...mapState({
                'projectBaseInfo': state => state.template.projectBaseInfo,
                'timeout': state => state.template.time_out
            }),
            notifyGroup () {
                if (this.projectBaseInfo.notify_group) {
                    return this.projectBaseInfo.notify_group.map(item => {
                        return {
                            id: item.value,
                            name: item.text
                        }
                    })
                }
                return []
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
            },
            receiverGroup: {
                get () {
                    return this.$store.state.template.notify_receivers.receiver_group
                },
                set (value) {
                    this.setReceiversGroup(value)
                }
            },
            notifyType: {
                get () {
                    return this.$store.state.template.notify_type
                },
                set (value) {
                    this.setNotifyType(value)
                }
            },
            category: {
                get () {
                    return this.$store.state.template.category
                },
                set (value) {
                    this.setCategory(value)
                    this.$emit('onSelectCategory', value)
                }
            }
        },
        created () {
            this.getNotifyTypeList()
        },
        methods: {
            ...mapMutations('template/', [
                'setOutputs',
                'setReceiversGroup',
                'setNotifyType',
                'setOvertime',
                'setCategory'
            ]),
            ...mapActions([
                'getNotifyTypes'
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
            onChangeTimeout (val) {
                this.setOvertime(val)
            },
            onChangeTaskCategories (id) {
                this.selectedTaskCategory = id
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
    .common-form-item {
       margin: 20px
    }
    .common-form-item > label {
        margin-top: 0;
        width: 70px;
        height: 32px;
        line-height: 32px;
        font-size: 12px;
        font-weight: normal;
    }
    .common-form-content {
        margin-left: 94px;
        line-height: 32px;
    }
    .bk-form-checkbox {
        margin: 14px 30px 0 0;
        min-width: 96px;
        /deep/ .bk-checkbox-text {
            color: $greyDefault;
            font-size: 12px;
        }
        &:nth-child(-n + 4) {
            margin-top: 0;
        }
    }
    /deep/ .bk-checkbox-text {
        display: inline-flex;
        align-items: center;
        width: 110px;
    }
    .notify-icon {
        margin-right: 4px;
        width: 18px;
    }
}
</style>
