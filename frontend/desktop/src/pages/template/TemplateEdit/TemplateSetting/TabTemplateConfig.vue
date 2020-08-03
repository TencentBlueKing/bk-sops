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
            <div class="form-area">
                <div class="common-form-item">
                    <label class="required">{{ $t('分类') }}</label>
                    <div class="common-form-content">
                        <bk-select
                            class="category-select"
                            :clearable="false"
                            v-model="selectedTaskCategory"
                            @change="isCategoryEmpty = false">
                            <bk-option
                                v-for="(item, index) in taskCategories"
                                :key="index"
                                :id="item.id"
                                :name="item.name">
                            </bk-option>
                        </bk-select>
                        <span v-show="isCategoryEmpty" class="common-error-tip error-msg">{{ $t('必填项')}}</span>
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
            <div class="btn-wrap">
                <bk-button class="save-btn" theme="primary" :disable="notifyTypeLoading" @click="onConfirm">{{ $t('保存') }}</bk-button>
                <bk-button theme="default" @click="closeTab">{{ $t('取消') }}</bk-button>
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
            const { category, notify_type, notify_receivers } = this.$store.state.template
            return {
                selectedTaskCategory: category,
                receiverGroup: notify_receivers.receiver_group.slice(0),
                notifyType: notify_type.slice(0),
                notifyTypeLoading: false,
                notifyTypeList: [],
                isCategoryEmpty: !this.isTemplateConfigValid
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
            }
        },
        watch: {
            isTemplateConfigValid (val) {
                this.isCategoryEmpty = !val
            }
        },
        created () {
            this.getNotifyTypeList()
        },
        methods: {
            ...mapMutations('template/', [
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
            onConfirm () {
                if (!this.selectedTaskCategory) {
                    this.isCategoryEmpty = true
                    return
                }
                this.setCategory(this.selectedTaskCategory)
                this.setReceiversGroup(this.receiverGroup)
                this.setNotifyType(this.notifyType)
                this.closeTab()
                this.$emit('templateDataChanged')
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
    .common-form-item {
       margin: 0 20px 20px;
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
}
</style>
