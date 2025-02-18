<template>
    <div class="file-upload">
        <input
            v-model="fileName"
            type="text"
            :placeholder="$t('仅支持上传.mp4,.mov文件')"
            readonly
            class="file-input-display"
            @click="triggerFileInput"
        />
        <bk-button class="mb10" :disabled="!selectedFiles.length" @click="triggerFileInput">{{ $t('选择文件') }}</bk-button>
        <input
            ref="fileInput"
            type="file"
            accept=".mp4,.mov"
            :multiple="false"
            class="file-input-hidden"
            @change="handleFileChange"
        />
    </div>
</template>

<script>
    import { mapActions } from 'vuex'

    export default {
        props: {
            sceneType: {
                type: String,
                required: true
            }
        },
        data () {
            return {
                fileName: '',
                selectedFiles: [],
                uploading: false
            }
        },
        methods: {
            ...mapActions('templateMarket/', [
                'getFileUploadAddr',
                'uploadFileToUrl'
            ]),
            handleFileChange (event) {
                const { files } = event.target
                if (files) {
                    const fileList = Array.from(files)
                    if (
                        fileList
                            .map(file => file.name)
                            .join('')
                            .includes('\\')
                    ) {
                        this.$bkMessage({
                            content: '文件名称不能带有‘\\’'
                        })
                        return
                    }
                    this.selectedFiles = fileList

                    this.fileName = this.selectedFiles.map(file => file.name).join(', ') || ''
                }
            },

            async uploadFiles () {
                if (this.selectedFiles.length === 0) return null

                try {
                    this.uploading = true

                    const resp = await this.getFileUploadAddr({
                        file_name: this.selectedFiles[0].name,
                        scene_type: this.sceneType
                    })
                    await this.uploadFileToUrl({
                        upload_url: resp.upload_url,
                        blob: this.selectedFiles[0]
                    })
                    return resp.download_url
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.uploading = false
                }
            },
            triggerFileInput () {
                this.$refs.fileInput.click()
            }
        }
    }

</script>

<style lang="scss" scoped>
  .file-upload {
    display: flex;
    flex-direction: row;
    align-items: center;
  }

  .file-input-display {
    width: 300px;
    padding: 10px;
    margin-bottom: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    cursor: pointer;
    height: 32px;
    box-sizing: border-box;
    margin-right: 8px;
  }

  .file-input-hidden {
    display: none; /* Hide the actual file input */
  }
</style>
