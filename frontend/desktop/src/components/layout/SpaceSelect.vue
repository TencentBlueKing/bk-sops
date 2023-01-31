<template>
    <div class="space-select-wrapper">
        <div class="space-select">
            <span class="slot-prepend">{{ $t('空间') }}</span>
            <bk-select
                ref="spaceSelect"
                v-model="crtSpace"
                placeholder="请选择空间"
                searchable
                :clearable="false"
                :popover-width="248"
                :popover-options="{
                    placement: 'bottom-end',
                    offset: '1, 0',
                    onHide: handleDropdownHide
                }"
                ext-popover-cls="space-select-popover-list"
                @selected="handleSpaceSelected">
                <bk-option
                    v-for="spaceInfo in commonSpaceList"
                    :key="spaceInfo.id"
                    :id="spaceInfo.id"
                    :name="spaceInfo.name">
                    <div class="space-select-option">
                        <div class="option-content">
                            <span>{{ spaceInfo.name }}</span>
                            <span v-if="spaceInfo.code">{{ $t('（') + spaceInfo.code + $t('）') }}</span>
                        </div>
                        <div v-if="spaceInfo.code" class="operate-wrap">
                            <i
                                v-bk-tooltips="{ content: $t('管理空间'), boundary: 'window' }"
                                v-cursor="{ active: !spaceInfo.auth_actions.includes('common_space_manage') }"
                                class="bk-icon icon-cog"
                                @click.stop="onEditSpace(spaceInfo)">
                            </i>
                            <i
                                v-bk-tooltips="{ content: $t('删除空间'), boundary: 'window' }"
                                v-cursor="{ active: !spaceInfo.auth_actions.includes('common_space_manage') }"
                                class="bk-icon icon-close-line-2"
                                @click.stop="onDeleteSpace(spaceInfo)">
                            </i>
                        </div>
                    </div>
                </bk-option>
                <div slot="extension" class="space-select-extension">
                    <div
                        class="add-space"
                        data-test-id="commonProcess_header__createSpace"
                        @click="onCreateSpace">
                        <i class="bk-icon icon-plus-circle"></i>
                        <span>{{ $t('新建空间') }}</span>
                    </div>
                </div>
            </bk-select>
        </div>
        <bk-dialog
            v-model="isCreateDialogShow"
            theme="primary"
            :mask-close="false"
            :auto-close="false"
            header-position="left"
            render-directive="if"
            width="480"
            :title="isEditSpace ? $t('编辑空间') : $t('新建空间')"
            :ok-text="isEditSpace ? $t('保存') : $t('创建')"
            ext-cls="create-space-dialog"
            :loading="isCreateLoading"
            @confirm="onConfirm"
            @cancel="onCancel">
            <bk-form :model="formData" :rules="rules" :label-width="86" ref="spaceValidate">
                <bk-form-item :label="$t('空间名称')" required property="name">
                    <bk-input
                        :placeholder="$t('不超过 50 个字符')"
                        v-model="formData.name">
                    </bk-input>
                </bk-form-item>
                <bk-form-item :label="$t('空间代号')" required property="code">
                    <bk-input
                        :placeholder="$t('不超过 50 个字符，由字母、数字、下划线组成')"
                        v-model="formData.code">
                    </bk-input>
                </bk-form-item>
                <bk-form-item :label="$t('空间管理员')">
                    <member-select
                        :multiple="true"
                        :placeholder="$t('可管理空间和流程，创建人自动成为管理员')"
                        v-model="formData.manager">
                    </member-select>
                </bk-form-item>
                <bk-form-item :label="$t('空间成员')">
                    <member-select
                        :multiple="true"
                        :placeholder="$t('仅可管理空间下的流程')"
                        v-model="formData.member">
                    </member-select>
                </bk-form-item>
                <bk-form-item :label="$t('空间说明')" property="description">
                    <bk-input
                        style="height: 80px"
                        :placeholder="$t('至少 5 个字符')"
                        :type="'textarea'"
                        v-model="formData.description">
                    </bk-input>
                </bk-form-item>
            </bk-form>
        </bk-dialog>
    </div>
</template>

<script>
    import permission from '@/mixins/permission.js'
    import MemberSelect from '@/components/common/Individualization/MemberSelect.vue'
    import { mapState, mapMutations, mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
    export default {
        components: {
            MemberSelect
        },
        mixins: [permission],
        data () {
            return {
                crtSpace: '',
                commonSpaceList: [],
                authActions: [],
                isEditSpace: false, // 是否为编辑空间
                isCreateDialogShow: false,
                isCreateLoading: false,
                formData: {
                    name: '',
                    code: '',
                    manager: [],
                    member: [],
                    description: ''
                },
                rules: {
                    name: [
                        {
                            required: true,
                            message: this.$t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            max: 50,
                            message: this.$t('不超过 50 个字符'),
                            trigger: 'blur'
                        }
                    ],
                    code: [
                        {
                            required: true,
                            message: this.$t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            validator: (val) => {
                                const regex = /[a-zA-Z0-9_]+/
                                return regex.test(val) && val.length <= 50
                            },
                            message: this.$t('不超过 50 个字符，由字母、数字、下划线组成'),
                            trigger: 'blur'
                        }
                    ],
                    description: [
                        {
                            min: 5,
                            message: this.$t('至少 5 个字符'),
                            trigger: 'blur'
                        }
                    ]
                },
                isDeleteLoading: false
            }
        },
        computed: {
            ...mapState({
                'username': state => state.username
            })
        },
        created () {
            this.getCommonSpaceList()
        },
        methods: {
            ...mapActions('template', [
                'getCommonSpace',
                'createCommonSpace',
                'updateCommonSpace',
                'deleteCommonSpace'
            ]),
            ...mapMutations('template/', [
                'setCommonSpace'
            ]),
            async getCommonSpaceList () {
                try {
                    const resp = await this.getCommonSpace()
                    this.commonSpaceList = [
                        { name: '默认空间', id: -1 },
                        ...resp.data
                    ]
                    this.crtSpace = -1
                    this.setCommonSpace({
                        id: this.crtSpace,
                        list: this.commonSpaceList
                    })
                } catch (error) {
                    console.warn(error)
                }
            },
            handleDropdownHide () {
                if (!this.isCreateDialogShow && !this.isDeleteLoading) {
                    this.$refs.spaceSelect.focus = false
                    return true
                }
                return false
            },
            handleSpaceSelected () {
                this.setCommonSpace({
                    id: this.crtSpace,
                    list: this.commonSpaceList
                })
            },
            onEditSpace (info) {
                if (!info.auth_actions.includes('common_space_manage')) {
                    return
                }
                this.isEditSpace = true
                this.formData = tools.deepClone(info)
                this.isCreateDialogShow = true
            },
            onDeleteSpace (info) {
                if (!info.auth_actions.includes('common_space_manage')) {
                    return
                }
                if (this.isDeleteLoading) return
                this.isDeleteLoading = true
                this.$bkInfo({
                    title: '是否删除空间【数据库】?',
                    confirmLoading: true,
                    confirmFn: async () => {
                        await this.deleteCommonSpace({ spaceId: info.id })
                        this.isDeleteLoading = false
                        // 拉取新的空间列表
                        this.getCommonSpaceList()
                        this.$bkMessage({
                            message: this.$t('空间删除成功'),
                            theme: 'success'
                        })
                    },
                    cancelFn: () => {
                        this.isDeleteLoading = false
                    }
                })
            },
            onCreateSpace () {
                this.isEditSpace = false
                this.formData = {
                    name: '',
                    code: '',
                    manager: [],
                    member: [],
                    description: ''
                }
                this.isCreateDialogShow = true
            },
            onConfirm () {
                if (this.isCreateLoading) return
                this.$refs.spaceValidate.validate().then(async () => {
                    try {
                        this.isCreateLoading = true
                        const funcName = this.isEditSpace ? 'updateCommonSpace' : 'createCommonSpace'
                        await this[funcName]({ creator: this.username, ...this.formData })
                        this.isCreateDialogShow = false
                        // 拉取新的空间列表
                        this.getCommonSpaceList()
                        this.$bkMessage({
                            message: this.isEditSpace ? this.$t('空间修改成功') : this.$t('空间创建成功'),
                            theme: 'success'
                        })
                    } catch (error) {
                        console.warn(error)
                    } finally {
                        this.isCreateLoading = false
                    }
                })
            },
            onCancel () {
                this.isCreateDialogShow = false
            }
        }
    }
</script>

<style lang="scss" scoped>
    .space-select-wrapper {
        margin-right: 18px;
        .space-select {
            display: flex;
            align-items: center;
            width: 248px;
            .slot-prepend {
                width: 40px;
                height: 32px;
                font-size: 12px;
                color: #63656e;
                text-align: center;
                line-height: 30px;
                border: 1px solid #c4c6cc;
                border-right: none;
                border-radius: 2px 0 0 2px;
                background: #fafbfd;
            }
            .bk-select {
                width: 208px;
                border-radius: 0 2px 2px 0;
                .bk-select-name {
                    height: 32px;
                }
            }
        }
    }
</style>
<style lang="scss">
    .space-select-popover-list {
        .bk-option {
            .bk-option-content {
                padding: 0;
            }
            .space-select-option {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 16px;
                .option-content {
                    white-space: nowrap;
                    text-overflow: ellipsis;
                    overflow: hidden;
                }
                .operate-wrap {
                    display: flex;
                    align-items: center;
                    font-size: 16px;
                    color: #979ba5;
                    opacity: 0;
                    .icon-cog {
                        font-size: 14px;
                    }
                    .bk-icon {
                        margin-left: 16px;
                    }
                }
                &:hover {
                    color: #63656e;
                    background: #f5f7fa;
                    .operate-wrap {
                        opacity: 1;
                    }
                }
            }
            &.is-selected .space-select-option {
                color: #3a84ff;
                background: #e1ecff;

            }
        }
        .bk-select-extension {
            height: 40px;
            line-height: 40px;
            text-align: center;
            padding: 0;
            cursor: pointer;
        }
    }
    .create-space-dialog {
        .bk-form .bk-label {
            font-size: 12px;
            padding-right: 22px;
        }
        .user-selector {
            width: 100%;
        }
    }
</style>
