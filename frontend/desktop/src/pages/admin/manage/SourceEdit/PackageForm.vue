/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
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
                {{i18n.sourceName}}: {{ name || i18n.noName }}
            </div>
            <bk-button
                theme="default"
                size="small"
                class="delete-btn"
                @click="onDeleteSource">
                {{i18n.delete}}
            </bk-button>
            <div class="error-msg" v-if="showError">{{i18n.errorMsg}}</div>
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
                                <input
                                    type="text"
                                    class="package-name"
                                    name="packageName"
                                    v-model="name"
                                    v-validate="packageNameRule"
                                    :disabled="isEditing"
                                    :class="{ 'error-border': errors.first('packageName') }"
                                    @blur="onPackageNameBlur">
                                <i class="common-icon-info common-error-tip" v-bk-tooltips.top="errors.first('packageName')"></i>
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
                                <bk-select
                                    v-model="type"
                                    class="bk-select-inline"
                                    :disabled="isEditing"
                                    :popover-width="260"
                                    :searchable="true"
                                    @selected="onTypeSelect">
                                    <bk-option
                                        v-for="(option, index) in list"
                                        :key="index"
                                        :id="option.id"
                                        :name="option.name">
                                    </bk-option>
                                </bk-select>
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
                                <textarea
                                    rows="4"
                                    class="package-desc"
                                    v-model="desc"
                                    @blur="onPackageDescBlur">
                                </textarea>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <th>
                            <div class="form-label">
                                <label>{{i18n.detail}}</label>
                            </div>
                        </th>
                        <td class="value">
                            <table class="detail-table">
                                <tbody>
                                    <tr v-for="field in detailFields" :key="field.id">
                                        <th>{{field.name}}</th>
                                        <td class="td-with-input"
                                            :class="{ 'error-border': errors.first('detailValue' + field.id) }">
                                            <input
                                                type="text"
                                                class="table-input"
                                                :name="'detailValue' + field.id"
                                                :placeholder="field.placeholder"
                                                v-model="details[field.id]"
                                                v-validate="valueRule"
                                                @blur="onDetailInputBlur(field.id)">
                                            <i class="common-icon-info common-error-tip" v-bk-tooltips.top="i18n.required"></i>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <th>
                            <div class="form-label">
                                <label>{{i18n.module}}</label>
                            </div>
                        </th>
                        <td class="value">
                            <div class="module-table-wrapper">
                                <table class="module-table">
                                    <thead>
                                        <tr>
                                            <th>{{i18n.subModule}}</th>
                                            <th>{{i18n.version}}</th>
                                            <th>{{i18n.importModule}}</th>
                                            <th>{{i18n.operation}}</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="(item, index) in packageValues" :key="index">
                                            <td
                                                :class="{ 'error-border': errors.first('moduleName' + index) }"
                                                class="td-with-input">
                                                <input
                                                    type="text"
                                                    class="table-input"
                                                    :name="'moduleName' + index"
                                                    :placeholder="i18n.placeholder"
                                                    v-model="item.key"
                                                    v-validate="packageNameRule"
                                                    @blur="onPackageInputBlur($event, 'key', index)">
                                                <i class="common-icon-info common-error-tip" v-bk-tooltips.top="i18n.required"></i>
                                            </td>
                                            <td
                                                :class="{ 'error-border': errors.first('moduleVersion' + index) }"
                                                class="td-with-input">
                                                <input
                                                    type="text"
                                                    class="table-input"
                                                    :name="'moduleVersion' + index"
                                                    :placeholder="i18n.placeholder"
                                                    v-model="item.version"
                                                    v-validate="valueRule"
                                                    @blur="onPackageInputBlur($event, 'version', index)">
                                                <i class="common-icon-info common-error-tip" v-bk-tooltips.top="i18n.required"></i>
                                            </td>
                                            <td
                                                :class="{ 'error-border': errors.first('modules' + index) }"
                                                class="td-with-input">
                                                <input
                                                    type="text"
                                                    class="table-input"
                                                    :name="'modules' + index"
                                                    :placeholder="i18n.importPlaceholder"
                                                    v-model="item.modules"
                                                    v-validate="valueRule"
                                                    @blur="onPackageInputBlur($event, 'modules', index)">
                                                <i class="common-icon-info common-error-tip" v-bk-tooltips.top="i18n.required"></i>
                                            </td>
                                            <td>
                                                <bk-button
                                                    size="small"
                                                    class="delete-btn"
                                                    :class="{ 'default-color': !isShowDelete }"
                                                    @click="onDeletePackage(index)">
                                                    {{ modulesOptName }}
                                                </bk-button>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                                <div class="add-module">
                                    <bk-button theme="default" size="small" class="add-btn" @click="onAddPackage">{{i18n.add}}</bk-button>
                                </div>
                                <div v-if="showModuleError" class="common-error-tip error-msg">{{i18n.required}}</div>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { SOURCE_TYPE } from '@/constants/manage.js'
    import { PACKAGE_NAME_REG, STRING_LENGTH } from '@/constants/index.js'

    export default {
        name: 'PackageForm',
        props: {
            value: {
                type: Object,
                default () {
                    return {
                        id: undefined,
                        name: '',
                        type: 'git',
                        desc: '',
                        details: {
                            repo_address: '',
                            repo_raw_address: '',
                            branch: ''
                        },
                        packages: {}
                    }
                }
            },
            sourceIndex: {
                type: Number,
                default: 0
            }
        },
        data () {
            const list = this.getSourceTypeList()
            const { name, type, desc, details, packages } = this.value
            const packageValues = this.getPackageValues(packages)
            const [detailFields] = this.getSourceKeys(type)
            return {
                name,
                type,
                desc,
                details,
                packages,
                list,
                detailFields,
                packageValues,
                isSettingPanelShow: true,
                showError: false, // 包源配置错误
                showModuleError: false, // 模块配置错误
                packageNameRule: { // 名称校验规则
                    required: true,
                    max: STRING_LENGTH.SOURCE_NAME_MAX_LENGTH,
                    regex: PACKAGE_NAME_REG
                },
                valueRule: {
                    required: true
                },
                i18n: {
                    sourceName: gettext('包源名'),
                    noName: gettext('未命名'),
                    delete: gettext('删除'),
                    name: gettext('名称'),
                    type: gettext('类型'),
                    desc: gettext('描述'),
                    detail: gettext('详细信息'),
                    module: gettext('模块配置'),
                    placeholder: gettext('请输入'),
                    importPlaceholder: gettext('请输入模块绝对路径，如a.b.c，多个用,分隔'),
                    subModule: gettext('根模块'),
                    version: gettext('版本'),
                    importModule: gettext('导入模块'),
                    operation: gettext('操作'),
                    add: gettext('添加'),
                    errorMsg: gettext('输入有误，请展开检查'),
                    required: gettext('必填项')
                }
            }
        },
        computed: {
            isEditing () {
                return typeof this.value.id === 'number'
            },
            isShowDelete () {
                return this.packageValues && this.packageValues.length > 1
            },
            modulesOptName () {
                return this.isShowDelete ? this.i18n.delete : '--'
            }
        },
        methods: {
            getSourceTypeList () {
                return SOURCE_TYPE.map(item => {
                    return {
                        id: item.type,
                        name: item.name
                    }
                })
            },
            getSourceKeys (type) {
                const detailFields = []
                const detailValues = {}

                const source = SOURCE_TYPE.find(item => item.type === type)
                for (const key in source.keys) {
                    detailFields.push({
                        id: key,
                        name: source.keys[key].name,
                        placeholder: source.keys[key].placeholder
                    })
                    detailValues[key] = ''
                }

                return [detailFields, detailValues]
            },
            /**
             * packages 的值由对象转为数组 packageValues
             */
            getPackageValues (packages) {
                const values = []
                if (JSON.stringify(packages) === '{}') {
                    values.push({
                        key: '',
                        version: '',
                        modules: ''
                    })
                }
                for (const key in packages) {
                    const pkg = packages[key]
                    values.push({
                        key: key,
                        version: pkg.version,
                        modules: Array.isArray(pkg.modules) ? pkg.modules.join(',') : pkg.modules
                    })
                }
                return values
            },
            /**
             * packageValues 的值由数组转为对象 packages
             */
            getPackages () {
                const packages = {}
                this.packageValues.forEach(item => {
                    if (item.key) {
                        packages[item.key] = {
                            version: item.version,
                            modules: Array.isArray(item.modules) ? item.modules : item.modules.split(',')
                        }
                    }
                })
                return packages
            },
            updateValue (key, val) {
                this.$emit('updateSource', key, val, this.sourceIndex)
            },
            validate () {
                return this.$validator.validateAll().then(result => {
                    if (this.packageValues.length === 0) {
                        this.showModuleError = true
                    }
                    return result && !this.showModuleError
                })
            },
            onTogglePanelShow () {
                this.isSettingPanelShow = !this.isSettingPanelShow
                if (!this.isSettingPanelShow) {
                    this.validate().then(result => {
                        if (!result) {
                            this.showError = true
                        }
                    })
                } else {
                    this.showError = false
                }
            },
            onTypeSelect (type) {
                this.type = type;
                [this.detailFields, this.details] = this.getSourceKeys(type)
                this.updateValue('type', this.type)
                this.updateValue('details', this.details)
            },
            onAddPackage () {
                this.packageValues.push({
                    key: '',
                    version: '',
                    modules: []
                })
                this.showModuleError = false
            },
            /**
             * 删除模块配置（只有一条时不显示删除按钮）
             */
            onDeletePackage (index) {
                if (!this.isShowDelete) return
                this.packageValues.splice(index, 1)
                const packages = this.getPackages()
                this.updateValue('packages', packages)
                if (Object.keys(packages).length === 0) {
                    this.showModuleError = true
                }
            },
            onPackageNameBlur () {
                this.updateValue('name', this.name)
            },
            onPackageDescBlur () {
                this.updateValue('desc', this.desc)
            },
            onDetailInputBlur (field) {
                this.updateValue('details', this.details)
            },
            onPackageInputBlur (e, type, index) {
                const val = e.target.value
                this.packageValues[index][type] = val
                const packages = this.getPackages()
                this.updateValue('packages', packages)
            },
            onDeleteSource () {
                this.$emit('deleteSource')
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/mixins/input-error.scss';
    /deep/ .bk-select {
        background-color: #ffffff;
        &.is-disabled {
            background-color: #fafafa;
        }
    }
    .package-form {
        margin-bottom: 30px;
        background: #f0f1f5;
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
            max-width: 300px;
            white-space: nowrap;
            text-overflow: ellipsis;
            overflow: hidden;
            vertical-align: middle;
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
            top: 22px;
            right: 20px;
            font-size: 12px;
        }
        .error-msg {
            position: absolute;
            top: 25px;
            left: 350px;
            font-size: 14px;
            line-height: 1;
            color: #ff5757;
        }
    }
    .delete-btn,
    .add-btn {
        padding: 0;
        background: transparent;
        border: none;
        color: #3a84ff;
        height: auto;
        line-height: initial;
    }
    .default-color {
        color: #313238;
    }
    .package-setting {
        padding: 0 20px 20px;
    }
    .form-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
        th, td {
            padding: 10px;
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
        .td-with-input {
            &:hover{
                border-style: double;
                border-color: #3c96ff;
            }
            @include common-input-error;
        }
        .form-content {
            position: relative;
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
            &[disabled="disabled"] {
                color: #aaa;
                cursor: not-allowed;
                background: #fafafa;
                &:hover {
                    border-color: #c3cdd7;
                }
            }
            @include common-input-error;
        }
        .package-desc {
            display: block;
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
        font-size: 12px;
        border-collapse: collapse;
        background: #ffffff;
        th,td {
            position: relative;
            padding: 10px 20px;
            border: 1px solid #dde4eb;
        }
        th {
            width: 30%;
            font-weight: 700;
            text-align: center;
        }
    }
    .module-table-wrapper {
        position: relative;
    }
    .module-table {
        width: 100%;
        font-size: 12px;
        border-collapse: collapse;
        background: #ffffff;
        text-align: center;
        th,td {
            position: relative;
            padding: 10px 20px;
            border: 1px solid #dde4eb;
        }
        th {
            font-weight: 700;
            text-align: center;
            &:nth-child(1),
            &:nth-child(2),
            &:nth-child(4) {
                width: 16.66%;
            }
            &:nth-child(3) {
                width: 50%;
            }
        }
        input[aria-invalid="true"] + .common-error-tip {
            display: inline-block;
        }
        .common-error-tip {
            display: none;
            bottom: 0;
        }
        tbody {
            td {
                padding: 10px 20px;
            }
        }
    }
    .detail-table, .module-table {
        .td-with-input {
            &:hover{
                border-style: double;
                border-color: #3c96ff;
            }
            @include common-input-error;
        }

    }
    .table-input {
        width: 100%;
        color: #333333;
        border: none;
        outline: none;
    }
    .add-module {
        height: 40px;
        line-height: 40px;
        font-size: 12px;
        text-align: center;
        color: #3a84ff;
        background: #ffffff;
        border: 1px solid #dde4eb;
        border-top: none;
    }
</style>
