<template>
    <div class="editorPreviewContainer">
        <div :id="randomId" ref="editorRef"></div>
    </div>
</template>
<script>
    import Editor from '@toast-ui/editor'
    export default {
        props: {
            value: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                randomId: `editor${(Math.random() * 100000).toFixed(0)}`
            }
        },
        mounted () {
            Editor.factory({
                el: this.$refs.editorRef,
                initialEditType: 'markdown',
                previewStyle: 'tab',
                initialValue: this.value,
                hideModeSwitch: true,
                viewer: true
            })
        }
    }
</script>
