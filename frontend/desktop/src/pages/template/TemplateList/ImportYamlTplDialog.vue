<template>
    <bk-dialog
        class="import-yaml-dialog"
        width="850"
        header-position="left"
        :mask-close="false"
        :ext-cls="'common-dialog'"
        :title="$t('导入') + 'YAML'"
        :value="isShow"
        @cancel="onCloseDialog">
        <div class="import-dialog-content">
            <div v-if="!file || !importData" class="upload-file-area">
                <bk-upload
                    accept=".yaml,.yml"
                    url=""
                    :limit="1"
                    :tip="$t('支持YAML类型文件，文件小于2M')"
                    :custom-request="handleUpload">
                </bk-upload>
            </div>
            <div v-else class="import-check-wrapper">
                <bk-alert :type="checkResult ? 'success' : 'error'">
                    <div slot="title">
                        {{ file.name }}
                        {{ checkResult ? $t('文件合法性检查通过。') : $t('文件不合法，请') }}
                        <template v-if="!checkResult">
                            <a class="view-result-btn" href="#checkMsgTitle">{{ $t('查看合法检查结果') }}</a>
                            {{ $t('或') }}
                        </template>
                        <label
                            :for="checkPending ? '' : 'tpl-file'"
                            :class="['upload-tpl-btn', { 'is-disabled': checkPending }]">
                            {{ $t('重新上传文件') }}
                        </label>
                        <input
                            ref="tplFile"
                            id="tpl-file"
                            type="file"
                            accept=".yaml,.yml"
                            style="display: none;"
                            @change="onFileChange" />
                    </div>
                </bk-alert>
                <div class="table-title">
                    <span>{{ $t('文件解析流程') + $t('（') }}{{ ('file' in importData.error) ? 0 : importData.yaml_docs.length }}{{ $t('）') }}</span>
                    <bk-pagination
                        v-if="pagination.count > 5"
                        small
                        :current="pagination.current"
                        :count="pagination.count"
                        :limit-list="[5]"
                        :limit="5"
                        :show-limit="false"
                        @change="onPageChange">
                    </bk-pagination>
                </div>
                <bk-table :data="tableList" :key="Math.random()">
                    <bk-table-column :label="$t('流程名称')" show-overflow-tooltip>
                        <template slot-scope="props">
                            {{ props.row.meta.name }}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="$t('父流程')" show-overflow-tooltip>
                        <template slot-scope="props">
                            {{ importData.relations[props.row.meta.id] ? importData.relations[props.row.meta.id].map(item => item.name).join(',') : '--' }}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="$t('是否覆盖已有流程')">
                        <template slot-scope="props">
                            <bk-select
                                :placeholder="$t('请选择需要覆盖的流程')"
                                :loading="tplLoading"
                                :searchable="true"
                                :value="overriders[props.row.meta.id]"
                                @clear="onClearOverrideTpl(props.row.meta.id)"
                                @selected="onSelectOverrideTpl(props.row.meta.id, $event)">
                                <bk-option
                                    v-for="item in templateList"
                                    :key="item.id"
                                    :id="item.id"
                                    :name="item.name">
                                    {{ item.name }}
                                </bk-option>
                            </bk-select>
                        </template>
                    </bk-table-column>
                </bk-table>
                <div class="check-msg-title" id="checkMsgTitle">{{ $t('合法性检测结果') }}</div>
                <div class="check-msg">
                    <template v-if="!errorMsg">{{ $t('合法性检查通过。') }}</template>
                    <template v-else>
                        <template v-if="Array.isArray(errorMsg)">
                            <p v-for="(item, index) in errorMsg" :key="index">{{ item }}</p>
                        </template>
                        <template v-else>{{ errorMsg }}</template>
                    </template>
                </div>
            </div>
        </div>
        <div class="footer-wrap" slot="footer">
            <label
                :for="checkPending ? '' : 'tpl-file'"
                :class="['upload-tpl-btn', { 'is-disabled': checkPending, 'is-hide': !file || !importData }]">
                {{ $t('重新上传文件') }}
            </label>
            <div class="operate-area">
                <bk-button
                    theme="primary"
                    :disabled="!checkResult || checkPending"
                    :loading="importPending"
                    @click="onConfirm">
                    {{ $t('导入') }}
                </bk-button>
                <bk-button @click="onCloseDialog">{{ $t('取消') }}</bk-button>
            </div>
        </div>
    </bk-dialog>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions } from 'vuex'

    export default {
        name: 'ImportYamlTplDialog',
        props: {
            isShow: {
                type: Boolean,
                default: false
            },
            common: String,
            project_id: [String, Number]
        },
        data () {
            return {
                file: null,
                importData: null,
                checkResult: false,
                templateList: [],
                overriders: {},
                errorMsg: null,
                checkPending: false,
                importPending: false,
                tplLoading: false,
                pagination: {
                    current: 1,
                    count: 0
                }
            }
        },
        computed: {
            tableList () {
                if (this.importData && this.importData.yaml_docs && !('file' in this.importData.error)) {
                    return this.importData.yaml_docs.slice((this.pagination.current - 1) * 5, this.pagination.current * 5)
                }
                return []
            }
        },
        methods: {
            ...mapActions('templateList', [
                'loadTemplateList',
                'yamlTplImport',
                'yamlTplImportCheck'
            ]),
            async handleUpload (file) {
                try {
                    this.checkPending = true
                    this.file = file.fileObj.origin
                    const data = new FormData()
                    data.append('data_file', this.file)
                    const res = await this.yamlTplImportCheck(data)
                    this.checkResult = res.result ? (typeof res.data.error === 'string' ? res.data.error === '' : Object.keys(res.data.error).length === 0) : false
                    if (res.result) {
                        this.importData = res.data
                        this.pagination.current = 1
                        this.pagination.count = ('file' in res.data.error) ? 0 : res.data.yaml_docs.length
                        this.overriders = {}
                        this.errorMsg = this.handleErrorMsg(res.data)
                        this.getTemplateData()
                    } else {
                        this.errorMsg = res.message
                    }
                } catch (error) {
                    console.log(error)
                } finally {
                    this.checkPending = false
                    this.$nextTick(() => {
                        if (this.$refs.tplFile) {
                            this.$refs.tplFile.value = null
                        }
                    })
                }
            },
            async getTemplateData () {
                this.tplLoading = true
                try {
                    const data = {}
                    if (this.common) {
                        data.common = 1
                    } else {
                        data.project__id = this.project_id
                    }
                    const respData = await this.loadTemplateList(data)
                    this.templateList = respData.objects
                } catch (e) {
                    console.log(e)
                } finally {
                    this.tplLoading = false
                }
            },
            handleErrorMsg (data) {
                if (data && data.error && Object.keys(data.error).length > 0) {
                    const errors = []
                    Object.keys(data.error).forEach(item => {
                        errors.push(...data.error[item])
                    })
                    return errors
                }
                return null
            },
            onFileChange (e) {
                const file = e.target.files[0]
                if (file) {
                    const filename = file.name
                    const ext = filename.substr(filename.lastIndexOf('.') + 1)
                    if (ext !== 'yaml') {
                        this.file = null
                        return
                    }
                    this.handleUpload({ fileObj: { origin: file } })
                }
            },
            onPageChange (val) {
                this.pagination.current = val
            },
            onSelectOverrideTpl (tpl, id) {
                this.$set(this.overriders, tpl, id)
            },
            onClearOverrideTpl (tpl) {
                this.$delete(this.overriders, tpl)
            },
            async onConfirm () {
                const overriderKeys = Object.keys(this.overriders)
                const overrideTpl = []
                if (overriderKeys.length > 0) {
                    const hasRepeat = overriderKeys.some(key => {
                        const id = this.overriders[key]
                        if (overrideTpl.includes(id)) {
                            const tpl = this.templateList.find(item => item.id === id)
                            this.$bkMessage({
                                message: i18n.t('流程') + tpl.name + i18n.t('不能被重复覆盖'),
                                theme: 'error',
                                ellipsisLine: 0
                            })
                            return true
                        } else {
                            overrideTpl.push(id)
                        }
                    })
                    if (hasRepeat) {
                        return
                    }
                }

                try {
                    this.importPending = true
                    const data = new FormData()
                    data.append('data_file', this.file)
                    data.append('override_mappings', JSON.stringify(this.overriders))
                    if (this.common) {
                        data.append('template_type', 'common')
                    } else {
                        data.append('template_type', 'project')
                        data.append('project_id', this.project_id)
                    }
                    const res = await this.yamlTplImport(data)
                    if (res.result) {
                        this.$emit('confirm')
                        this.resetData()
                    }
                } catch (error) {
                    console.log(error)
                } finally {
                    this.importPending = false
                }
            },
            onCloseDialog () {
                this.$emit('update:isShow', false)
                this.resetData()
            },
            resetData () {
                this.file = null
                this.importData = null
                this.checkResult = false
                this.overriders = {}
                if (this.$refs.tplFile) {
                    this.$refs.tplFile.value = null
                }
                this.pagination = {
                    current: 1,
                    count: 0
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';
    .import-dialog-content {
        padding-left: 24px;
        height: 365px;
        overflow-y: auto;
        @include scrollbar;
    }
    .upload-file-area {
        width: 530px;
        margin: 120px auto 0;
        /deep/.file-wrapper {
            background: #fafbfd;
        }
    }
    .import-check-wrapper {
        height: 100%;
        margin-right: 25px;
    }
    .bk-button-text {
        font-size: 12px;
    }
    .view-result-btn, .upload-tpl-btn {
        color: #3a84ff;
        cursor: pointer;
        font-size: 12px;
    }
    .table-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 16px 0 4px;
        & > span {
            font-size: 14px;
            color: #313237;
        }
    }
    .check-msg-title {
        margin-top: 26px;
        font-size: 14px;
        color: #313237;
    }
    .check-msg {
        padding: 10px 0 10px;
        font-size: 12px;
        color: #696a72;
    }
</style>
<style lang="scss">
    .import-yaml-dialog {
        .bk-dialog-content {
            height: 480px;
            .bk-dialog-tool {
                min-height: 0;
            }
            .bk-dialog-header {
                margin-top: 0;
                padding-left: 24px;
                border-bottom: none;
            }
        }
        .footer-wrap {
            display: flex;
            align-items: center;
            justify-content: space-between;
            .upload-tpl-btn {
                font-size: 14px;
                &.is-hide {
                    transform: scale(0);
                }
            }
        }
    }
</style>
