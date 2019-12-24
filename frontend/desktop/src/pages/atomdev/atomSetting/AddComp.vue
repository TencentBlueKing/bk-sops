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
    <div class="add-comp" @click="$emit('click')">
        <slot>{{i18n.add}}</slot>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    export default {
        name: 'AddComp',
        data () {
            return {
                i18n: {
                    add: gettext('点击添加')
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .add-comp {
        display: flex;
        height: 60px;
        justify-content: center;
        align-items: center;
        font-size: 12px;
        color: #c4c6cc;
        border: 1px dotted #c4c6cc;
        cursor: pointer;
        &:hover {
            color: #3a84ff;
            border-color: #3a84ff;
        }
    }
</style>
