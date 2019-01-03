/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="config-wrapper">
        <BaseInput class="canvas-name"
            v-model="tName"
            :placeholder="i18n.placeholder"
            v-validate="templateNameRule"
            data-vv-name="templateName"
            :name="'templateName'"
            :has-error="errors.has('templateName')"/>
        <span class="common-error-tip error-msg">{{ errors.first('templateName') }}</span>
        <div class="operation-wrapper">
            <bk-button type="success" class="save-canvas" @click="onSaveTemplate" >{{ i18n.save }}</bk-button>
            <router-link class="bk-button bk-button-default" :to="`/template/home/${this.cc_id}/`">{{ i18n.return }}</router-link>
        </div>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { Validator } from 'vee-validate'
import { NAME_REG } from '@/constants/index.js'
import BaseInput from '@/components/common/base/BaseInput.vue'

export default {
    name: "ConfigBar",
    components: {
        BaseInput
    },
    props: ['name', 'cc_id'],
    data () {
        return {
            i18n: {
                placeholder: gettext("请输入名称"),
                save: gettext("保存流程"),
                return: gettext("返回列表")
            },
            tName: this.name,
            templateNameRule: {
                required: true,
                max: 30,
                regex: NAME_REG
            }
        }
    },
    watch: {
        name (val) {
            this.tName = val
        },
        tName (val) {
            this.$emit('onChangeName', val)
        }
    },
    methods: {
        onSaveTemplate () {
            this.$validator.validateAll().then((result) => {
                if (!result) return
                this.$emit('onSaveTemplate')
            })
        }
    }
}
</script>
<style lang="scss" scoped>
    @import '@/scss/config.scss';
    .config-wrapper {
        float: left;
        width: calc(100% - 60px);
        height: 50px;
        background: $commonBgColor;
        border-bottom: 1px solid $commonBorderColor;
    }
    .canvas-name {
        float: left;
        margin-top: 10px;
        margin-left: 20px;
        padding: 4px;
        height: 30px;
        width: 400px;
        font-size: 14px;
        border: 1px solid $commonBorderColor;
        outline: none;
        &:focus {
            border-color: $blueDefault;
        }
    }
    .error-msg {
        margin-left: 10px;
        height: 50px;
        line-height: 50px;
    }
    .operation-wrapper {
        float: right;
        margin-right: 30px;
        margin-top: 6px;
    }
</style>

