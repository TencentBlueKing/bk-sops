/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="page-view">
        <section class="bk-block">
            <div class="bk-text-list">
                <van-field
                    :label="i18n.timing"
                    :placeholder="i18n.timePlaceholder"
                    v-model="inputs['bk_timing']" />
            </div>
        </section>
        <div class="btn-group">
            <van-button size="large" type="default" @click="gotoCanvas">{{ i18n.cancel }}</van-button>
            <van-button size="large" type="info" @click="onClick">{{ i18n.confirm }}</van-button>
        </div>
    </div>
</template>
<script>
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'

    export default {
        name: 'task_edit_timing',
        data () {
            return {
                show: false,
                inputs: {},
                taskId: '',
                nodeId: '',
                componentCode: '',
                operating: false,
                i18n: {
                    timePlaceholder: window.gettext('秒(s) 或 时间(%Y-%m-%d %H:%M:%S)'),
                    cancel: window.gettext('取消'),
                    confirm: window.gettext('确定'),
                    timing: window.gettext('定时时间')
                }
            }
        },
        created () {
            this.loadData()
        },
        methods: {
            ...mapActions('task', [
                'instanceNodeEditTime'
            ]),
            loadData () {
                ({ inputs: this.inputs, componentCode: this.componentCode, taskId: this.taskId, nodeId: this.nodeId } = this.$route.params)
            },
            onClick () {
                if (!this.operating) {
                    this.operating = true
                    this.editTime()
                }
            },
            async editTime () {
                this.show = false
                this.$toast.loading({ mask: true, message: this.i18n.loading })
                const params = {
                    instance_id: this.taskId,
                    node_id: this.nodeId,
                    component_code: this.componentCode,
                    inputs: JSON.stringify(this.inputs)
                }
                try {
                    const response = await this.instanceNodeEditTime(params)
                    if (response.result) {
                        this.gotoCanvas()
                        global.bus.$emit('notify', { message: window.gettext('修改定时时间成功') })
                    } else {
                        global.bus.$emit('notify', response)
                        errorHandler(response, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.operating = false
                }
            },
            gotoCanvas () {
                this.$router.push({ path: '/task/canvas', query: { taskId: this.taskId } })
            }
        }
    }
</script>
