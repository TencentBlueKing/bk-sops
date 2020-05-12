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
    <div class="tag-button">
        <bk-button
            :theme="type"
            :size="size"
            :disabled="disabled"
            :loading="loading"
            :icon="icon"
            :text="text"
            @click="onClick">
            {{ title }}
        </bk-button>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { getFormMixins } from '../formMixins.js'

    export const attrs = {
        title: {
            type: String,
            required: false,
            default: i18n.t('按钮文本'),
            desc: 'determine whether it\'s a plain button'
        },
        type: {
            type: String,
            required: false,
            default: '',
            desc: 'button type primary / success / warning / danger'
        },
        icon: {
            type: String,
            required: false,
            default: '',
            desc: 'button icon'
        },
        size: {
            type: String,
            required: false,
            default: 'normal',
            desc: 'button size small / normal / large'

        },
        disabled: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'button disabled'
        },
        loading: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'button loading'
        },
        text: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'text button'
        }
    }
    export default {
        name: 'TagButton',
        mixins: [getFormMixins(attrs)],
        methods: {
            onClick () {
                this.emit_event(this.tagCode, 'click', this.value)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .tag-button {
        height: 32px;
        .bk-button,
        .bk-button-text{
            font-size: 12px;
        }
        .bk-button-text {
            line-height: 32px;
        }
    }
</style>
