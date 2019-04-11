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
    <div class="modify-params-container" v-bkloading="{isLoading: loading, opacity: 1}">
        <div class="panel-title">
            <h3>{{ i18n.change_params }}</h3>
        </div>
        <div class="edit-wrapper">
            <TaskParamEdit
                v-if="!isParamsEmpty"
                ref="TaskParamEdit"
                :constants="constants"
                :editable="paramsCanBeModify">
            </TaskParamEdit>
            <NoData v-else></NoData>
        </div>
        <div class="action-wrapper" v-if="!isParamsEmpty && paramsCanBeModify">
            <bk-button type="success" @click="onModifyParams">{{ i18n.save }}</bk-button>
        </div>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import {mapActions} from 'vuex'
import { errorHandler } from '@/utils/errorHandler.js'
import NoData from '@/components/common/base/NoData.vue'
import TaskParamEdit from '../TaskParamEdit.vue'
export default {
    name: 'ModifyParams',
    components: {
        TaskParamEdit,
        NoData
    },
    props: ['instance_id', 'paramsCanBeModify'],
    data () {
        return {
            bkMessageInstance: null,
            constants: [],
            loading: false,
            pending: false, // 提交修改中
            i18n: {
                change_params: gettext("修改全局参数"),
                save: gettext("保存")
            }
        }
    },
    computed: {
        isParamsEmpty () {
            return !Object.keys(this.constants).length
        }
    },
    created () {
        this.getTaskData()
    },
    methods: {
        ...mapActions('task/', [
            'getTaskInstanceData',
            'instanceModifyParams'
        ]),
        async getTaskData () {
            this.loading = true
            try {
                const instanceData = await this.getTaskInstanceData(this.instance_id)
                const pipelineData = JSON.parse(instanceData.pipeline_tree)
                const constants = {}
                Object.keys(pipelineData.constants).forEach(key => {
                    const cnt = pipelineData.constants[key]
                    if (cnt.show_type === 'show') {
                        constants[key] = cnt
                    }
                })
                this.constants = constants
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.loading = false
            }
        },
        async onModifyParams () {
            if (this.pending) {
                return
            }
            const paramEditComp = this.$refs.TaskParamEdit
            const formData = {}
            let formValid = true
            if (paramEditComp) {
                formValid = paramEditComp.validate()
                if (!formValid) return
                const variables = paramEditComp.getVariableData()
                for (let key in variables) {
                    formData[key] = variables[key].value
                }
            }

            const data = {
                instance_id: this.instance_id,
                constants: JSON.stringify(formData)
            }
            try {
                this.pending = true
                const res = await this.instanceModifyParams(data)
                if (res.result) {
                    this.$bkMessage({
                        message: gettext('参数修改成功'),
                        theme: 'success'
                    })
                } else {
                    errorHandler(res, this)
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
    @import '@/scss/mixins/scrollbar.scss';
    .modify-params-container {
        position: relative;
        height: 100%;
        overflow: hidden;
        .panel-title {
            padding: 20px;
            h3 {
                margin: 0;
                font-size: 22px;
                font-weight: normal;
            }
        }
        .edit-wrapper {
            padding: 20px 20px 0;
            height: calc(100% - 150px);
            overflow-y: auto;
            @include scrollbar;
        }
        .action-wrapper {
            height: 90px;
            line-height: 90px;
            text-align: center;
            border-top: 1px solid $commonBorderColor;
        }
    }
</style>


