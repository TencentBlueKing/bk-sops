<script>
    export default {
        name: 'LoadingBtnDialog',
        props: ['pending', 'btnAmount'],
        data () {
            return {
                i18n: {
                    confirm: gettext('确认'),
                    cancel: gettext('取消')
                }
            }
        },
        methods: {
            onConfirm () {
                this.$emit('onConfirm')
            },
            onCancel () {
                this.$emit('onCancel')
            }
        },
        render: function (h) {
            return h('bk-button', {
                'class': 'confirm',
                props: {
                    type: 'primary',
                    loading: false
                },
                nativeOn: {
                    click: this.onConfirm
                },
                domProps: {
                    innerHTML: this.i18n.confirm
                }
            })
        }
    }
</script>
<style lang="scss">
    .confirm {
        width: 120px;
        height: 32px;
    }
    .cancel {
        width:70px;
        height:32px;
    }
</style>
