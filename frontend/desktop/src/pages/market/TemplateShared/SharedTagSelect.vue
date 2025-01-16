<template>
    <bk-select
        :value="value"
        searchable
        multiple
        display-tag
        :placeholder="$t('请选择标签')"
        ext-popover-cls="tpl-shared-tag-popover"
        :loading="loading"
        @change="onSelectChange">
        <bk-option v-for="(tag, index) in tagList"
            :key="index"
            :id="tag.id"
            :name="tag.name">
        </bk-option>
        <template slot="extension">
            <bk-input
                v-if="isTagInputShow"
                ref="tagInput"
                v-model="newTag"
                :placeholder="$t('请输入标签，enter保存')"
                @blur="resetTagInput"
                @enter="addTag">
            </bk-input>
            <div v-else @click="showTagInput">
                <i class="bk-icon icon-plus-circle mr2"></i>
                {{ $t('新增') }}
            </div>
        </template>
    </bk-select>
</template>
<script>
    import { mapActions } from 'vuex'

    export default {
        model: {
            prop: 'value',
            event: 'change'
        },
        props: {
            loading: {
                type: Boolean,
                default: false
            },
            value: {
                type: Array,
                default: () => ([])
            },
            tagList: {
                type: Array,
                default: () => ([])
            }
        },
        data () {
            return {
                isTagInputShow: false,
                newTag: ''
            }
        },
        methods: {
            ...mapActions('templateMarket/', [
                'createLabel'
            ]),
            onSelectChange (val) {
                this.$emit('change', val)
            },
            showTagInput () {
                this.isTagInputShow = true
                this.$nextTick(() => {
                    this.$refs.tagInput.focus()
                })
            },
            resetTagInput () {
                this.isTagInputShow = false
                this.newTag = ''
            },
            async addTag () {
                if (this.newTag) {
                    // 判断是否存在重复
                    const isExist = this.tagList.find(item => item.name === this.newTag)
                    if (isExist) {
                        this.$bkMessage({
                            message: this.$t('【n】标签已存在', { n: this.newTag }),
                            theme: 'error'
                        })
                        return
                    }
                    try {
                        const resp = await this.createLabel({
                            name: this.newTag,
                            code: this.newTag
                        })
                        // 添加新标签到父组件的标签列表
                        this.$emit('update:tagList', [...this.tagList, resp.data])
                        // 添加新标签到选中的标签列表
                        this.$emit('change', [...this.value, resp.data.id])
                    } catch (error) {
                        console.warn(error)
                    }
                }
                this.isTagInputShow = false
            }
        }
    }
</script>
<style lang="scss">
    .tpl-shared-tag-popover {
        .bk-select-extension {
            padding: 2px 10px;
            text-align: center;
            line-height: 30px;
            cursor: pointer;
            .bk-form-input {
                height: 30px;
            }
        }
    }
</style>
