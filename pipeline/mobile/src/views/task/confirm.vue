<template>
    <div>
        <van-button
            type="primary"
            plain
            @click="onClickConfirm">
            确定弹窗
        </van-button>
        <van-dialog
            v-model="show"
            title="标题"
            show-cancel-button>
        </van-dialog>
    </div>
</template>
<script>
    export default {
        name: 'confirm',
        data () {
            return {
                show: false
            }
        },
        methods: {
            onClickConfirm () {
                this.$dialog.confirm({
                    message: '弹窗内容'
                })
            }
        }
    }
</script>
