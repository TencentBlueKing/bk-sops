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
    <div class="common-dialog-footer-btn-wrapper">
        <bk-button
            class="dialog-btn"
            v-for="(item, index) in dialogFooterData"
            :key="index"
            :theme="item.type"
            :icon="item.icon"
            :loading="item.loading"
            :disabled="item.disabled"
            @click="onClick(item.click)">
            {{item.btnText}}
        </bk-button>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    export default {
        name: 'LoadingBtnDialog',
        props: {
            dialogFooterData: {
                type: Array,
                default: function () {
                    return [{
                        type: 'primary',
                        btnText: gettext('确认'),
                        click: 'onConfirm'
                    }, {
                        btnText: gettext('取消'),
                        click: 'onCancel'
                    }]
                }
            }
        },
        methods: {
            onClick (click) {
                this.$emit(click)
            }
        }
    }
</script>
<style lang="scss">
.common-dialog-footer-btn-wrapper {
    .dialog-btn {
        min-width: 76px;
        &:not(:last-child) {
            margin-right: 10px;
        }
    }
}

</style>
