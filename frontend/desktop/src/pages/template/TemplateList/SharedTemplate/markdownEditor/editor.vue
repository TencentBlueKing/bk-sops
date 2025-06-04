<template>
    <div class="editorContainer">
        <div :id="randomId" ref="editorRef" style="height: 100%"></div>
        <div ref="uploadVideoBtn" v-show="editor">
            <bk-popover
                ref="uploadPop"
                width="450"
                :is-show="isShow"
                theme="light"
                trigger="click"
                @after-hidden="isShow = $event"
            >
                <span class="uploadVideoBtn common-icon-play"></span>
                <template #content>
                    <div style="padding-bottom: 40px">
                        <div style="font-weight: 600; color: #555; display: block; margin: 20px 0 5px">
                            {{ $t('选择视频文件') }}
                        </div>
                        <videoUpload ref="videoInputRef" :scene-type="sceneType"></videoUpload>
                        <div style="position: absolute; right: 40px; bottom: 20px">
                            <bk-button theme="primary" size="small" @click="uploadFile">{{ $t('确认') }}</bk-button>
                            <bk-button size="small" @click="toggleIsShow(false)">{{ $t('取消') }}</bk-button>
                        </div>
                    </div>
                </template>
            </bk-popover>
        </div>
    </div>
</template>
<script>
    import Editor from '@toast-ui/editor'
    import { mapActions } from 'vuex'
    import VideoUpload from './videoUpload.vue'

    export default {
        components: {
            VideoUpload
        },
        model: {
            prop: 'value',
            event: 'change'
        },
        props: {
            value: {
                type: String,
                default: ''
            },
            sceneType: {
                type: String,
                default: 'flow_template'
            }
        },
        data () {
            return {
                randomId: `editor${(Math.random() * 100000).toFixed(0)}`,
                editor: null,
                timer: null,
                isShow: false
            }
        },
        computed: {

        },
        watch: {
            value (val) {
                if (this.timer) {
                    clearTimeout(this.timer)
                }
                if (val !== this.editor.getMarkdown()) {
                    this.timer = setTimeout(() => {
                        this.editor.setMarkdown(val)
                    }, 200)
                }
            }
        },
        mounted () {
            setTimeout(() => {
                const videoTool = {
                    name: this.$t('上传视频'),
                    el: this.$refs.uploadVideoBtn,
                    tooltip: 'Insert Video'
                }
                const editorRef = this.$refs.editorRef
                const height = Math.max(editorRef.clientHeight || 0, 450) + 'px'
                this.editor = new Editor({
                    el: editorRef,
                    height,
                    initialEditType: 'markdown',
                    previewStyle: 'tab',
                    initialValue: this.value,
                    plugins: [this.getVideoPlugins],
                    toolbarItems: [
                        ['heading', 'bold', 'italic'],
                        ['quote', 'ul', 'ol'],
                        ['image', videoTool, 'table', 'link', 'codeblock']
                    ]
                })
                this.editor.addHook('addImageBlobHook', this.handleFileUpload)
                this.editor.on('change', () => {
                    this.$emit('change', this.editor.getMarkdown())
                })
                this.editor.removeToolbarItem('codeblock')
            }, 500)
        },
        methods: {
            ...mapActions('templateMarket/', [
                'getFileUploadAddr',
                'uploadFileToUrl'
            ]),
            getVideoPlugins () {
                const toHTMLRenderers = {
                    video (node) {
                        const src = node.literal.replaceAll('\\', '')
                        return [
                            {
                                type: 'openTag',
                                tagName: 'video',
                                attributes: {
                                    controls: true,
                                    src,
                                    class: 'markdownVideo'
                                },
                                outerNewLine: true
                            },
                            { type: 'closeTag', tagName: 'video', outerNewLine: true }
                        ]
                    }
                }
                return { toHTMLRenderers }
            },
            async handleFileUpload (blob, cb) {
                try {
                    // 这里补充上传图片逻辑并将url通过cb传回
                    const resp = await this.getFileUploadAddr({
                        file_name: blob.name.replaceAll(' ', ''),
                        scene_type: this.sceneType
                    })
                    await this.uploadFileToUrl({
                        upload_url: resp.upload_url,
                        blob
                    })
                    cb(resp.download_url)
                } catch (error) {
                    console.warn(error)
                }
            },
            async uploadFile () {
                const url = await this.$refs.videoInputRef.uploadFiles()
                if (url) {
                    const content = ['\n', '$$video', `${url}`, '$$', ''].join('\n')
                    this.editor.replaceSelection(content)
                }
                this.isShow = false
                this.$refs.uploadPop.hideHandler()
                return true
            },
            toggleIsShow (val) {
                this.isShow = val
                if (val) {
                    this.$refs.uploadPop.showHandler()
                } else {
                    this.$refs.uploadPop.hideHandler()
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    ::v-deep .markdownVideo {
        width: 100%;
    }
    .editorContainer {
        height: 100%;
    }
    .uploadVideoBtn {
        display: flex;
        height: 32px;
        width: 32px;
        cursor: pointer;
        justify-content: center;
        font-size: 20px;
        align-items: center;
        border-radius: 3px;
        &:hover {
            background-color: #fff;
            border: 1px solid #e4e7ee;
        }
    }
</style>
