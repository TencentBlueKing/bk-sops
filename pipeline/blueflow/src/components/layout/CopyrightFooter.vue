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
    <footer class="footer-wrapper">
        <div class="copyright">
            <ul class="link-list">
                <a href="tencent://message/?uin=800802001&site=qq&menu=yes" class="link-item">{{i18n.qq}}(800802001)</a>
                <a href="http://bk.tencent.com/s-mart/community/" class="link-item" target="_blank">{{i18n.bkForum}}</a>
                <a href="http://bk.tencent.com/" class="link-item" target="_blank">{{i18n.bk}}</a>
            </ul>
            <div class="desc">Copyright &copy; 2012-{{year}} Tencent BlueKing. All Rights Reserved.</div>
            <div>{{i18n.copyRight}}</div>
        </div>
    </footer>
</template>
<script>
import '@/utils/i18n.js'
import { mapState } from 'vuex'
import moment from 'moment-timezone'
export default {
    name: 'CopyrightFooter',
    computed: {
        ...mapState({
            businessTimezone: state => state.businessTimezone
        })
    },
    data () {
        return {
            year: moment.tz(this.businessTimezone).year(),
            i18n: {
                qq: gettext('QQ咨询'),
                bk: gettext('蓝鲸官网'),
                bkForum: gettext('蓝鲸论坛'),
                copyRight: gettext('蓝鲸智云 版权所有')
            }
        }
    }
}
</script>
<style lang="scss" scoped>
.footer-wrapper {
    margin-top: 50px;
    padding-bottom: 30px;
    min-width: 1320px;
    .copyright {
        font-size: 12px;
        color: #999999;
        text-align: center;
    }
    .link-list {
        margin-bottom: 6px;
    }
    .link-item {
        display: inline-block;
        margin-left: -4px;
        padding: 0 4px;
        line-height: 1;
        color: #3480fe;
        border-right: 1px solid #3480fe;
        &:last-child {
            border-right: none;
        }
    }
    .desc {
        margin-bottom: 8px;
        line-height: 1;
    }
}
</style>

