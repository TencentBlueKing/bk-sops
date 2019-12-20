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
    <div class="common-used" v-bkloading="{ isLoading: commonlyUsedloading, opacity: 1 }">
        <h3 class="panel-title">{{ i18n.title }}</h3>
        <div v-if="commonUsedList.length && !isScreenChange" class="card-list">
            <li
                v-for="(item, index) in commonUsedList"
                :key="index"
                class="card-item"
                @click="onSwitchBusiness(item.project.id)">
                <p class="business-name">{{ item.project.name }}</p>
                <div class="business-info">
                    <p class="info-item">
                        <label class="label">{{ i18n.businessId }}</label>
                        <span class="text">{{ item.project.id }}</span>
                    </p>
                    <p class="info-item">
                        <label class="label">{{ i18n.timeZone }}</label>
                        <span class="text">{{ item.project.create_at | getTimeZone }}</span>
                    </p>
                </div>
            </li>
        </div>
        <panel-nodata v-else>
            <span>{{ i18n.nodataDes1 }}</span>
            <span class="link-text" @click="openOtherApp('bk_iam_app')">{{ i18n.nodataDes2 }}</span>
            <span>{{ i18n.nodataDes3 }}</span>
            <span class="link-text" @click="openOtherApp('bk_cmdb')">{{ i18n.nodataDes4 }}</span>
        </panel-nodata>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import PanelNodata from './PanelNodata.vue'
    import { errorHandler } from '@/utils/errorHandler.js'
    import { mapActions, mapMutations } from 'vuex'
    export default {
        name: 'CommonlyUsed',
        components: {
            PanelNodata
        },
        filters: {
            getTimeZone (time) {
                const res = /\+(\d)+$/g.exec(time)
                return res ? res[0] : ''
            }
        },
        data () {
            return {
                i18n: {
                    title: gettext('常用业务'),
                    nodataDes1: gettext('业务，业务集的权限请前往'),
                    nodataDes2: gettext('权限中心'),
                    nodataDes3: gettext('进行申请；如需新建业务，业务集请前往'),
                    nodataDes4: gettext('配置平台'),
                    businessId: gettext('业务id：'),
                    timeZone: gettext('时区：')

                },
                commonlyUsedloading: false,
                isScreenChange: false,
                commonUsedList: []
            }
        },
        mounted () {
            this.initData()
        },
        methods: {
            ...mapActions('template/', [
                'loadCommonProject'
            ]),
            ...mapMutations('project', [
                'setProjectId'
            ]),
            async initData () {
                try {
                    this.commonlyUsedloading = true
                    const res = await this.loadCommonProject()
                    this.commonUsedList = res.objects
                    this.commonlyUsedloading = false
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            openOtherApp (url) {
                if (self === top) {
                    window.open(url, '__blank')
                } else {
                    window.PAAS_API.open_other_app(url)
                }
            },
            onSwitchBusiness (id) {
                this.setProjectId(id)
                this.$router.push({
                    name: 'process',
                    params: { project_id: id }
                })
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.common-used {
    margin-top: 20px;
    padding: 20px 24px 28px 24px;
    background: #ffffff;
    .panel-title {
        color: #313238;
        font-size: 16px;
        font-weight: 600;
    }
    .card-list {
        max-height: 95px;
        overflow: hidden;
        .card-item {
            display: inline-block;
            margin-right: 10px;
            padding: 14px;
            width: 278px;
            background: #f0f1f5;
            cursor: pointer;
            &:hover {
                background: #e3e5e9;
            }
            .business-name {
                font-size: 14px;
                color: #313238;
                font-weight: 600;
                white-space: nowrap;
                text-overflow: ellipsis;
                overflow: hidden;
            }
            .business-info {
                margin-top: 6px;
                .info-item {
                    .label {
                        display: inline-block;
                        width: 60px;
                        font-size: 12px;
                        color: #63656e;
                    }
                    .text {
                        margin-left: 10px;
                        font-size: 12px;
                        color: #313238;
                    }
                }
            }
        }
    }
    .link-text {
        cursor: pointer;
        color: #3a84ff;
    }
}
</style>
