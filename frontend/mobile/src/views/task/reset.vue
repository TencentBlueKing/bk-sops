/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="page-view">
        <!-- 任务信息 -->
        <section class="bk-block">
            <div class="bk-text-list">
                <template v-if="Object.keys(inputs).length">
                    <template v-for="item in inputs">
                        <VantComponent
                            v-if="!loadingConfig && item.show_type === 'show'"
                            :source-code="item.source_tag"
                            :custom-type="item.custom_type"
                            :key="item.key"
                            :label="item.name"
                            :placeholder="i18n.paramInput"
                            :value="item.value"
                            :data="item"
                            :render-config="item.renderConfig"
                            @dataChange="onInputDataChange" />
                    </template>
                </template>
                <template v-else>
                    <no-data />
                </template>
            </div>
        </section>
        <div class="btn-group">
            <van-button size="large" type="default" @click="onClickCancel">{{ i18n.cancel }}</van-button>
            <van-button size="large" type="info" @click="onClick">{{ i18n.confirm }}</van-button>
        </div>

        <!-- 选择popup -->
        <van-popup
            v-model="show"
            position="bottom"
            :overlay="true">
            <van-picker
                show-toolbar
                :default-index="defaultIndex"
                :columns="columns"
                @confirm="onSelectConfirm"
                @cancel="show = false" />
        </van-popup>
    </div>
</template>
<script>
    import { mapActions } from 'vuex'
    import NoData from '@/components/NoData/index.vue'
    import VantComponent from '@/components/VantForm/index.vue'
    import { errorHandler } from '@/utils/errorHandler.js'

    export default {
        name: 'TaskReset',
        components: {
            NoData,
            VantComponent
        },
        data () {
            return {
                operating: false,
                show: false,
                defaultIndex: 0,
                columns: [],
                inputs: {},
                nodeId: '',
                taskId: '',
                componentCode: '',
                operatingTagCode: '', // 当前正在操作的原子项
                formData: [],
                i18n: {
                    btnCreate: window.gettext('执行任务'),
                    retrySuccess: window.gettext('重试成功'),
                    cancel: window.gettext('取消'),
                    confirm: window.gettext('确定'),
                    loading: window.gettext('加载中...')
                }
            }
        },
        created () {
            this.loadData()
        },
        methods: {
            ...mapActions('task', [
                'instanceNodeRetry'
            ]),
            loadData () {
                ({ inputs: this.inputs, componentCode: this.componentCode, taskId: this.taskId, nodeId: this.nodeId } = this.$route.params)
            },
            onClick () {
                this.doRetry()
            },
            onClickCancel () {
                this.gotoCanvas()
            },
            onSelect ({ defaultVal, columns, tagCode }) {
                this.show = true
                this.columns = columns
                this.defaultIndex = defaultVal
                this.operatingTagCode = tagCode
            },
            onSelectConfirm (column) {
                this.$set(this.inputs[this.operatingTagCode], 'value', column.value)
                this.show = false
            },
            onInputDataChange (val, key) {
                this.inputs[key].value = val
            },
            async doRetry () {
                if (!this.operating) {
                    this.operating = true
                    this.show = false
                    this.$toast.loading({ mask: true, message: this.i18n.loading })
                    const params = {
                        instance_id: this.taskId,
                        node_id: this.nodeId,
                        component_code: this.componentCode,
                        inputs: JSON.stringify(this.inputs)
                    }
                    try {
                        const response = await this.instanceNodeRetry(params)
                        if (response.result) {
                            global.bus.$emit('notify', { message: this.i18n.retrySuccess })
                            this.gotoCanvas()
                        } else {
                            errorHandler(response, this)
                        }
                    } catch (e) {
                        errorHandler(e, this)
                    } finally {
                        this.operating = false
                    }
                }
            },
            gotoCanvas () {
                this.$router.push({ path: '/task/canvas', query: { taskId: this.taskId } })
            }
        }
    }
</script>
