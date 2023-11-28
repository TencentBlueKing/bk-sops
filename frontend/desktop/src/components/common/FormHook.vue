<template>
    <div class="form-hook" :class="{ 'hook-mode': hook, 'disable-mode': !option.formEdit }" v-show="showHook">
        <!-- 表单勾选为全局变量 -->
        <div v-if="hook" :class="['tag-hooked-form-content', { 'active': varPanelActivated && isHooking }]">
            <span>{{ value }}</span>
            <i v-if="variableSourceCount > 1" class="common-icon-enter-config" @click="handleVariableHook('reselect')"></i>
            <i v-else class="bk-icon icon-edit-line" @click="handleVariableHook('edit')"></i>
        </div>
        <div class="rf-tag-hook">
            <bk-popover
                ref="tagHookPopover"
                placement="bottom-end"
                trigger="manual"
                theme="light"
                :arrow="false"
                :distance="5"
                :disabled="!isInputBoxControl"
                ext-cls="tag-hook-pop-content"
                :on-hide="() => isHookPopShow = false">
                <div
                    class="tag-hook-pop-wrap"
                    :class="{ 'is-active': hook, disabled: !option.formEdit || !render }"
                    v-bk-tooltips="{
                        content: hook ? $t('取消使用变量，节点内维护') : $t('转换为变量集中维护'),
                        placement: 'top',
                        zIndex: 3000,
                        disabled: isInputBoxControl && !hook
                    }"
                    @click="handleHookClick">
                    <i class="common-icon-variable-hook hook-icon"></i>
                    <i
                        v-if="isInputBoxControl && !hook"
                        :class="['bk-icon', isHookPopShow ? 'icon-angle-down-fill' : 'icon-angle-up-fill']">
                    </i>
                </div>
                <ul slot="content">
                    <li class="operate-item" @click="onInsertVariable">{{$t('插入已有变量')}}</li>
                    <li class="operate-item" @click="handleVariableHook('create')">{{$t('新建并插入变量')}}</li>
                    <li class="operate-item" @click="onHookForm">{{$t('转换为变量集中维护')}}</li>
                </ul>
            </bk-popover>
            <i
                v-if="isShowRenderIcon"
                :class="['common-icon-render-skip render-skip-icon', { 'is-active': !render, disabled: !option.formEdit || hook }]"
                v-bk-tooltips="{
                    content: !render ? $t('取消变量免渲染') : $t('变量免渲染'),
                    placement: 'top',
                    zIndex: 3000
                }"
                @click="onRenderChange">
            </i>
        </div>
    </div>
</template>

<script>
    import { mapState } from 'vuex'
    export default {
        name: 'FormHook',
        props: {
            params: Object
        },
        data () {
            const {
                isShow,
                value,
                scheme,
                hook,
                render,
                option
            } = this.params
            return {
                value,
                scheme,
                hook,
                render,
                option,
                showHook: isShow,
                isHookPopShow: false,
                isShowRenderIcon: false, // 是否展示免渲染icon
                isHooking: false
            }
        },
        computed: {
            ...mapState('template', [
                'varPanelActivated'
            ]),
            isInputBoxControl () {
                return ['input', 'textarea'].includes(this.scheme.type)
            },
            compInstance () {
                return this.$parent.$refs.tagComponent
            },
            variableSourceCount () {
                const { constants } = this.$parent
                const sameCode = Object.keys(constants).filter(keyItem => {
                    const { source_tag: sourceTag, source_type: sourceType } = constants[keyItem]
                    if (sourceTag) { // 判断 sourceTag 是否存在是为了兼容旧数据自定义全局变量 source_tag 为空
                        const tagCode = sourceTag.split('.')[1]
                        // 判断全局变量中是否有与被勾选表单项存在相同类型的，输入参数和输出参数不做比较
                        if (tagCode === this.scheme.tag_code && sourceType !== 'component_outputs') {
                            return true
                        }
                    }
                })
                return sameCode.length
            }
        },
        watch: {
            params: {
                handler (val) {
                    const keys = ['value', 'scheme', 'render', 'option', 'hook']
                    keys.forEach(key => {
                        this[key] = val[key]
                    })
                },
                deep: true
            },
            varPanelActivated (val) {
                if (!this.isHooking) return
                this.isHooking = val
                this.$nextTick(() => {
                    if (this.compInstance) {
                        const divWrapDom = this.compInstance.$el.querySelector('.rf-form-wrap')
                        divWrapDom.style.borderColor = val ? '#3a84ff' : ''
                    }
                })
            }
        },
        created () {
            // 移除「变量免渲染」的功能开关
            const { type, attrs } = this.scheme
            if (type === 'code_editor') {
                if (attrs.variable_render === false) { // variable_render 开启变量渲染
                    /**
                     * need_render:
                        1. false
                            之前已勾选，现在去掉免渲染icon
                        2.true，判断value
                            a. 不包含${}，需要把need_render置为false，去掉免渲染icon
                            b. 包含${}，保留免渲染icon
                     */
                    if (this.render) {
                        const regex = /\${[a-zA-Z_]\w*}/g
                        const matchList = this.value.match(regex)
                        const isMatch = matchList && matchList.some(item => {
                            return !!this.constants[item]
                        })
                        if (isMatch) {
                            this.isShowRenderIcon = true
                        } else {
                            this.showHook = false
                            this.$nextTick(() => {
                                this.onRenderChange()
                            })
                        }
                    } else {
                        this.showHook = false
                    }
                } else {
                    if (!this.render) {
                        this.isShowRenderIcon = true
                    }
                }
            } else if (!this.render) { // 如果开启了免渲染则展示按钮
                this.isShowRenderIcon = true
            }
        },
        mounted () {
        },
        methods: {
            handleHookClick () {
                if (!this.option.formEdit || !this.render) {
                    return
                }
                if (this.isInputBoxControl && !this.hook) {
                    this.isHookPopShow = !this.isHookPopShow
                    this.$refs.tagHookPopover.showHandler()
                    return
                }
                this.$emit('onHook', this.scheme.tag_code, !this.hook)
            },
            // 插入已有变量
            onInsertVariable () {
                this.$emit('change', this.scheme.tag_code, this.value + '$')
                setTimeout(() => {
                    this.compInstance.focus()
                }, 0)
                this.$refs.tagHookPopover.hideHandler()
            },
            // 变量勾选
            onHookForm () {
                this.isHooking = true
                this.$emit('onHook', this.scheme.tag_code, !this.hook)
                this.$refs.tagHookPopover.hideHandler()
            },
            // 变量重选/修改
            handleVariableHook (type) {
                if (!this.option.formEdit) return
                this.isHooking = true
                // 向上抛出边框勾选事件
                this.$emit('handleVariableHook', {
                    type,
                    code: this.scheme.tag_code
                })
                if (this.isHookPopShow) {
                    this.$refs.tagHookPopover.hideHandler()
                }
            },
            // 免渲染切换
            onRenderChange () {
                if (!this.option.formEdit || this.hook) {
                    return
                }
                this.$emit('onRenderChange', this.scheme.tag_code, !this.render)
            }
        }
    }
</script>

<style lang="scss" scoped>
.form-hook {
    display: flex;
    justify-content: flex-end;
    min-width: 0;
    margin-left: 8px;
    .tag-hooked-form-content {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 32px;
        min-width: 0;
        padding: 0 4px 0 10px;
        margin-right: 8px;
        font-size: 12px;
        color: #63656e;
        background: #fff;
        border: 1px solid #cdc6cc;
        border-radius: 2px;
        cursor: not-allowed;
        span {
            margin-right: 10px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
        }
        i {
            height: 24px;
            width: 24px;
            text-align: center;
            line-height: 24px;
            font-size: 16px;
            color: #979ba5;
            background: #f0f1f5;
            border-radius: 2px;
            &:hover {
                cursor: pointer;
                color: #3a84ff;
                background: #e1ecff;
            }
        }
        &.active {
            border-color: #3a84ff !important;
        }
    }
    .rf-tag-hook {
        display: flex;
        .tag-hook-pop-wrap,
        .render-skip-icon {
            display: inline-block;
            height: 32px;
            width: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            color: #979ba5;
            background: #f0f1f5;
            border-radius: 2px;
            cursor: pointer;
            &:hover {
                background: #e1ecff;
            }
            &.disabled {
                color: #c4c6cc;
                background: #f0f1f5;
                cursor: not-allowed;
            }
            &.is-active {
                color: #3a84ff;
                background: #e1ecff;
            }
        }
        .tag-hook-pop-wrap {
            width: 42px;
            font-size: 16px;
            .icon-angle-down-fill,
            .icon-angle-up-fill {
                font-size: 12px;
                color: #979ba5;
                margin-left: 2px;
            }
        }
        .render-skip-icon {
            margin-left: 4px;
        }
    }
    &.hook-mode {
        flex: 1;
        margin-left: 0;
    }
    &.disable-mode {
        .tag-hooked-form-content {
            background-color: #fafbfd;
            border-color: #dcdee5;
            i {
                color: #c4c6cc;
                &:hover {
                    background: #f0f1f5;
                    cursor: not-allowed;
                }
            }
        }
        .icon-angle-up-fill {
            color: #c4c6cc !important;
        }
    }
}
</style>
