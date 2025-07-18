/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="common-used" data-test-id="home_form_commonUsed" v-bkloading="{ isLoading: commonlyUsedloading, opacity: 1, zIndex: 100 }">
        <h3 class="panel-title">{{ $t('常用项目') }}</h3>
        <router-link :to="{ name: 'projectHome' }" data-test-id="home_form_allProject" class="link-btn">{{ $t('全部项目') }}</router-link>
        <div ref="cardView" v-if="commonUsedList.length" class="card-view">
            <ul ref="cardList" class="card-list scroll-body">
                <li
                    v-for="(item, index) in commonUsedList"
                    :key="index"
                    class="card-item"
                    @click="onSwitchBusiness(item.project.id)">
                    <p class="business-name">{{ item.project.name }}</p>
                    <div class="business-info">
                        <p class="info-item">
                            <label class="label">{{ $t('项目id：') }}</label>
                            <span class="text">{{ item.project.id }}</span>
                        </p>
                        <p class="info-item">
                            <label class="label">{{ $t('时区：') }}</label>
                            <span class="text">{{ item.project.time_zone }}</span>
                        </p>
                    </div>
                </li>
            </ul>

        </div>
        <panel-nodata v-else>
            <span>{{ $t('项目，项目集的权限请前往') }}</span>
            <span class="link-text" @click="jumpToOther('bk_iam')">{{ $t('权限中心') }}</span>
            <span>{{ $t('进行申请；如需新建项目，项目集请前往') }}</span>
            <span class="link-text" @click="jumpToOther('bk_cmdb')">{{ $t('配置平台') }}</span>
        </panel-nodata>
        <span
            v-if="viewIndex > 0"
            class="button-prev common-icon-prev-triangle-shape"
            @click="onShowPrevPage">
        </span>
        <span
            v-if="isShowNextBtn"
            class="button-next common-icon-next-triangle-shape"
            @click="onShowNextPage">
        </span>
    </div>
</template>
<script>
    import PanelNodata from './PanelNodata.vue'
    import { mapActions, mapMutations } from 'vuex'
    import toolsUtils from '@/utils/tools.js'
    import openOtherApp from '@/utils/openOtherApp.js'

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
                commonlyUsedloading: false,
                commonUsedList: [],
                viewIndex: 0,
                limit: 4
            }
        },
        computed: {
            isShowNextBtn () {
                return ((this.commonUsedList.length - this.limit * (this.viewIndex + 1)) / this.limit) > 0
            }
        },
        created () {
            this.onWindowResize = toolsUtils.debounce(this.handlerWindowResize, 300)
        },
        async mounted () {
            window.addEventListener('resize', this.onWindowResize, false)
            await this.initData()
            this.handlerWindowResize()
        },
        beforeDestroy () {
            window.removeEventListener('resize', this.onWindowResize, false)
        },
        methods: {
            ...mapActions('project/', [
                'changeDefaultProject',
                'loadCommonProject'
            ]),
            ...mapMutations('project', [
                'setProjectId'
            ]),
            async initData () {
                try {
                    this.commonlyUsedloading = true
                    const res = await this.loadCommonProject()
                    this.commonUsedList = res.results
                    this.commonlyUsedloading = false
                } catch (e) {
                    console.log(e)
                }
            },
            getLimit () {
                return document.body.clientWidth > 1920 ? 6 : 4
            },
            // 这里统一直接用后端提供的 host 跳转
            jumpToOther (name) {
                const code = name === 'bk_iam' ? window.BK_IAM_APP_CODE : name
                const HOST_MAP = {
                    'bk_iam': window.BK_IAM_APPLY_URL,
                    'bk_cmdb': window.BK_CC_HOST
                }
                openOtherApp(code, HOST_MAP[name])
            },
            onSwitchBusiness (id) {
                window.reportInfo({
                    page: 'home',
                    zone: 'commonUsed',
                    event: 'click'
                })
                this.setProjectId(id)
                this.changeDefaultProject(id)
                this.$router.push({
                    name: 'processHome',
                    params: { project_id: id }
                })
            },
            onShowPrevPage () {
                this.viewIndex -= 1
                this.changeViewIndex()
            },
            onShowNextPage () {
                this.viewIndex += 1
                this.changeViewIndex()
            },
            changeViewIndex () {
                const cardListDom = this.$refs.cardList
                const baseW = this.$refs.cardView.offsetWidth
                cardListDom.style.transform = `translateX(-${this.viewIndex * baseW}px)`
            },
            handlerWindowResize () {
                const cardList = this.$refs.cardView
                const cardItem = document.querySelector('.my-collection .card-list .card-item')
                if (
                    !this.commonUsedList
                    || this.commonUsedList.length === 0
                    || !cardList
                    || !cardItem) {
                    return
                }

                this.limit = Math.floor(cardList.offsetWidth / cardItem.offsetWidth)
                this.viewIndex = 0
                this.changeViewIndex()
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.common-used {
    position: relative;
    margin: 20px 0;
    padding: 20px 24px 28px 24px;
    background: #ffffff;
    .panel-title {
        margin-top: 0;
        margin-bottom: 20px;
        color: #313238;
        font-size: 16px;
        font-weight: 600;
    }
    .link-btn {
        position: absolute;
        right: 24px;
        top: 24px;
        font-size: 12px;
        color: #3a84ff;
    }
    .card-view {
        width: 100%;
        overflow: hidden;
        .card-list {
            max-height: 95px;
            white-space: nowrap;
            transition: all 0.5s;
            .card-item {
                display: inline-block;
                height: 95px;
                padding: 14px;
                background: #f0f1f5;
                border-radius: 2px;
                cursor: pointer;
                @media screen and (max-width: 1560px) {
                    width: calc( (100% - 48px) / 4 );
                    &:not(:nth-child(4n)) {
                        margin-right: 16px;
                    }
                }
                @media screen and (min-width: 1561px) and (max-width: 1919px) {
                    width: calc( (100% - 64px) / 5 );
                    &:not(:nth-child(5n)) {
                        margin-right: 16px;
                    }
                }
                @media screen and (min-width: 1920px) {
                    width: calc( (100% - 80px) / 6 );
                    &:not(:nth-child(6n)) {
                        margin-right: 16px;
                    }
                }
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
    }
    .link-text {
        cursor: pointer;
        color: #3a84ff;
    }
    .button-prev,.button-next {
        position: absolute;
        top: 100px;
        cursor: pointer;
        color: #979ba5;
        &:hover {
            color: #63656e;
        }
    }
    .button-prev {
        left: 6px;
    }
    .button-next {
        right: 6px;
    }
}
</style>
