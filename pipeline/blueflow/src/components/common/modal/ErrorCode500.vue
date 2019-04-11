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
    <div class="content-wrapper">
        <h3 class="error-title">{{ i18n.except }}</h3>
        <p>{{ i18n.contact }}</p>
        <p v-if="responseText" class="error-tip">{{responseText}}</p>
    </div>
</template>
<script>
import '@/utils/i18n.js'
export default {
    name: 'ErrorCode500',
    props: ['responseText'],
    data () {
        return {
            i18n: {
                except: gettext("应用出现异常"),
                contact: gettext("系统出现异常, 请记录下错误场景并与开发人员联系, 谢谢!")
            }
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.content-wrapper {
    text-align: center;
}
.error-tip {
    margin-top: 10px;
    color: $redDark;
    text-align: left;
}
</style>

