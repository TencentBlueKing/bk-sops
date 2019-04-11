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
        <h3 class="error-title">{{ i18n.sorry }}</h3>
        <ul>
            <li>{{ i18n.contact1 }}
                <a href="javascript:void(0);" @click.prevent="onGotoCC">{{ i18n.cc_system }}</a>
                {{ i18n.cc_roles }}
            </li>
            <li>{{ i18n.goto }}
                <a href="javascript:void(0);" @click.prevent="onGotoCC">{{ i18n.cc_system }}</a>
                {{ i18n.create_biz }}
            </li>
        </ul>
    </div>
</template>
<script>
import '@/utils/i18n.js'
export default {
    name: 'ErrorCode406',
    methods: {
        onGotoCC () {
            window.PAAS_API.open_other_app('bk_cc')
        }
    },
    data () {
        return {
            i18n: {
                sorry: gettext("对不起，您没有业务权限"),
                contact1: gettext("1.联系业务运维为您添加"),
                cc_system: gettext("配置平台"),
                cc_roles: gettext("对应业务的角色，如运维人员、开发人员、产品人员、测试人员"),
                goto: gettext("2.或者前往"),
                create_biz: gettext("创建属于自己的业务")
            }
        }
    }
}
</script>
<style lang="scss" scoped>
    ul {
        padding-left: 30px;
    }
    li {
        list-style: disc;
    }
</style>

