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
    <div class="package-form">
        <div class="form-header">
            <div
                :class="['title', { 'fold': !isSettingPanelShow }]"
                @click="onTogglePanelShow">
                {{i18n.sourceName}}: main_source1
            </div>
            <bk-button type="default" size="mini" class="delete-btn">{{i18n.delete}}</bk-button>
        </div>
        <div class="package-setting" v-show="isSettingPanelShow">
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
                                <input type="text" class="package-name" v-model="name">
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
                                <textarea rows="4" class="package-desc"></textarea>
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
                    <tr>
                        <th>
                            <div class="form-label required">
                                <label>{{i18n.module}}</label>
                            </div>
                        </th>
                        <td class="value">
                            <table class="module-table">
                                <thead>
                                    <tr>
                                        <th>{{i18n.rootModule}}</th>
                                        <th>{{i18n.version}}</th>
                                        <th>{{i18n.importModule}}</th>
                                        <th>{{i18n.operation}}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>fccdsadf</td>
                                        <td>1.0</td>
                                        <td>fasdfasdfasdf</td>
                                        <td><bk-button type="default" size="mini" class="delete-btn">{{i18n.delete}}</bk-button></td>
                                    </tr>
                                </tbody>
                            </table>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
<script>
    export default {
        name: 'PackageForm',
        data () {
            return {
                name: '',
                type: 'git',
                desc: '',
                info: {},
                module: [],
                list: [{ id: 'git', name: 'Git' }],
                isSettingPanelShow: true,
                i18n: {
                    sourceName: gettext('包源名'),
                    delete: gettext('删除'),
                    name: gettext('名称'),
                    type: gettext('类型'),
                    desc: gettext('描述'),
                    detail: gettext('详细信息'),
                    module: gettext('模块配置'),
                    rootModule: gettext('根模块'),
                    version: gettext('版本'),
                    importModule: gettext('导入模块'),
                    operation: gettext('操作')
                }
            }
        },
        methods: {
            onTogglePanelShow () {
                this.isSettingPanelShow = !this.isSettingPanelShow
            },
            onTypeSelect (type) {
                this.type = type
            }
        }
    }
</script>
<style lang="scss" scoped>
    .package-form {
        margin-bottom: 30px;
        background: rgb(240, 241, 245);
        border-radius: 2px;
    }
    .form-header {
        position: relative;
        padding: 20px 20px 15px;
        .title {
            display: inline-block;
            position: relative;
            padding-left: 20px;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
                &:before {
                    border-color: #3a84ff transparent transparent transparent;
                }
            }
            &.fold {
                &:before {
                    top: 7px;
                    transform: rotate(-90deg);
                }
            }
            &:before {
                content: '';
                position: absolute;
                top: 8px;
                left: 2px;
                width: 0;
                height: 0;
                border-style: solid;
                border-width: 6px 5px 0 5px;
                border-color: #cccccc transparent transparent transparent;
                transition: transform 0.3s ease-in-out;
            }
        }
        .delete-btn {
            position: absolute;
            top: 20px;
            right: 20px;
            font-size: 14px;
        }
    }
    .delete-btn {
        padding: 0;
        background: transparent;
        border: none;
        color: #3a84ff;
    }
    .package-setting {
        padding: 0 20px 20px;
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
        .package-name {
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
        .package-desc {
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
    .module-table {
        width: 100%;
        border-collapse: collapse;
        background: #ffffff;
        text-align: center;
        th,td {
            padding: 10px 20px;
            border: 1px solid #dde4eb;
        }
        th {
            font-weight: 700;
            text-align: center;
        }
    }
</style>
