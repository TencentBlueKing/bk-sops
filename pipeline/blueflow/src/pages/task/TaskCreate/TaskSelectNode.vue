/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="select-node-wrapper" v-bkloading="{isLoading: loading, opacity: 1}">
        <div class="canvas-content">
            <div :class="['node-select-scheme', {'actived': showPanel}]" v-if="isSchemeShow && viewMode !== 'appmaker'">
                <div class="toggle-button" @click="togglePanel">
                    <i :class="['common-icon-arrow-left', {'arrow-right': showPanel}]"></i>
                </div>
                <div class="scheme-header">
                    <h3>{{ i18n.schema_list }}</h3>
                    <bk-button type="primary" class="save-scheme-btn" @click="onShowSchemeDialog">{{ i18n.new_schema }}</bk-button>
                </div>
                <ul class="schemeList">
                    <li
                        v-for="item in taskScheme"
                        :class="{
                            'scheme-item': true,
                            'selected': item.id === selectedScheme
                        }"
                        :key="item.id"
                        @click="onSelectScheme(item.id)">
                        <a class="scheme-name" :title="item.name">{{item.name}}</a>
                        <i class="common-icon-close" @click.stop="onDeleteScheme(item.id)"></i>
                    </li>
                </ul>
            </div>
            <div class="quick-select" v-if="isSchemeShow && viewMode !== 'appmaker'">
                <bk-button @click="onSelectAllNode">{{ i18n.all }}</bk-button>
                <bk-button @click="onSelectNoneNode">{{ i18n.cancel }}</bk-button>
            </div>
            <pipelineCanvas
                v-if="!loading"
                ref="pipelineCanvas"
                :isMenuBarShow="false"
                :isConfigBarShow="false"
                :isEdit="false"
                :canvasData="canvasData">
            </pipelineCanvas>
        </div>
        <div class="action-wrapper" slot="action-wrapper">
            <bk-button
                type="primary"
                @click="onGotoParamFill">
                {{ i18n.next }}
            </bk-button>
        </div>
        <bk-dialog
            :is-show.sync="showDialog"
            :quick-close="false"
            :ext-cls="'common-dialog'"
            :title="i18n.save"
            width="600"
            @confirm="onConfirm"
            @cancel="onCancel">
            <div slot="content">
                <div v-if="showDialog" class="scheme-name-wrapper">
                    <label>{{ i18n.schema_name }}</label>
                    <div class="scheme-name-input">
                        <BaseInput
                            name="schemeName"
                            v-model="schemeName"
                            v-validate="schemeNameRule">
                        </BaseInput>
                        <span v-if="errors.has('schemeName')" class="common-error-tip error-msg">{{ errors.first('schemeName') }}</span>
                    </div>
                </div>
            </div>
        </bk-dialog>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapMutations, mapActions } from 'vuex'
import { errorHandler } from '@/utils/errorHandler.js'
import { NAME_REG } from '@/constants/index.js'
import PipelineCanvas from '@/components/common/PipelineCanvas/index.vue'
import BaseInput from '@/components/common/base/BaseInput.vue'
export default {
    name: 'TaskSelectNode',
    components: {
        PipelineCanvas,
        BaseInput
    },
    props: ['cc_id', 'template_id', 'excludeNode'],
    data () {
        return {
            i18n: {
                schema_list: gettext("执行方案列表"),
                new_schema: gettext("新建方案"),
                all: gettext("全选"),
                cancel: gettext("取消全选"),
                next: gettext("下一步"),
                save: gettext("执行方案保存"),
                schema_name: gettext("方案名称")
            },
            loading: true,
            bkMessageInstance: null,
            isSubmit: false,
            isDelete: false,
            showPanel: true,
            showDialog: false,
            selectedNodes: [],
            selectedScheme: '',
            schemeName: '',
            schemeNameRule: {
                required: true,
                max: 30,
                regex: NAME_REG
            }
        }
    },
    computed: {
        ...mapState({
            'activities': state => state.template.activities,
            'locations': state => state.template.location,
            'lines': state => state.template.line,
            'constants': state => state.template.constants,
            'gateways': state => state.template.gateways,
            'taskScheme': state => state.task.taskScheme,
            'app_id': state => state.app_id,
            'viewMode': state => state.view_mode
        }),
        canvasData () {
            const branchConditions = {}
            let mode
            for (let gKey in this.gateways) {
                const item = this.gateways[gKey]
                if (item.conditions) {
                    branchConditions[item.id] = Object.assign({}, item.conditions)
                }
            }
            if (this.viewMode === 'appmaker') {
                mode = 'selectDisabled'
            } else {
                mode = 'select'
            }
            return {
                lines: this.lines,
                locations: this.locations.map(item => {return {...item, mode, checked: true}}),
                branchConditions
            }
        },
        isSchemeShow () {
            return this.locations.some(item => item.optional)
        }
    },
    mounted () {
        this.getTemplateData()
    },
    methods: {
        ...mapActions('template/', [
            'loadTemplateData',
            'saveTemplateData'
        ]),
        ...mapActions('task/', [
            'loadTaskScheme',
            'createTaskScheme',
            'deleteTaskScheme',
            'getSchemeDetail'
        ]),
        ...mapActions('appmaker/', [
            'loadAppmakerDetail'
        ]),
        ...mapMutations('template/', [
            'setTemplateData'
        ]),
        ...mapMutations('task/', [
            'setTaskScheme'
        ]),
        async getTemplateData () {
            this.loading = true
            try {
                const templateData = await this.loadTemplateData(this.template_id)
                const schemeData = await this.loadTaskScheme({'cc_id': this.cc_id, 'template_id': this.template_id})
                if (this.viewMode === 'appmaker') {
                    const appmakerData = await this.loadAppmakerDetail(this.app_id)
                    const schemeId = Number(appmakerData.template_scheme_id)
                    schemeId && this.onSelectScheme(schemeId)
                }
                this.setTaskScheme(schemeData)
                this.setTemplateData(templateData)
                const selectedNodes = []
                this.locations.forEach(item => {
                    if (
                        (item.type === 'tasknode' || item.type === 'subflow') &&
                        this.excludeNode.indexOf(item.id) === -1
                    ) {
                        selectedNodes.push(item.id)
                    }
                })
                this.selectedNodes = selectedNodes
                this.updateSelectedLocation()
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.loading = false
            }
        },
        togglePanel () {
            this.showPanel = !this.showPanel
        },
        onShowSchemeDialog () {
            this.showDialog = true
        },
        getExcludeNode () {
            const canvasEl = this.$refs.pipelineCanvas.$el
            const optionalNode = canvasEl.querySelectorAll('.node-checkbox input[type="checkbox"]')
            const nodeId = []
            Array.prototype.forEach.call(optionalNode, function (item) {
                if (!item.checked) {
                    nodeId.push(item.dataset.id)
                }
            })
            return nodeId
        },
        onConfirm () {
            if (this.isSubmit) return
            const isSchemeNameExist = this.taskScheme.some(item => item.name === this.schemeName)
            if (isSchemeNameExist) {
                errorHandler({message: gettext('方案名称已存在')}, this)
                return
            }
            this.isSubmit = true
            this.$validator.validateAll().then(async (result) => {
                if (!result) {
                    this.isSubmit = false
                    return
                }
                this.showDialog = false
                const excludeNode = this.getExcludeNode()
                let selectedNodes = []
                this.canvasData.locations.forEach(item => {
                    if (item.type === 'tasknode' || item.type === 'subflow') {
                        if (excludeNode.indexOf(item.id) === -1) {
                            selectedNodes.push(item.id)
                        }
                    }
                })
                this.selectedNodes = selectedNodes
                const scheme = {
                    cc_id: this.cc_id,
                    template_id: this.template_id,
                    name: this.schemeName,
                    data: JSON.stringify(selectedNodes)
                }
                try {
                    const newScheme = await this.createTaskScheme(scheme)
                    const schemeData = await this.loadTaskScheme({'cc_id': this.cc_id, 'template_id': this.template_id})
                    this.setTaskScheme(schemeData)
                    this.selectedScheme = newScheme.id
                    this.schemeName = ''
                    this.$bkMessage({
                        message: gettext("方案添加成功"),
                        theme: 'success'
                    })
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.isSubmit = false
                }
            })
        },
        onCancel () {
            this.showDialog = false
            this.schemeName = ''
        },
        updateSelectedLocation () {
            const pipelineCanvas = this.$refs.pipelineCanvas
            this.canvasData.locations.forEach((item) => {
                if (item.type === 'tasknode' || item.type === 'subflow') {
                    const checkState = this.selectedNodes.indexOf(item.id) > -1
                    this.$set(item, 'checked', checkState)
                    pipelineCanvas && pipelineCanvas.onUpdateNodeInfo(item.id, item)
                }
            })
        },
        async onSelectScheme (id) {
            this.selectedScheme = id
            try {
                const data = await this.getSchemeDetail(id)
                this.selectedNodes = JSON.parse(data.data)
                this.updateSelectedLocation()
            } catch (e) {
                errorHandler(e, this)
            }
        },
        async onDeleteScheme (id) {
            if (this.isDelete) return
            this.isDelete = true
            try {
                await this.deleteTaskScheme(id)
                const schemeData = await this.loadTaskScheme({'cc_id': this.cc_id, 'template_id': this.template_id})
                this.setTaskScheme(schemeData)
                this.$bkMessage({
                    message: gettext("方案删除成功"),
                    theme: 'success'
                })
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.isDelete = false
            }
        },
        onSelectAllNode () {
            const list = []
            this.canvasData.locations.forEach(item => {
                if (item.type === 'tasknode' || item.type === 'subflow') {
                    item.checked = true
                    list.push(item.id)
                }
            })
            this.selectedNodes = list
            this.updateSelectedLocation()
        },
        onSelectNoneNode () {
            this.canvasData.locations.forEach(item => {
                if (item.type === 'tasknode' || item.type === 'subflow') {
                    item.checked = false
                }
            })
            this.selectedNodes = []
            this.updateSelectedLocation()
        },
        onGotoParamFill () {
            const excludeNode = this.getExcludeNode()
            this.$emit('setExcludeNode', excludeNode)
            if (this.viewMode === 'appmaker') {
                this.$router.push({path: `/appmaker/${this.app_id}/newtask/${this.cc_id}/paramfill/`, query: {'template_id': this.template_id}})
            } else {
                this.$router.push({path: `/template/newtask/${this.cc_id}/paramfill/`, query: {template_id: this.template_id}})
            }
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
@import '@/scss/config.scss';
.select-node-wrapper {
    height: calc(100% - 62px);
}
.canvas-content {
    position: relative;
    height: calc(100% -90px);
    border-bottom: 1px solid $commonBorderColor;
    overflow: hidden;
    /deep/ .node-canvas {
        width: 100%;
        height: 100%;
        background: $whiteDefault;
    }
}
.node-select-scheme {
    position: absolute;
    top: 0;
    right: -300px;
    width: 300px;
    height: 100%;
    background: $whiteDefault;
    border-left: 1px solid $commonBorderColor;
    box-shadow: 0 0 8px rgba(0, 0, 0, 0.15);
    z-index: 4;
    transition: right 0.5s ease-in-out;
    &.actived {
        right: 0;
    }
}
.quick-select {
    position: absolute;
    top: 15px;
    left: 10px;
    z-index: 5;
}
.toggle-button {
    position: absolute;
    top: 0;
    left: -20px;
    width: 20px;
    height: 50px;
    line-height: 50px;
    color: $whiteDefault;
    background: $blueThinBg;
    text-align: center;
    cursor: pointer;
    &:hover {
        background: $blueDefault;
    }
    .common-icon-arrow-left {
        display: inline-block;
        &.arrow-right {
            transform: rotate(180deg);
        }
    }
}
.scheme-header {
    position: relative;
    background: $commonBgColor;
    border-bottom: 1px solid $commonBorderColor;
    h3 {
        margin: 0;
        padding: 0 20px;
        height: 60px;
        line-height: 60px;
        font-size: 14px;
    }
    .save-scheme-btn {
        position: absolute;
        top: 12px;
        right: 20px;
    }
}
.schemeList {
    height: calc(100% - 62px);
    overflow-y: auto;
    @include scrollbar;
}
.scheme-item {
    padding: 0 20px;
    height: 40px;
    line-height: 40px;
    font-size: 14px;
    border-bottom: 1px solid $commonBorderColor;
    cursor: pointer;
    &:hover {
        background: $blueStatus;
    }
    &.selected {
        color: $whiteDefault;
        background: $blueDefault;
    }
    .scheme-name {
        display: inline-block;
        width: 240px;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
    }
    .common-icon-close {
        float: right;
        margin-top: 15px;
        font-size: 12px;
        cursor: pointer;
        &:hover {
            color: $redDark;
        }
    }
}
.scheme-name-wrapper {
    padding: 10px 0;
    label {
        float: left;
        margin-top: 6px;
        width: 100px;
        text-align: right;
    }
    .scheme-name-input {
        margin-left: 120px;
    }
}
</style>

