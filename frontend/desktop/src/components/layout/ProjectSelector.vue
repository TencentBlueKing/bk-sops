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
    <div
        :class="[
            'project-wrapper',
            { 'disabled': disabled },
            { 'read-only': readOnly }
        ]">
        <div v-if="readOnly" :title="projectName" class="project-name">
            {{ projectName }}
        </div>
        <bk-select
            v-else
            ref="projectSelect"
            :key="randomKey"
            class="project-select"
            ext-popover-cls="project-select-comp-list"
            v-model="crtProject"
            :disabled="disabled"
            :search-with-pinyin="true"
            :clearable="false"
            :searchable="true"
            :remote-method="onProjectSearch"
            @toggle="onProjectSelectToggle"
            @selected="onProjectChange">
            <bk-option
                class="project-item"
                v-for="option in renderList"
                :class="{
                    'is-disabled': !option.is_user_project,
                    'is-hover': option.id === hoverId
                }"
                v-cursor="{ active: !option.is_user_project }"
                :key="option.id"
                :id="option.id"
                :name="`${option.name}`">
                <div class="project-content-wrapper">
                    <div class="content-wrap">
                        <span class="name" v-html="option.matchName || option.name"></span>
                        <span class="id">
                            (<span v-html="option.matchBizId || option.bk_biz_id"></span>)
                        </span>
                    </div>
                    <div
                        v-bk-tooltips="{
                            content: favorCount >= 9 ? $t('最多只能收藏 9 个') : option.is_fav ? $t('取消收藏') : $t('添加收藏')
                        }"
                        :class="[
                            'project-favor',
                            option.is_fav ? 'common-icon-favorite' : 'common-icon-rate',
                            { 'favor-disable': favorCount >= 9 && !option.is_fav }
                        ]"
                        @click.stop="handleFavorToggle(option)">
                    </div>
                </div>
            </bk-option>
            <div slot="extension" @click="jumpToOther">
                <i class="bk-icon icon-plus-circle"></i>
                {{ $t('申请业务权限') }}
            </div>
        </bk-select>
    </div>
</template>
<script>
    import { mapState, mapActions } from 'vuex'
    import openOtherApp from '@/utils/openOtherApp.js'
    import bus from '@/utils/bus.js'
    import permission from '@/mixins/permission.js'
    import tools from '@/utils/tools.js'
    import pinyin from 'bk-magic-vue/lib/utils/pinyin'
    import compare from '@/utils/projectSelectSort.js'

    export default {
        name: 'ProjectSelector',
        mixins: [permission],
        props: {
            readOnly: {
                type: Boolean,
                default: false
            },
            disabled: {
                type: Boolean,
                default: false
            }
        },
        data () {
            const id = Number(this.$store.state.project.project_id)
            return {
                crtProject: isNaN(id) ? '' : id,
                showList: false,
                searchStr: '',
                randomKey: null,
                projectList: [],
                renderList: [],
                hoverId: ''
            }
        },
        computed: {
            ...mapState('project', {
                userProjectList: state => state.userProjectList,
                project_id: state => state.project_id,
                projectName: state => state.projectName
            }),
            favorCount () {
                return this.projectList.filter(item => item.is_fav).length
            }
        },
        watch: {
            '$route' (val) {
                this.updateSelected()
            },
            userProjectList: {
                handler (val) {
                    const list = val.map(item => {
                        return {
                            ...item,
                            ...this.getTransformInfo(item.name)
                        }
                    })
                    this.projectList = this.sortProjectList(list)
                    this.renderList = Object.freeze([
                        ...this.projectList
                    ])
                },
                immediate: true
            }
        },
        created () {
            bus.$on('cancelRoute', (val) => {
                this.updateSelected()
            })
            this.onProjectSearch = tools.debounce(this.handleProjectSearch, 500)
        },
        methods: {
            ...mapActions([
                'setProjectFavor',
                'deleteProjectFavor'
            ]),
            ...mapActions('project', [
                'loadUserProjectList'
            ]),
            
            getTransformInfo (text) {
                const sentence = []
                const head = []
                let word = []
                const parseArr = pinyin.parse(text)
                parseArr.forEach((target) => {
                    if (target.type === 2) {
                        if (word.length > 0) {
                            head.push(word[0])
                            sentence.push(word.join(''))
                            word = []
                        }
                        head.push(target.target[0])
                        sentence.push(target.target)
                    } else {
                        word.push(target.target)
                    }
                })
                if (word.length > 0) {
                    head.push(word[0])
                    sentence.push(word.join(''))
                }
                return {
                    sentence: sentence.join(''),
                    head: head.join('')
                }
            },
            sortProjectList (list) {
                const favorList = []
                const unFavorList = []
                const unPermission = []

                list.forEach((item) => {
                    if (item.is_fav) {
                        favorList.push(item)
                    } else if (!item.is_user_project) {
                        unPermission.push(item)
                    } else {
                        unFavorList.push(item)
                    }
                })
                // 按符号 => 数字 => 英文 => 中文 排序
                favorList.sort((a, b) => compare(a.name, b.name, true))
                unFavorList.sort((a, b) => compare(a.name, b.name, true))
                unPermission.sort((a, b) => compare(a.name, b.name, true))

                return [
                    ...favorList,
                    ...unFavorList,
                    ...unPermission
                ]
            },
            updateSelected () {
                let { project_id: projectId } = this.$route.params
                projectId = Number(projectId)
                const { selected } = this.$refs.projectSelect || {}
                if (selected && Number(projectId) !== selected) {
                    this.crtProject = projectId
                    this.randomKey = new Date().getTime()
                }
            },
            async onProjectChange (id) {
                const project = this.projectList.find(item => item.id === id)
                if (!project.is_user_project) {
                    const resourceData = {
                        project: [{
                            id: project.id,
                            name: project.name
                        }]
                    }
                    this.applyForPermission(['project_view'], project.auth_actions, resourceData)
                    this.crtProject = Number(this.$store.state.project.project_id)
                    return false
                }
                if (this.project_id === id) {
                    return false
                }
                const redirectMap = {
                    '/template': {
                        name: 'processHome',
                        params: { project_id: id }
                    },
                    '/taskflow': {
                        name: 'taskList',
                        params: { project_id: id }
                    },
                    '/appmaker': {
                        name: 'appMakerList',
                        params: { project_id: id }
                    }
                }
                const key = Object.keys(redirectMap).find(path => this.$route.path.indexOf(path) === 0)
                if (key && this.$route.name !== redirectMap[key].name && !['periodicTemplate', 'clockedTemplate'].includes(this.$route.name)) {
                    this.$router.push(redirectMap[key])
                } else {
                    this.$router.push({
                        name: this.$route.name,
                        params: { project_id: id }
                    })
                    this.$nextTick(() => {
                        this.$emit('reloadHome')
                    })
                }
            },
            // 这里统一直接用后端提供的 host 跳转
            jumpToOther () {
                openOtherApp(window.BK_IAM_APP_CODE, window.BK_IAM_APPLY_URL)
            },
            async handleFavorToggle (option) {
                try {
                    const { is_fav, id } = option
                    const project = this.projectList.find(item => item.id === id)
                    // 最多只能收藏9个
                    if (!is_fav && this.favorCount >= 9) return
                    const resp = is_fav ? await this.deleteProjectFavor({ id }) : await this.setProjectFavor({ id })
                    if (resp.result) {
                        project.is_fav = !project.is_fav
                        this.renderList = Object.freeze([
                            ...this.renderList
                        ])
                        this.$bkMessage({
                            message: is_fav ? this.$t('取消收藏成功！') : this.$t('添加收藏成功！'),
                            theme: 'success'
                        })
                    }
                } catch (error) {
                    console.warn(error)
                }
            },
            handleProjectSearch (val) {
                const query = val.trim()
                let renderList = []

                if (!query) {
                    renderList = Object.freeze(this.projectList)
                } else {
                    const rule = new RegExp(this.encodeRegexp(query), 'i')
                    const replaceText = `<span style="color: #3a84ff">${query}</span>`
                    renderList = this.projectList.reduce((acc, cur) => {
                        const match = {}

                        if (/[\u4e00-\u9fa5]/.test(query)) {
                            // 有中文精确匹配
                            if (rule.test(cur.name)) {
                                const matchName = cur.name.replace(query, replaceText)
                                match.matchName = matchName
                            }
                        } else {
                            if (rule.test(cur.head) || rule.test(cur.sentence) || rule.test(cur.bk_biz_id)) {
                                if (rule.test(cur.bk_biz_id)) {
                                    const matchBizId = String(cur.bk_biz_id).replace(query, replaceText)
                                    match.matchBizId = matchBizId
                                } else {
                                    const matchName = cur.name.replace(query, replaceText)
                                    match.matchName = matchName
                                }
                            }
                        }

                        if (Object.keys(match).length > 0) {
                            acc.push({
                                ...cur,
                                ...match
                            })
                        }

                        return acc
                    }, [])
                }

                this.renderList = Object.freeze(renderList)
            },
            encodeRegexp (paramStr) {
                const regexpKeyword = [
                    '\\', '.', '*', '-', '{', '}', '[', ']', '^', '(', ')', '$', '+', '?', '|'
                ]
                return regexpKeyword.reduce(
                    (result, charItem) => result.replace(new RegExp(`\\${charItem}`, 'g'), `\\${charItem}`),
                    paramStr
                )
            },
            onProjectSelectToggle (val) {
                if (val) {
                    // window.addEventListener('keydown', this.handleDocumentKeydown)
                } else {
                    this.hoverId = ''
                    this.loadUserProjectList({
                        params: { is_disable: false }
                    })
                    // window.removeEventListener('keydown', this.handleDocumentKeydown)
                }
            },
            handleDocumentKeydown (event) {
                switch (event.code) {
                    case 'Enter':
                    case 'NumpadEnter':
                        event.preventDefault()
                        this.onProjectChange(this.hoverId)
                        break
                    case 'ArrowDown':
                    case 'ArrowUp':
                        event.preventDefault()
                        const len = this.renderList.length
                        if (!len) return
                        event.stopPropagation()
                        let curIndex = this.renderList.findIndex(item => item.id === this.hoverId)
                        curIndex = event.code === 'ArrowDown' ? curIndex + 1 : curIndex - 1
                        curIndex = curIndex > len - 1 ? 0 : (curIndex < 0 ? len - 1 : curIndex)
                        const option = this.renderList[curIndex]
                        if (option) {
                            this.hoverId = option.id
                            const selectDom = document.querySelector('.project-select-comp-list .bk-options')
                            const hoverItemDom = selectDom && selectDom.querySelector('.is-hover')
                            if (hoverItemDom) {
                                selectDom.scrollTo({
                                    top: 32 * (curIndex < 9 ? 0 : curIndex - 8)
                                })
                            }
                        }
                        break
                    default:
                        return false
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    .project-wrapper {
        position: relative;
        margin-right: 18px;
        width: 320px !important;
        font-size: 14px;
        color: #979ba5;
        background: #fff;
        &.disabled {
            background: #252f43;
        }
        &.read-only {
            margin-top: 0;
            width: auto;
            height: 50px;
            line-height: 50px;
            .project-name {
                width: 100%;
                color: #979ba5;
                font-size: 14px;
                text-align: right;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
            }
        }
    }
    .local-loading {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        text-align: center;
        cursor: not-allowed;
        .common-icon-loading-ring {
            display: inline-block;
            font-size: 34px;
            animation: loading 1.4s infinite linear;
        }
    }
    @keyframes loading {
        from {
            transform: rotate(0);
        }
        to {
            transform: rotate(360deg);
        }
    }
</style>
<style lang="scss">
    .project-select-comp-list {
        .bk-options-wrapper,
        .bk-options {
            max-height: 294px !important;
        }
        .project-item {
            .bk-option-content {
                padding: 0 12px;
                .project-content-wrapper {
                    display: flex;
                    align-items: center;
                    width: 100%;
                }
                .content-wrap {
                    display: flex;
                    overflow: hidden;
                    .name {
                        flex: 1;
                        color: #63656e;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                    }
                    .id {
                        flex-shrink: 0;
                        color: #c4c4c4;
                        margin-left: 4px;
                    }
                }
                .project-favor {
                    opacity: 0;
                    font-size: 16px;
                    color: #979ba5;
                    margin-left: auto;
                    padding-left: 5px !important;
                    &:hover {
                        color: #313238;
                    }
                    &.common-icon-favorite {
                        opacity: 1;
                        color: #ff9c01;
                        &:hover {
                            color: #ffb848;
                        }
                    }
                    &.favor-disable {
                        color: #dcdee5;
                        cursor: not-allowed;
                    }
                }
            }
            &.is-hover,
            &:hover {
                color: inherit !important;
                background: #f5f7fa !important;
                .name {
                    color: inherit;
                }
                .project-favor {
                    opacity: 1;
                }
            }
            &.is-selected {
                background: #e1ecff !important;
                .name {
                    color: #3a84ff !important;
                }
            }
            &.is-disabled {
                color: #c4c4c4 !important;
                .project-favor {
                    display: none;
                }
            }
        }
        .bk-select-extension {
            text-align: center;
            cursor: pointer;
            padding: 0;
            .project-create {
                display: flex;
                .project {
                    flex: 1;
                }
            }
        }
    }
</style>
