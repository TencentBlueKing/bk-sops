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
    <bk-dialog
        width="600"
        :ext-cls="'common-dialog'"
        :title="i18n.title"
        :header-position="'left'"
        :mask-close="false"
        :value="isAuthorityDialogShow"
        @confirm="onAuthorityConfirm"
        @cancel="onAuthorityCancel">
        <div class="auth-content" v-bkloading="{ isLoading: loading || pending, opacity: 1 }">
            <div class="common-form-item">
                <label>{{i18n.createTaskAuth}}</label>
                <div class="common-form-content">
                    <bk-select v-model="createdTaskPerList" searchable multiple>
                        <bk-option-group
                            v-for="(group, groupIndex) in personGroupList"
                            :name="group.text"
                            :key="groupIndex">
                            <bk-option
                                v-for="(option, optionIndex) in group.children"
                                :key="optionIndex"
                                :id="option.id"
                                :name="option.text">
                            </bk-option>
                        </bk-option-group>
                    </bk-select>
                </div>
            </div>
            <div class="common-form-item">
                <label>{{i18n.modifyParamsAuth}}</label>
                <div class="common-form-content">
                    <bk-select v-model="modifyParamsPerList" searchable multiple>
                        <bk-option-group
                            v-for="(group, groupIndex) in personGroupList"
                            :name="group.text"
                            :key="groupIndex">
                            <bk-option
                                v-for="(option, optionIndex) in group.children"
                                :key="optionIndex"
                                :id="option.id"
                                :name="option.text">
                            </bk-option>
                        </bk-option-group>
                    </bk-select>
                </div>
            </div>
            <div class="common-form-item">
                <label>{{i18n.executeTaskAuth}}</label>
                <div class="common-form-content">
                    <bk-select v-model="executeTaskPerList" searchable multiple>
                        <bk-option-group
                            v-for="(group, groupIndex) in personGroupList"
                            :name="group.text"
                            :key="groupIndex">
                            <bk-option
                                v-for="(option, optionIndex) in group.children"
                                :key="optionIndex"
                                :id="option.id"
                                :name="option.text">
                            </bk-option>
                        </bk-option-group>
                    </bk-select>
                </div>
            </div>
        </div>
    </bk-dialog>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    export default {
        name: 'AthorityManageDialog',
        props: ['isAuthorityDialogShow', 'templateId', 'pending', 'common'],
        data () {
            return {
                loading: true,
                personGroupList: [],
                createdTaskPerList: [],
                modifyParamsPerList: [],
                executeTaskPerList: [],
                i18n: {
                    title: gettext('使用权限'),
                    createTaskAuth: gettext('新建任务权限'),
                    modifyParamsAuth: gettext('认领任务权限'),
                    executeTaskAuth: gettext('执行任务权限')
                }
            }
        },
        watch: {
            isAuthorityDialogShow (val) {
                if (val) {
                    this.loadData()
                }
            }
        },
        methods: {
            ...mapActions('templateList/', [
                'getBizPerson',
                'getTemplatePersons'
            ]),
            async loadData () {
                this.loading = true
                try {
                    Promise.all([
                        this.loadBizPerson(),
                        this.loadTemplatePersons()
                    ]).then(values => {
                        this.personGroupList = values[0].roles
                        this.createdTaskPerList = values[1].create_task.map(item => item.show_name)
                        this.modifyParamsPerList = values[1].fill_params.map(item => item.show_name)
                        this.executeTaskPerList = values[1].execute_task.map(item => item.show_name)
                        this.loading = false
                    })
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            async loadBizPerson () {
                try {
                    const res = await this.getBizPerson()
                    if (res.result) {
                        return res.data
                    } else {
                        errorHandler(res, this)
                        return []
                    }
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            async loadTemplatePersons () {
                try {
                    const data = {
                        templateId: this.templateId,
                        common: this.common
                    }
                    const res = await this.getTemplatePersons(data)
                    if (res.result) {
                        return res.data
                    } else {
                        errorHandler(res, this)
                        return []
                    }
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            onAuthorityConfirm () {
                const data = {
                    templateId: this.templateId,
                    createTask: this.createdTaskPerList,
                    fillParams: this.modifyParamsPerList,
                    executeTask: this.executeTaskPerList,
                    common: this.common
                }
                this.$emit('onAuthorityConfirm', data)
            },
            onAuthorityCancel () {
                this.$emit('onAuthorityCancel')
            }
        }
    }
</script>
<style lang="scss" scoped>
.auth-content {
    padding: 30px;
}
.common-form-item {
    label {
        font-size: 12px;
        font-weight: normal;
    }
}
.common-form-content {
    margin-right: 20px;
}
</style>
