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
    <div class="cache-edit">
        <div class="cache-content">
            <h3 class="edit-title">step1.{{ i18n.setting + i18n.cache }}</h3>
            <div class="cache-setting">
                <table class="form-table">
                    <tbody>
                        <tr>
                            <th>
                                <div class="form-label required">
                                    <label>{{i18n.name}}</label>
                                </div>
                            </th>
                            <td class="value">
                                <div class="form-content">
                                    <input type="text" class="cache-name" v-model="name">
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <th>
                                <div class="form-label required">
                                    <label>{{i18n.type}}</label>
                                </div>
                            </th>
                            <td class="value">
                                <div class="form-content">
                                    <bk-selector
                                        :list="list"
                                        :selected="type"
                                        @item-selected="onTypeSelect">
                                    </bk-selector>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <th>
                                <div class="form-label">
                                    <label>{{i18n.desc}}</label>
                                </div>
                            </th>
                            <td class="value">
                                <div class="form-content">
                                    <textarea rows="4" class="cache-desc"></textarea>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <th>
                                <div class="form-label required">
                                    <label>{{i18n.detail}}</label>
                                </div>
                            </th>
                            <td class="value">
                                <table class="detail-table">
                                    <tbody>
                                        <tr>
                                            <th>仓库地址</th>
                                            <td>http://tag.open.com</td>
                                        </tr>
                                        <tr>
                                            <th>仓库静态文件地址</th>
                                            <td>gdfgf</td>
                                        </tr>
                                        <tr>
                                            <th>分支</th>
                                            <td>fsdfsdfsdfsdf</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        <div class="operate-area">
            <router-link to="/admin/manage/source_edit/package_edit/" class="bk-button bk-default">{{ i18n.prevStep }}</router-link>
            <a class="bk-button bk-success" @click="onSaveSetting">{{ i18n.save }}</a>
            <router-link to="/admin/manage/source_manage/" class="bk-button bk-default">{{ i18n.cancel }}</router-link>
        </div>
    </div>
</template>
<script>
    export default {
        name: 'PackageEdit',
        data () {
            return {
                name: '',
                type: 'git',
                desc: '',
                list: [],
                i18n: {
                    setting: gettext('配置'),
                    cache: gettext('本地缓存'),
                    prevStep: gettext('上一步'),
                    save: gettext('完成'),
                    cancel: gettext('取消'),
                    name: gettext('名称'),
                    type: gettext('类型'),
                    desc: gettext('描述'),
                    detail: gettext('详细信息')
                }
            }
        },
        methods: {
            onSaveSetting () {
                console.log('save')
            },
            onTypeSelect (type) {
                this.type = type
            }
        }
    }
</script>
<style lang="scss" scoped>
    .cache-edit {
        height: calc(100% - 60px);
        background: #ffffff;
    }
    .cache-content {
        padding: 30px 60px 60px;
        min-height: 100%;
    }
    .edit-title {
        margin: 0 0 30px;
        font-size: 20px;
    }
    .form-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
        th, td {
            padding: 9px;
        }
        th {
            position: relative;
            width: 16%;
            color: #313238;
            font-weight: 400;
        }
        .form-label {
            padding-right: 20%;
            text-align: right;
            label {
                position: relative;
            }
            &.required {
                label:after {
                    content: '*';
                    position: absolute;
                    top: 1px;
                    right: -10px;
                    color: #F00;
                    font-family: "SimSun";
                }
            }
            
        }
        .form-content {
            width: 40%;
        }
        .cache-name {
            padding: 0 10px;
            width: 100%;
            height: 32px;
            line-height: 32px;
            border: 1px solid #c3cdd7;
            border-radius: 2px;
            color: #63656e;
            outline: none;
            &:hover {
                border-color: #3c96ff;
            }
            &:active {
                border-color: #3c96ff;
            }
        }
        .cache-desc {
            display: inline-block;
            padding: 10px;
            width: 100%;
            border: 1px solid #c3cdd7;
            border-radius: 2px;
            color: #63656e;
            outline: none;
            resize: vertical;
            min-height: 102px;
            max-height: 140px;
            &:hover {
                border-color: #3c96ff;
            }
            &:active {
                border-color: #3c96ff;
            }
        }
    }
    .detail-table {
        width: 100%;
        border-collapse: collapse;
        background: #ffffff;
        th,td {
            padding: 10px 20px;
            border: 1px solid #dde4eb;
        }
        th {
            width: 30%;
            font-weight: 700;
            text-align: center;
        }
    }
    .operate-area {
        margin-top: -60px;
        padding: 0 60px;
        height: 60px;
        line-height: 60px;
        border-top: 1px solid #cacedb;
        .bk-button {
            height: 32px;
            line-height: 32px;
        }
    }
</style>
