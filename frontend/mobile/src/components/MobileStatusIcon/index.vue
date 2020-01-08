/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <van-icon
        v-if="status"
        slot="right-icon"
        :name="name"
        :class="['task-icon', cls]" />
</template>
<span v-if="showText" class="text">{{ text }}</span>
<script>
    // { 任务状态 : [图标名称, css名称, 文本] }
    const STATUS_CLASS = {
        'CREATED': ['circle', 'circle', window.gettext('未执行')],
        'FINISHED': ['checked', 'checked', window.gettext('完成')],
        'FAILED': ['close', 'clear', window.gettext('失败')],
        'SUSPENDED': ['pause', 'pause-circle', window.gettext('暂停')],
        'REVOKED': ['close', 'clear', window.gettext('撤销')],
        'RUNNING': ['more', 'more', window.gettext('运行中')]
    }

    export default {
        name: 'NoData',
        props: {
            status: {
                type: String,
                default: ''
            },
            showText: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                name: 'circle',
                cls: 'circle',
                text: ''
            }
        },
        watch: {
            status (val) {
                [this.cls, this.name, this.text] = STATUS_CLASS[this.status]
            }
        },
        created () {
            if (this.status) {
                [this.cls, this.name, this.text] = STATUS_CLASS[this.status]
                console.log(this.status, this.name, this.cls, this.text)
            }
        }
    }
</script>

<style lang="scss">
    @import '../../../static/style/var.scss';

    .bk-block .status{
        .task-icon{
            vertical-align: middle;
        }
        .text{
            margin-left: 5px;
            font-size: $fs-12;
            color: $text-color-light;
        }
    }
</style>
