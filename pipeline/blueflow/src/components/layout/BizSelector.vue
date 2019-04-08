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
    <div
        :class="['biz-wrapper',]"
        v-clickout="onHideBizList">
        <div
            :class="['current-biz-name', {'list-open': showList, 'disabled-biz-name': disabled}]"
            :title="currentBizName"
            @click="onToggleBizList">
            {{currentBizName}}
        </div>
        <div class="biz-list" v-show="showList">
            <div class="search-wrapper">
                <input class="search-input" v-model="searchStr"/>
                <i class="common-icon-search"></i>
            </div>
            <ul>
                <li
                    v-for="biz in businessList"
                    :key="biz.cc_id"
                    :class="['biz-item', { 'selected': Number(currentBizId) === biz.cc_id}]"
                    :title="biz.cc_name"
                    @click.stop="onSelectBiz(biz.cc_id)">
                    {{biz.cc_name}}
                </li>
            </ul>
        </div>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapMutations, mapActions } from 'vuex'
import toolsUtils from '@/utils/tools.js'
import { setAtomConfigApiUrls } from '@/config/setting.js'
import { errorHandler } from '@/utils/errorHandler.js'

export default {
    name: 'BizSelector',
    data () {
        return {
            showList: false,
            searchStr: ''
        }
    },
    props: ['disabled'],
    computed: {
        ...mapState({
            site_url: state => state.site_url,
            username: state => state.username,
            cc_id: state => state.cc_id,
            bizList: state => state.bizList
        }),
        businessList () {
            if (this.searchStr === '') {
                return this.bizList
            } else {
                const reg = new RegExp(this.searchStr)
                return this.bizList.filter(item => {
                    return reg.test(item.cc_name)
                })
            }
        },
        currentBizId: {
            get () {
                return this.cc_id
            },
            set (id) {
                this.setBizId(id)
            }
        },
        currentBizName () {
            const crtIndex = this.bizList.findIndex(item => Number(this.currentBizId) === item.cc_id)
            return crtIndex > -1 ? this.bizList[crtIndex].cc_name : ''
        }
    },
    created () {
        this.setTimezone(this.cc_id)
    },
    methods: {
        ...mapActions([
            'getBizList',
            'changeDefaultBiz',
            'getBusinessTimezone'
        ]),
        ...mapMutations([
            'setBizId',
            'setBusinessTimezone'
        ]),
        async onSelectBiz (id) {
            this.showList = false
            try {
                const res = await this.changeDefaultBiz(id)
                if (res.result) {
                    await this.setTimezone(id)
                    setAtomConfigApiUrls(this.site_url, id)
                    this.$router.push({path: `/business/home/${id}/`})
                    // notice: 清除标准插件配置项里的全局变量缓存
                    $.atoms = {}
                } else {
                    errorHandler(res, this)
                }
            } catch (e) {
                errorHandler(e, this)
            }
        },
        onToggleBizList () {
            if (this.disabled) {
                this.showList = false
            } else {
                this.showList = !this.showList
            }
        },
        onHideBizList () {
            this.showList = false
        },
        async setTimezone (ccId) {
            // 需要进行整型转换
            const nowCCId = Number(ccId)
            if (this.bizList.length !== 0) {
                // 有业务列表不需要直接接口拉
                let business = this.bizList.find((business) => business.cc_id === nowCCId)
                let timezone = 'Asia/Shanghai'
                if (business !== undefined) {
                    // 业务如果不携带时区信息即undefined情况
                    timezone = business.time_zone || 'Asia/Shanghai'
                }
                this.setBusinessTimezone(timezone)
            } else {
                await this.getBusinessTimezone()
            }
        }
    }
}
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';

.biz-wrapper {
    float: left;
    position: relative;
    margin-top: 9px;
    width: 200px;
    color: #979ba5;
    font-size: 14px;
}
.current-biz-name {
    position: relative;
    padding: 0 20px 0 10px;
    height: 32px;
    line-height: 32px;
    border: 1px solid #445060;
    border-radius: 2px;
    cursor: pointer;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
    &:after {
        content: '';
        position: absolute;
        top: 12px;
        right: 10px;
        width: 0;
        height: 0;
        border-style: solid;
        border-width: 8px 6px 0 6px;
        border-color: #63656e transparent transparent transparent;
        transition: transform 0.3s ease-in-out;
    }
    &:hover {
        color: #ffffff;
        border-color: #616d7d;
    }
    &.list-open:after {
        transform: rotate(180deg);
        transform-origin: center;
    }
}
.disabled-biz-name {
    cursor: not-allowed;
    &:hover {
        color: #979ba5;
        border-color: #445060;
    }
}
/*业务下拉列表*/
.biz-list {
    position: absolute;
    top: 34px;
    left: 0;
    background: #ffffff;
    z-index: 1001;
    width: 100%;
    max-height: 290px;
    border-radius: 0 0 2px 2px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.16);
    overflow-y: auto;
    @include scrollbar;
    .biz-item {
        padding: 0 10px;
        height: 30px;
        line-height: 30px;
        color: #333333;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
        user-select: none;
        cursor: pointer;
        &:hover {
            color: $blueDefault;
        }
        &.selected {
            background: $blueDefault;
            color: #ffffff;
        }
    }
}
.search-wrapper {
    margin: 5px auto;
    width: 190px;
    .search-input {
        padding: 0 30px 0 10px;
        width: 190px;
        height: 36px;
        line-height: 36px;
        font-size: 14px;
        background: $whiteDefault;
        border: 1px solid $commonBorderColor;
        outline: none;
        &:hover {
            border-color: #c0c4cc;
        }
        &:focus {
            border-color: $blueDefault;
            & + i {
                color: $blueDefault;
            }
        }
    }
    .common-icon-search {
        position: absolute;
        right: 12px;
        top: 16px;
        color: $commonBorderColor;
    }
}

</style>

