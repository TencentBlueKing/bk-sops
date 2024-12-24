<template>
    <div class="editorContainer">
        <div :id="randomId" ref="editorRef"></div>
    </div>
</template>
<script>
    import Editor from '@toast-ui/editor'
    import { mapActions } from 'vuex'
    import axios from 'axios'

    export default {
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
                timer: null
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
                this.editor = new Editor({
                    el: this.$refs.editorRef,
                    height: '336px',
                    initialEditType: 'markdown',
                    previewStyle: 'tab',
                    initialValue: this.value,
                    hideModeSwitch: true
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
                'getFileUploadAddr'
            ]),
            async handleFileUpload (blob, cb) {
                try {
                    // 这里补充上传图片逻辑并将url通过cb传回
                    const resp = await this.getFileUploadAddr({
                        file_name: blob.name,
                        scene_type: this.sceneType
                    })
                    await axios({
                        url: resp.upload_url,
                        method: 'put',
                        data: blob, // 直接将 File 对象作为请求体
                        withCredentials: false,
                        headers: {
                            'content-Type': blob.type // 使用文件本身的类型
                            // 如果需要添加额外的请求头，可以在这里添加
                            // 'Authorization': 'Bearer your-token',
                        }
                    })
                    cb(resp.download_url)
                } catch (error) {
                    console.warn(error)
                }
            }
        }
    }

</script>
