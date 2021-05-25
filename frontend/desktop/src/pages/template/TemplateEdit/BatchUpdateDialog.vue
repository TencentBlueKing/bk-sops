<template>
    <bk-dialog
        class="batch-update-dialog"
        v-model="isShow"
        :close-icon="false"
        :fullscreen="true">
        <div slot="header" class="header-wrapper">
            <h4>批量更新子流程{{ $t('（') + expiredTplNum + $t('）') }}</h4>
            <div class="legend-area">
                <span class="legend-item delete">删除</span>
                <span class="legend-item add">新增</span>
            </div>
            <i class="bk-dialog-close bk-icon icon-close" @click="onCloseDialog"></i>
        </div>
        <div class="subflow-form-wrap" v-bkloading="{ isLoading: subflowFormsLoading, opacity: 1 }">
            <section
                v-for="subflow in subflowForms"
                :key="subflow.id"
                class="subflow-item">
                <div class="header-area" @click.self="subflow.fold = !subflow.fold">
                    <bk-checkbox v-model="subflow.checked"></bk-checkbox>
                    <h3>{{ subflow.name }}</h3>
                    <i :class="['bk-icon', 'icon-angle-up', 'fold-icon', subflow.fold ? 'fold' : '']" @click="subflow.fold = !subflow.fold"></i>
                </div>
                <div v-show="!subflow.fold" class="form-area">
                    <!-- 当前版本表单 -->
                    <div class="current-form">
                        <div class="version-tag">{{ $t('原版本') }}</div>
                        <!-- 输入参数 -->
                        <section class="config-section">
                            <h4>{{$t('输入参数')}}</h4>
                            <div class="inputs-wrapper">
                                <input-params
                                    v-if="subflow.currentForm.inputsConfig.length > 0"
                                    ref="inputParams"
                                    :is-subflow="true"
                                    :node-id="subflow.id"
                                    :scheme="subflow.currentForm.inputsConfig"
                                    :version="subflow.currentForm.version"
                                    :subflow-forms="subflow.currentForm.form"
                                    :value="subflow.currentForm.inputsValue"
                                    :constants="localConstants">
                                </input-params>
                                <no-data v-else></no-data>
                            </div>
                        </section>
                        <!-- 输出参数 -->
                        <section class="config-section">
                            <h4>{{$t('输出参数')}}</h4>
                            <div class="outputs-wrapper">
                                <output-params
                                    v-if="subflow.currentForm.outputs.length > 0"
                                    :constants="localConstants"
                                    :params="subflow.currentForm.outputs"
                                    :version="subflow.currentForm.version"
                                    :node-id="subflow.id">
                                </output-params>
                                <no-data v-else></no-data>
                            </div>
                        </section>
                    </div>
                    <!-- 新版本表单 -->
                    <div class="latest-form">
                        <div class="version-tag lastest">{{ $t('待更新版本') }}</div>
                        <!-- 输入参数 -->
                        <section class="config-section">
                            <h4>{{$t('输入参数')}}</h4>
                            <div class="inputs-wrapper">
                                <input-params
                                    v-if="subflow.latestForm.inputsConfig.length > 0"
                                    ref="inputParams"
                                    :is-subflow="true"
                                    :node-id="subflow.id"
                                    :scheme="subflow.latestForm.inputsConfig"
                                    :version="subflow.latestForm.version"
                                    :subflow-forms="subflow.latestForm.form"
                                    :value="subflow.latestForm.inputsValue"
                                    :constants="localConstants"
                                    @hookChange="onHookChange"
                                    @update="updateInputsValue">
                                </input-params>
                                <no-data v-else></no-data>
                            </div>
                        </section>
                        <!-- 输出参数 -->
                        <section class="config-section">
                            <h4>{{$t('输出参数')}}</h4>
                            <div class="outputs-wrapper">
                                <output-params
                                    v-if="subflow.latestForm.outputs.length"
                                    :constants="localConstants"
                                    :params="subflow.latestForm.outputs"
                                    :version="subflow.latestForm.version"
                                    :node-id="subflow.id"
                                    @hookChange="onHookChange">
                                </output-params>
                                <no-data v-else></no-data>
                            </div>
                        </section>
                    </div>
                </div>
            </section>
        </div>
        <div slot="footer" class="footer-wrapper">
            <bk-checkbox
                class="selecte-all"
                :indeterminate="selectedTplNum > 0 && selectedTplNum < expiredTplNum"
                :value="selectedTplNum > 0 && selectedTplNum === expiredTplNum"
                @change="onSelectedAllChange">
                {{ $t('全选') }}
            </bk-checkbox>
            <div class="action-btns">
                <span v-if="selectedTplNum > 0" class="selected-tips">{{ $t('已选择') + selectedTplNum + $t('个') + $t('待更新的子流程') }}</span>
                <bk-button theme="primary" style="margin-right: 8px;" @click="onConfirm">{{ $t('批量更新') }}</bk-button>
                <bk-button @click="onCloseDialog">{{ $t('取消') }}</bk-button>
            </div>
        </div>
    </bk-dialog>
</template>
<script>
    import { mapState, mapActions } from 'vuex'
    import atomFilter from './utils/atomFilter.js'
    import InputParams from './NodeConfig/InputParams.vue'
    import OutputParams from './NodeConfig/OutputParams.vue'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'BatchUpdateDialog',
        components: {
            InputParams,
            OutputParams,
            NoData
        },
        props: {
            show: {
                type: Boolean,
                default: false
            },
            projectId: Number,
            list: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                isShow: this.show,
                subflowFormsLoading: false,
                subflowForms: [],
                localConstants: {} // 全局变量列表，用来维护当前面板勾选、反勾选后全局变量的变化情况，保存时更新到 store
            }
        },
        computed: {
            ...mapState({
                'activities': state => state.template.activities,
                'constants': state => state.template.constants,
                'systemConstants': state => state.template.systemConstants
            }),
            expiredTplNum () {
                return this.list.filter(item => item.expired).length
            },
            selectedTplNum () {
                return this.subflowForms.filter(item => item.checked).length
            }
        },
        watch: {
            show (val) {
                this.isShow = val
                this.loadSubflowForms()
            }
        },
        methods: {
            ...mapActions('template', [
                'getBatchForms'
            ]),
            // 批量加载待更新流程模版当前版本和最新版本表单数据
            async loadSubflowForms () {
                try {
                    this.subflowFormsLoading = true
                    const tpls = []
                    this.list.map(item => {
                        if (item.expired) {
                            tpls.push({
                                id: item.template_id,
                                nodeId: item.subprocess_node_id,
                                version: item.version
                            })
                        }
                    })
                    const res = await this.getBatchForms({ tpls, projectId: this.projectId })
                    const subflowForms = []
                    tpls.forEach(tpl => {
                        const activity = this.activities[tpl.nodeId]
                        const { name, id, template_id } = activity
                        let latestForm = {}
                        let currentForm = {}
                        res.data[tpl.id].forEach(item => {
                            const { form, outputs, version } = item
                            let inputForms = {}
                            for (let key in form) { // 去掉隐藏变量
                                const item = form[key]
                                if (item.show_type === 'show') {
                                    inputForms[key] = item
                                }
                            }
                            const outputParams = Object.keys(outputs).map(item => { // 输出参数
                                const output = outputs[item]
                                return {
                                    name: output.name,
                                    key: output.key,
                                    version: output.hasOwnProperty('version') ? output.version : 'legacy'
                                }
                            })
                            const data = {
                                form: inputForms,
                                outputs: outputParams,
                                inputsConfig: [],
                                inputsValue: [],
                                version
                            }
                            if (item.is_current) { // 最新版本子流程表单数据
                                latestForm = data
                            } else {
                                currentForm = data
                            }
                            for (let key in latestForm.forms) { // 标记最新版本子流程输入参数表单项是否为新增
                                const latestFormItem = latestForm.forms[key]
                                if (!currentForm.forms.hasOwnProperty(key)) {
                                    latestFormItem.status = 'added'
                                }
                            }
                            for (let key in currentForm.forms) { // 标记当前版本子流程输入参数表单项是否被删除
                                const currentFormItem = currentForm.forms[key]
                                if (!latestFormItem.forms.hasOwnProperty(key)) {
                                    currentFormItem.status = 'deleted'
                                }
                            }
                        })
                        subflowForms.push({
                            name,
                            id,
                            template_id,
                            latestForm,
                            currentForm,
                            loading: false, // 输入参数表单是否在加载中
                            checked: false, // 是否选中更新
                            fold: false // 是否收起
                        })
                    })
                    this.subflowForms = subflowForms
                    this.getTplsFormConfig(subflowForms)
                } catch (e) {
                    console.error(e)
                } finally {
                    this.subflowFormsLoading = false
                }
            },
            // 加载当前版本和待更新版本流程的输入参数表单配置项
            async getTplsFormConfig (subflowForms) {
                const loadedConfigMap = {}
                const allSubflowInputForms = []
                subflowForms.forEach(subflow => {
                    const latestFormArr = Object.keys(subflow.latestForm.form).map(key => subflow.latestForm.form[key]).sort((a, b) => a.index - b.index)
                    const currentFormArr = Object.keys(subflow.currentForm.form).map(key => subflow.latestForm.form[key]).sort((a, b) => a.index - b.index)
                    allSubflowInputForms.push({
                        latestFormArr,
                        currentFormArr
                    })
                })

            },
            async loadConfig () {

            },
            onSelectedAllChange (val) {
                this.subflowForms.forEach(item => {
                    item.checked = val
                })
            },
            onHookChange () {},
            updateInputsValue () {},
            onConfirm () {
                this.$emit('batchUpdate')
            },
            onCloseDialog () {
                this.$emit('update:show', false)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .header-wrapper {
        position: relative;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 80px 0 26px;
        height: 54px;
        line-height: 1;
        border-bottom: 1px solid #dcdee5;
        background: #ffffff;
        z-index: 1;
        & > h4 {
            margin: 0;
            font-weight: normal;
            font-size: 14px;
            color: #313238;
        }
        .legend-item {
            position: relative;
            display: inline-block;
            margin-left: 18px;
            padding-left: 20px;
            font-size: 14px;
            color: #63656e;
            line-height: 1;
            &:before {
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 3px;
            }
            &.delete:before {
                border: 1px solid rgba(251,133,121,0.16);
                background: #ffeeed;
            }
            &.add:before {
                border: 1px solid rgba(76,164,90,0.22);
                background: #e5ffe9;
            }
        }
        .bk-dialog-close {
            position: absolute;
            right: 20px;
            top: 16px;
            width: 26px;
            height: 26px;
            line-height: 26px;
            text-align: center;
            border-radius: 50%;
            font-size: 24px;
            font-weight: bold;
            color: #979ba5;
            cursor: pointer;
            &:hover {
                background-color: #f0f1f5;
            }
        }
    }
    .subflow-form-wrap {
        min-height: 100%;
    }
    .subflow-item {
        border-bottom: 1px solid #ffffff;
        .header-area {
            position: relative;
            display: flex;
            align-items: center;
            padding: 14px 24px 14px 30px;
            background: #f4f4f4;
            cursor: pointer;
            & > h3 {
                margin: 0 0 0 8px;
                font-size: 14px;
                font-weight: bold;
            }
            .fold-icon {
                position: absolute;
                right: 20px;
                top: 12px;
                font-size: 24px;
                &.fold {
                    transform: rotate(180deg);
                }
            }
        }
        .form-area {
            display: flex;
            justify-content: space-between;
            overflow: hidden;
            .current-form,
            .latest-form {
                position: relative;
                width: 50%;
                padding-bottom: 38px;
                .config-section {
                    & > h4 {
                        margin: 26px 30px 20px;
                        padding-bottom: 10px;
                        color: #313238;
                        font-size: 14px;
                        font-weight: normal;
                        border-bottom: 1px solid #cacedb;
                    }
                }
                .version-tag {
                    position: absolute;
                    left: 0;
                    top: 0;
                    padding: 4px 7px;
                    font-size: 12px;
                    line-height: 1;
                    color: #ffffff;
                    background: #a8a8a8;
                    &:after {
                        content: '';
                        position: absolute;
                        top: 0;
                        right: -6px;
                        width: 0;
                        height: 0;
                        border-style: solid;
                        border-width: 20px 6px 0 0;
                        border-color: #a8a8a8 transparent transparent transparent;
                    }
                    &.lastest {
                        background: #1aaf41;
                        &:after {
                            border-color: #1aaf41 transparent transparent transparent;
                        }
                    }
                }
            }
            .current-form {
                background: #fcfcfc;
                .no-data-wrapper {
                    background: #fcfcfc;
                }
            }
        }
    }
    .selecte-all {
        position: absolute;
        bottom: 16px;
        left: 30px;
    }
    .action-btns {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        .selected-tips {
            margin-right: 12px;
            font-size: 14px;
            color: #313238;
        }
    }
</style>
<style lang="scss">
    .batch-update-dialog {
        .bk-dialog-tool {
            display: none;
        }
        .bk-dialog-header {
            padding: 0;
        }
        .bk-dialog-body {
            padding: 0;
        }
    }
</style>
