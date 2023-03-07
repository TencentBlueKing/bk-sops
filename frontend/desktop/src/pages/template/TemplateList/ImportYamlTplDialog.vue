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
            <!-- 上传区域 -->
            <div v-if="!file || !importData" class="upload-file-area">
                <bk-upload
                    accept=".yaml,.yml"
                    url=""
                    :limit="1"
                    :size="2048"
                    :tip="$t('支持YAML类型文件，文件小于2G')"
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
                </div>
                <p class="tpl-type-title">{{ $t('顶层流程（n）', { n: topFlowList.length }) }}</p>
                <bk-table :data="topFlowTableList" :key="Math.random()">
                    <bk-table-column :label="$t('流程名称')">
                        <div slot-scope="props" v-bk-overflow-tips>
                            {{ props.row.meta.name }}
                        </div>
                    </bk-table-column>
                    <bk-table-column :label="$t('是否覆盖已有流程')" :width="400">
                        <template slot-scope="{ row }">
                            <div class="tpl-overrider-select">
                                <bk-select
                                    style="width: 180px;"
                                    :clearable="false"
                                    :value="row.refer"
                                    @change="handleTopFlowOverriver($event, row)">
                                    <bk-option id="noOverrider" :name="$t('不覆盖，新建流程')"></bk-option>
                                    <bk-option id="overrider" :name="$t('覆盖已有流程')"></bk-option>
                                </bk-select>
                                <bk-select
                                    v-if="row.meta.id in overriders"
                                    style="width: 180px; margin-left: 8px;"
                                    :placeholder="$t('请选择需要覆盖的流程')"
                                    :loading="tplLoading"
                                    :searchable="true"
                                    :value="overriders[row.meta.id]"
                                    ext-popover-cls="tpl-popover"
                                    enable-scroll-load
                                    :scroll-loading="{ isLoading: scrollLoading }"
                                    :remote-method="onTplSearch"
                                    @clear="overriders[row.meta.id] = ''"
                                    @selected="overriders[row.meta.id] = $event"
                                    @scroll-end="onSelectScrollLoad(row)">
                                    <bk-option
                                        v-for="item in (common ? commonTemplateList : templateList)"
                                        :key="item.id"
                                        :id="item.id"
                                        :disabled="!hasPermission(getApplyPerm(row), item.auth_actions)"
                                        :name="item.name">
                                        <p
                                            v-cursor="{ active: !hasPermission(getApplyPerm(row), item.auth_actions) }"
                                            @click="onTempSelect(row, item)">
                                            {{ item.name }}
                                        </p>
                                    </bk-option>
                                </bk-select>
                            </div>
                        </template>
                    </bk-table-column>
                </bk-table>
                <bk-pagination
                    v-if="topFlowPagination.count > 5"
                    small
                    align="right"
                    :current="topFlowPagination.current"
                    :count="topFlowPagination.count"
                    :limit-list="[5]"
                    :limit="5"
                    :show-limit="false"
                    @change="onTopFlowPageChange">
                </bk-pagination>
                <template v-if="subFlowList.length > 0">
                    <p class="tpl-type-title">{{ $t('子流程（n）', { n: subFlowList.length }) }}</p>
                    <bk-table :data="subFlowTableList" :key="Math.random()">
                        <bk-table-column :label="$t('流程名称')">
                            <div slot-scope="props" v-bk-overflow-tips>
                                {{ props.row.meta.name }}
                            </div>
                        </bk-table-column>
                        <bk-table-column :label="$t('父流程')">
                            <div slot-scope="props" v-bk-overflow-tips>
                                {{ importData.relations[props.row.meta.id] ? importData.relations[props.row.meta.id].map(item => item.name).join(',') : '--' }}
                            </div>
                        </bk-table-column>
                        <bk-table-column :label="$t('是否覆盖已有子流程（实验功能，请谨慎使用并选择正确的流程）')" :width="400">
                            <template slot-scope="{ row }">
                                <div class="tpl-overrider-select">
                                    <bk-select
                                        style="width: 180px;"
                                        :value="row.refer"
                                        :clearable="false"
                                        @change="handleSubFlowReferChange($event, row)">
                                        <bk-option id="noOverrider" :name="$t('不覆盖，新建子流程')"></bk-option>
                                        <bk-option id="overrider" :name="$t('覆盖已有子流程')"></bk-option>
                                        <bk-option v-if="!common" id="useExisting" :name="$t('不导入，复用项目子流程')"></bk-option>
                                        <bk-option id="useCommonExisting" :name="$t('不导入，复用公共子流程')"></bk-option>
                                    </bk-select>
                                    <bk-select
                                        :key="row.refer"
                                        v-if="row.meta.id in Object.assign({}, overriders, reference)"
                                        style="width: 180px; margin-left: 8px;"
                                        :placeholder="getPlaceholder(row)"
                                        :loading="tplLoading"
                                        :searchable="true"
                                        :value="overriders[row.meta.id]"
                                        ext-popover-cls="tpl-popover"
                                        enable-scroll-load
                                        :scroll-loading="{ isLoading: scrollLoading }"
                                        :remote-method="onCommonTplSearch"
                                        @clear="onClearRefer(row)"
                                        @selected="onSelectRefer(row, $event)"
                                        @scroll-end="onSelectScrollLoad(row)">
                                        <bk-option
                                            v-for="item in ((common || row.refer === 'useCommonExisting') ? commonTemplateList : templateList)"
                                            :key="item.id"
                                            :id="item.id"
                                            :disabled="!hasPermission(getApplyPerm(row), item.auth_actions)"
                                            :name="item.name">
                                            <p
                                                v-cursor="{ active: !hasPermission(getApplyPerm(row), item.auth_actions) }"
                                                @click="onTempSelect(row, item)">
                                                {{ item.name }}
                                            </p>
                                        </bk-option>
                                    </bk-select>
                                </div>
                            </template>
                        </bk-table-column>
                    </bk-table>
                    <bk-pagination
                        v-if="subFlowPagination.count > 5"
                        small
                        align="right"
                        :current="subFlowPagination.current"
                        :count="subFlowPagination.count"
                        :limit-list="[5]"
                        :limit="5"
                        :show-limit="false"
                        @change="onSubFlowPageChange">
                    </bk-pagination>
                </template>
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
    import tools from '@/utils/tools.js'
    import permission from '@/mixins/permission.js'

    export default {
        name: 'ImportYamlTplDialog',
        mixins: [permission],
        props: {
            isShow: {
                type: Boolean,
                default: false
            },
            common: String,
            project_id: [String, Number],
            projectName: String
        },
        data () {
            return {
                file: null,
                importData: null,
                checkResult: false,
                topFlowList: [], // 顶层流程
                subFlowList: [], // 子流程
                templateList: [],
                commonTemplateList: [],
                overriders: {}, // 配置覆盖的流程
                reference: {}, // 配置引用的流程
                errorMsg: null,
                checkPending: false,
                importPending: false,
                tplLoading: false,
                scrollLoading: false,
                topFlowPagination: {
                    current: 1,
                    count: 0
                },
                subFlowPagination: {
                    current: 1,
                    count: 0
                },
                totalPage: 1,
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 15
                },
                commonTotalPage: 1,
                commonPagination: {
                    current: 1,
                    count: 0,
                    limit: 15
                }
            }
        },
        computed: {
            // 顶层流程
            topFlowTableList () {
                return this.topFlowList.slice((this.topFlowPagination.current - 1) * 5, this.topFlowPagination.current * 5)
            },
            // 子流程
            subFlowTableList () {
                return this.subFlowList.slice((this.subFlowPagination.current - 1) * 5, this.subFlowPagination.current * 5)
            }
        },
        created () {
            this.onTplSearch = tools.debounce(this.handleTplSearch, 500)
            this.onCommonTplSearch = tools.debounce(this.handleCommonTplSearch, 500)
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
                        this.topFlowList = res.data.yaml_docs.filter(item => !(item.meta.id in res.data.relations))
                        this.topFlowList.forEach(item => {
                            item.refer = 'noOverrider'
                        })
                        this.overriders = {}
                        this.topFlowPagination = {
                            current: 1,
                            count: ('file' in res.data.error) ? 0 : this.topFlowList.length
                        }
                        this.subFlowList = res.data.yaml_docs.filter(item => item.meta.id in res.data.relations)
                        this.subFlowList.forEach(item => {
                            item.refer = 'noOverrider'
                        })
                        this.subFlowPagination = {
                            current: 1,
                            count: ('file' in res.data.error) ? 0 : this.subFlowList.length
                        }
                        this.errorMsg = this.handleErrorMsg(res.data)
                        // 查询项目流程列表及公共流程列表
                        let offset = (this.commonPagination.current - 1) * this.commonPagination.limit
                        const promiseArr = [this.getTemplateData({ common: 1, offset, limit: 15 })]
                        if (!this.common) {
                            offset = (this.pagination.current - 1) * this.pagination.limit
                            promiseArr.push(this.getTemplateData({ project__id: this.project_id, offset, limit: 15 }))
                        }
                        this.tplLoading = true
                        Promise.all(promiseArr).then(res => {
                            this.tplLoading = false
                        })
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
            async getTemplateData (data, add) {
                try {
                    const respData = await this.loadTemplateList(data)
                    if (data.common) {
                        if (add) {
                            this.commonTemplateList.push(...respData.results)
                        } else {
                            this.commonTemplateList = respData.results
                        }
                        this.commonPagination.count = respData.count
                    } else {
                        if (add) {
                            this.templateList.push(...respData.results)
                        } else {
                            this.templateList = respData.results
                        }
                        this.pagination.count = respData.count
                    }
                    const totalPage = Math.ceil(respData.count / 15)
                    const variable = data.common ? 'commonTotalPage' : 'totalPage'
                    if (!totalPage) {
                        this[variable] = 1
                    } else {
                        this[variable] = totalPage
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.scrollLoading = false
                }
            },
            // 下拉框搜索
            handleTplSearch (val) {
                this.pagination.current = 1
                this.flowName = val
                const params = this.getQueryData()
                this.getTemplateData(params)
            },
            // 公共模板下拉框搜索
            handleCommonTplSearch (val) {
                this.commonPagination.current = 1
                this.commonFlowName = val
                const params = this.getQueryData(true)
                this.getTemplateData(params)
            },
            // 下拉框滚动加载
            onSelectScrollLoad (row) {
                if (['useExisting', 'overrider'].includes(row.refer)) {
                    if (this.totalPage !== this.pagination.current) {
                        this.scrollLoading = true
                        this.pagination.current += 1
                        const params = this.getQueryData()
                        this.getTemplateData(params, true)
                    }
                } else if (row.refer === 'useCommonExisting') {
                    if (this.commonTotalPage !== this.commonPagination.current) {
                        this.scrollLoading = true
                        this.commonPagination.current += 1
                        const params = this.getQueryData(true)
                        this.getTemplateData(params, true)
                    }
                }
            },
            getQueryData (common = undefined) {
                let tplName, offset, projectId
                if (common) {
                    tplName = this.commonFlowName
                    offset = (this.commonPagination.current - 1) * this.commonPagination.limit
                } else {
                    tplName = this.flowName
                    offset = (this.pagination.current - 1) * this.pagination.limit
                    projectId = this.project_id
                }
                const data = {
                    project__id: projectId || undefined,
                    common,
                    offset,
                    limit: 15,
                    pipeline_template__name__icontains: tplName || undefined
                }
                return data
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
                    if (file.size > 2 * 1024 * 1024 * 1024) {
                        this.$bkMessage({ message: i18n.t('上传失败，YAML类型文件最大为2G'), theme: 'error', delay: 10000 })
                        return
                    }
                    const filename = file.name
                    const ext = filename.substr(filename.lastIndexOf('.') + 1)
                    if (ext !== 'yaml') {
                        this.file = null
                        return
                    }
                    this.handleUpload({ fileObj: { origin: file } })
                }
            },
            onTopFlowPageChange (val) {
                this.topFlowPagination.current = val
            },
            onSubFlowPageChange (val) {
                this.subFlowPagination.current = val
            },
            // 切换顶层流程覆盖选项
            handleTopFlowOverriver (val, tpl) {
                const templateId = tpl.meta.id
                tpl.refer = val
                if (val === 'overrider') {
                    this.$set(this.overriders, templateId, '')
                } else {
                    this.$delete(this.overriders, templateId)
                }
            },
            // 切换子流程导入规则
            handleSubFlowReferChange (val, tpl) {
                const templateId = tpl.meta.id
                tpl.refer = val
                if (val === 'overrider') {
                    this.$set(this.overriders, templateId, '')
                    this.$delete(this.reference, templateId)
                } else if (val === 'noOverrider') {
                    this.$delete(this.overriders, templateId)
                    this.$delete(this.reference, templateId)
                } else {
                    this.$delete(this.reference, templateId)
                    this.$delete(this.overriders, templateId)
                    this.$set(this.reference, templateId, '')
                }
            },
            getPlaceholder (row) {
                return row.refer === 'overrider'
                    ? this.$t('请选择需要覆盖的流程')
                    : (row.refer === 'useCommonExisting' || this.common)
                        ? this.$t('请选择复用的公共流程')
                        : this.$t('请选择复用的项目流程')
            },
            onSelectRefer (tpl, id) {
                const templateId = tpl.meta.id
                if (tpl.refer === 'overrider') {
                    this.overriders[templateId] = id
                } else if (tpl.refer === 'useExisting') {
                    this.reference[templateId] = {
                        template_id: id,
                        template_type: 'project'
                    }
                } else if (tpl.refer === 'useCommonExisting') {
                    this.reference[templateId] = {
                        template_id: id,
                        template_type: 'common'
                    }
                }
            },
            getApplyPerm (row) {
                if (this.common) {
                    return row.refer === 'overrider' ? ['common_flow_edit'] : ['common_flow_view']
                } else {
                    return row.refer === 'overrider'
                        ? ['flow_edit']
                        : row.refer === 'useCommonExisting'
                            ? ['common_flow_view']
                            : ['flow_view']
                }
            },
            onTempSelect (row, selectInfo) {
                const required = this.getApplyPerm(row)
                if (!this.hasPermission(required, selectInfo.auth_actions)) {
                    const permissionData = {
                        project: [{
                            id: this.project_id,
                            name: this.projectName
                        }]
                    }
                    if (this.common || row.refer === 'useCommonExisting') {
                        permissionData['common_flow'] = [{
                            id: selectInfo.id,
                            name: selectInfo.name
                        }]
                    } else {
                        permissionData['flow'] = [selectInfo]
                    }
                    this.applyForPermission(required, selectInfo.auth_actions, permissionData)
                }
            },
            onClearRefer (tpl) {
                const templateId = tpl.meta.id
                if (tpl.refer === 'overrider') {
                    this.overriders[templateId] = ''
                } else if (['useExisting', 'useCommonExisting'].includes(tpl.refer)) {
                    this.reference[templateId] = ''
                }
            },
            async onConfirm () {
                const overriderKeys = Object.keys(this.overriders)
                const overrideTpl = []
                // 校验是否存在覆盖流程未选择或者重复选择的情况
                if (overriderKeys.length > 0) {
                    const tplList = this.topFlowList.concat(this.subFlowList)
                    const hasRepeat = overriderKeys.some(key => {
                        const id = this.overriders[key]
                        if (overrideTpl.includes(id)) {
                            const templateList = this.common ? this.commonTemplateList : this.templateList
                            const tpl = templateList.find(item => item.id === id)
                            this.$bkMessage({
                                message: i18n.t('流程') + tpl.name + i18n.t('不能被重复覆盖'),
                                theme: 'error',
                                ellipsisLine: 0,
                                delay: 10000
                            })
                            return true
                        } else {
                            overrideTpl.push(id)
                        }
                    })
                    const hasEmpty = overriderKeys.some(key => {
                        if (this.overriders[key] === '') {
                            const tpl = tplList.find(item => item.meta.id === key)
                            this.$bkMessage({
                                message: i18n.t('请选择流程“x”需要覆盖的流程', { x: tpl.meta.name }),
                                theme: 'error',
                                ellipsisLine: 0,
                                delay: 10000
                            })
                            return true
                        }
                    })
                    if (hasRepeat || hasEmpty) {
                        return
                    }
                }
                // 校验使用已有流程的表单是否存在未选择的情况
                if (Object.keys(this.reference).length > 0) {
                    const hasEmpty = Object.keys(this.reference).some(key => {
                        if (this.reference[key] === '') {
                            const tpl = this.subFlowList.find(item => item.meta.id === key)
                            this.$bkMessage({
                                message: i18n.t('请选择流程“x”需要使用的流程', { x: tpl.meta.name }),
                                theme: 'error',
                                ellipsisLine: 0,
                                delay: 10000
                            })
                            return true
                        }
                    })
                    if (hasEmpty) {
                        return
                    }
                }

                try {
                    this.importPending = true
                    const data = new FormData()
                    data.append('data_file', this.file)
                    data.append('override_mappings', JSON.stringify(this.overriders))
                    data.append('refer_mappings', JSON.stringify(this.reference))
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
                this.reference = {}
                if (this.$refs.tplFile) {
                    this.$refs.tplFile.value = null
                }
                this.topFlowPagination = {
                    current: 1,
                    count: 0
                }
                this.subFlowPagination = {
                    current: 1,
                    count: 0
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';
    .upload-file-area {
        width: 530px;
        margin: 120px auto 100px;
        /deep/.file-wrapper {
            background: #fafbfd;
        }
    }
    .import-check-wrapper {
        padding: 0 24px;
        height: 480px;
        overflow-y: auto;
        @include scrollbar;
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
    .tpl-type-title {
        margin: 12px 0 8px;
        font-size: 12px;
        color: #313238;
    }
    .tpl-overrider-select {
        display: flex;
        align-items: center;
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
    .tpl-popover {
        .bk-option {
            white-space: nowrap;
        }
        .bk-spin-title {
            font-size: 12px;
        }
    }
</style>
