<template>
    <div class="navigator-head-right">
        <!-- 选择业务 -->
        <div v-if="!isProjectHidden" class="project-select">
            <ProjectSelector :read-only="isProjectReadOnly" @reloadHome="reloadHome"></ProjectSelector>
        </div>
        <!-- 更多操作 -->
        <div
            :class="['help-icon', { active: isMoreOperateActive }]"
            v-bk-tooltips="{
                placement: 'bottom',
                allowHtml: 'true',
                theme: 'light',
                hideOnClick: false,
                extCls: 'more-operation-tips',
                content: '#more-operation-html'
            }">
            <i class="common-icon-help"></i>
        </div>
        <div id="more-operation-html">
            <div class="operate-item" @click="goToHelpDoc">{{ $t('产品文档') }}</div>
            <div class="operate-item" @click="onOpenVersion">{{ $t('版本日志') }}</div>
            <div class="operate-item" @click="goToFeedback">{{ $t('问题反馈') }}</div>
        </div>
        <!-- 用户icon -->
        <div class="user-avatar">{{ username }}</div>
        <!-- 日志组件 -->
        <version-log
            ref="versionLog"
            :log-list="logList"
            :log-detail="logDetail"
            :loading="logListLoading || logDetailLoading"
            @active-change="handleVersionChange">
        </version-log>
    </div>
</template>
<script>
    import { mapActions, mapState } from 'vuex'
    import ProjectSelector from './ProjectSelector.vue'
    import VersionLog from './VersionLog.vue'

    export default {
        name: 'NavigatorHeadRight',
        inject: ['reload'],
        components: {
            ProjectSelector,
            VersionLog
        },
        data () {
            return {
                bkDocUrl: window.BK_DOC_URL,
                bkFeedbackUrl: window.FEEDBACK_URL,
                logList: [],
                logDetail: '',
                isMoreOperateActive: false,
                logListLoading: false,
                logDetailLoading: false
            }
        },
        computed: {
            ...mapState({
                view_mode: state => state.view_mode,
                username: state => state.username
            }),
            ...mapState('project', {
                projectList: state => state.userProjectList
            }),
            // 隐藏右侧项目信息
            isProjectHidden () {
                if (this.view_mode !== 'appmaker' && this.projectList.length === 0) {
                    return true
                }
                const paths = ['/home', '/common/', '/admin/', '/project/', '/function/home', '/audit/home']
                return paths.some(path => this.$route.path.startsWith(path))
            },
            // 项目名称只读
            isProjectReadOnly () {
                if (this.view_mode === 'appmaker') {
                    return true
                }
                const paths = ['/audit/', '/function/']
                return paths.some(path => this.$route.path.startsWith(path))
            }
        },
        created () {
            if (this.view_mode !== 'appmaker') {
                this.loadUserProjectList({ limit: 0, is_disable: false })
            }
        },
        methods: {
            ...mapActions([
                'getVersionList',
                'getVersionDetail'
            ]),
            ...mapActions('project', [
                'loadUserProjectList'
            ]),
            goToHelpDoc () {
                window.open(this.bkDocUrl, '_blank')
            },
            goToFeedback () {
                window.open(this.bkFeedbackUrl, '_blank')
            },
            /* 打开版本日志 */
            async onOpenVersion () {
                this.$refs.versionLog.show()
                try {
                    this.logListLoding = true
                    const res = await this.getVersionList()
                    this.logList = res.data
                } catch (e) {
                    console.log(e)
                } finally {
                    this.logListLoding = false
                }
            },
            async loadLogDetail (version) {
                try {
                    this.logDetailLoding = true
                    const res = await this.getVersionDetail({ version })
                    this.logDetail = res.data
                } catch (e) {
                    console.log(e)
                } finally {
                    this.logDetailLoding = false
                }
            },
            handleVersionChange (data) {
                const version = data[0]
                this.loadLogDetail(version)
            },
            reloadHome () {
                this.reload()
            }
        }
    }
</script>
<style lang="scss" scoped>
    .navigator-head-right {
        display: flex;
        align-items: center;
        .project-select >>> .project-wrapper {
            margin-top: 0;
            width: 240px;
        }
        .help-icon {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 32px;
            height: 32px;
            font-size: 16px;
            color: #63656e;
            border-radius: 50%;
            cursor: pointer;
            transition: brackground .2s;
            &.tippy-active {
                background: #f0f1f5;
                i {
                    color: #3a84ff;
                }
            }
        }
        .user-avatar {
            margin-left: 10px;
            font-size: 14px;
            color: #747c85;
            .common-icon-dark-circle-avatar {
                cursor: text;
            }
        }
        /deep/ .bk-select.is-disabled {
            background: none;
        }
    }
</style>
<style lang="scss">
    .tippy-popper.more-operation-tips {
        .tippy-tooltip {
            padding: 4px 0;
        }
        #more-operation-html {
            .operate-item {
                display: block;
                height: 32px;
                line-height: 33px;
                padding: 0 20px;
                color: #63656e;
                font-size: 12px;
                text-decoration: none;
                white-space: nowrap;
                cursor: pointer;
                &:hover {
                    background-color: #eaf3ff;
                    color: #3a84ff;
                }
            }
        }
    }
</style>
