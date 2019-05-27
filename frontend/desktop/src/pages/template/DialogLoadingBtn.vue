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
    <div class="btn-wrapper">
        <bk-button
            v-if="dialogFooterData.additionalBtnShow"
            class="additionalBtn"
            :type="additionalBtnType"
            :loading="additionalBtnPending"
            @click="onAdditionalClick">
            {{dialogFooterData.additionalBtnText}}
        </bk-button>
        <bk-button
            class="confirmBtn"
            :type="confirmType"
            :loading="confirmBtnPending"
            @click="onConfirm">
            {{dialogFooterData.confirmText}}
        </bk-button>
        <bk-button
            class="cancelBtn"
            :type="cancelType"
            @click="onCancel">
            {{dialogFooterData.cancelText}}
        </bk-button>
    </div>
</template>
<script>
    export default {
        name: 'LoadingBtnDialog',
        props: ['dialogFooterData'],
        computed: {
            additionalBtnType () {
                return this.dialogFooterData.additionalBtnType
            },
            confirmType () {
                return this.dialogFooterData.confirmType
            },
            cancelType () {
                return this.dialogFooterData.cancelType
            },
            additionalBtnPending () {
                return this.dialogFooterData.additionalBtnPending
            },
            confirmBtnPending () {
                return this.dialogFooterData.confirmBtnPending
            }
        },
        methods: {
            onConfirm () {
                this.$emit('onConfirm')
            },
            onCancel () {
                this.$emit('onCancel')
            },
            onAdditionalClick () {
                this.$emit('onAdditionalClick')
            }
        }
    }
</script>
<style lang="scss">
.btn-wrapper {
    float: right;
    margin: 0 16px 2px 0;
    .confirmBtn, .additionalBtn {
        min-width: 120px;
        height: 32px;
        margin-right: 10px;
        line-height: 30px;
    }
    .cancelBtn {
        min-width:70px;
        height:32px;
    }
}
    
</style>
