<template>
    <div class="navigator-head-right">
        <!-- 选择业务 -->
        <div v-if="!isProjectHidden" class="project-select">
            <ProjectSelector :read-only="isProjectReadOnly" @reloadHome="reloadHome"></ProjectSelector>
        </div>
        <!-- 语言 -->
        <div
            class="language-icon"
            v-bk-tooltips="{
                placement: 'bottom-end',
                allowHtml: 'true',
                arrow: false,
                distance: 17,
                theme: 'light',
                hideOnClick: false,
                extCls: 'more-language-tips',
                content: '#more-language-html'
            }">
            <i :class="`bk-icon icon-${curLanguage}`"></i>
        </div>
        <div id="more-language-html">
            <div
                class="operate-item"
                :class="{ 'active': curLanguage === 'chinese' }"
                data-test-id="navHeader_list_chinese"
                @click="toggleLanguage('chinese')">
                <i class="bk-icon icon-chinese"></i>
                {{ '中文' }}
            </div>
            <div
                class="operate-item"
                :class="{ 'active': curLanguage === 'english' }"
                data-test-id="navHeader_list_english"
                @click="toggleLanguage('english')">
                <i class="bk-icon icon-english"></i>
                {{ 'English' }}
            </div>
        </div>
        <!-- 更多操作 -->
        <div
            :class="['help-icon', { active: isMoreOperateActive }]"
            v-bk-tooltips="{
                placement: 'bottom-end',
                allowHtml: 'true',
                arrow: false,
                distance: 17,
                theme: 'light',
                hideOnClick: false,
                extCls: 'more-operation-tips',
                content: '#more-operation-html'
            }">
            <i class="common-icon-help"></i>
        </div>
        <div id="more-operation-html">
            <div class="operate-item" data-test-id="navHeader_list_productDoc" @click="goToHelpDoc">{{ $t('产品文档') }}</div>
            <div class="operate-item" data-test-id="navHeader_list_versionLog" @click="onOpenVersion">{{ $t('版本日志') }}</div>
            <div class="operate-item" data-test-id="navHeader_list_feedback" @click="goToFeedback">{{ $t('问题反馈') }}</div>
        </div>
        <!-- 用户icon -->
        <div
            class="user-avatar"
            v-bk-tooltips="{
                placement: 'bottom-end',
                allowHtml: 'true',
                arrow: false,
                distance: 25,
                theme: 'light',
                hideOnClick: false,
                extCls: 'logout-tips',
                content: '#logout-html'
            }">
            {{ username }}
            <i class="bk-icon icon-down-shape"></i>
        </div>
        <div id="logout-html">
            <div class="operate-item" data-test-id="navHeader_list_logout" @click="handleLogout">{{ $t('退出登录') }}</div>
        </div>
        <!-- 日志组件 -->
        <version-log
            ref="versionLog"
            :log-list="logList"
            :log-detail="logDetail"
            :md-mode="true"
            :loading="logListLoading || logDetailLoading"
            @active-change="handleVersionChange">
        </version-log>
    </div>
</template>
<script>
    import { mapActions, mapMutations, mapState } from 'vuex'
    import ProjectSelector from './ProjectSelector.vue'
    import VersionLog from './VersionLog.vue'
    import Cookies from 'js-cookie'
    import axios from 'axios'

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
                logDetailLoading: false,
                curLanguage: 'chinese'
            }
        },
        computed: {
            ...mapState({
                view_mode: state => state.view_mode,
                username: state => state.username
            }),
            ...mapState('project', {
                project_id: state => state.project_id,
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
        async created () {
            this.curLanguage = getCookie('blueking_language') === 'en' ? 'english' : 'chinese'
            if (this.view_mode !== 'appmaker') {
                await this.loadUserProjectList({
                    params: { is_disable: false }
                })
                if (this.projectList.length && !this.project_id) {
                    const projectId = this.projectList[0].id
                    this.setProjectId(projectId)
                }
            }
            this.queryHasNewVersion()
        },
        methods: {
            ...mapActions([
                'queryNewVersion',
                'getVersionList',
                'getVersionDetail'
            ]),
            ...mapActions('project', [
                'loadUserProjectList'
            ]),
            ...mapMutations('project', [
                'setProjectId'
            ]),
            async toggleLanguage (language) {
                this.curLanguage = language
                const local = language === 'chinese' ? 'zh-cn' : 'en'
                const domain = window.BK_DOMAIN || window.location.hostname.replace(/^[^.]+(.*)$/, '$1')
                Cookies.set('blueking_language', local, {
                    expires: 1,
                    domain,
                    path: '/'
                })
                if (window.BK_PAAS_ESB_HOST) {
                    const url = `${window.BK_PAAS_ESB_HOST}/api/c/compapi/v2/usermanage/fe_update_user_language/`
                    try {
                        await axios.jsonp(url, { language: local })
                    } catch (error) {
                        console.warn(error)
                    } finally {
                        window.location.reload()
                    }
                } else {
                    window.location.reload()
                }
            },
            goToHelpDoc () {
                window.open(this.bkDocUrl, '_blank')
            },
            goToFeedback () {
                window.open(this.bkFeedbackUrl, '_blank')
            },
            // 查询用户是否读过最新的产品日志，如果自动弹出日志弹窗
            async queryHasNewVersion () {
                const res = await this.queryNewVersion()
                if (!res.data.has_read_latest) {
                    this.onOpenVersion()
                }
            },
            /* 打开版本日志 */
            async onOpenVersion () {
                this.$refs.versionLog.show()
                try {
                    this.logListLoading = true
                    const res = await this.getVersionList()
                    this.logList = res.data
                } catch (e) {
                    console.log(e)
                } finally {
                    this.logListLoading = false
                }
            },
            async loadLogDetail (version) {
                try {
                    this.logDetailLoading = true
                    const res = await this.getVersionDetail({ version })
                    this.logDetail = res.data
                } catch (e) {
                    console.log(e)
                } finally {
                    this.logDetailLoading = false
                }
            },
            handleVersionChange (data) {
                const version = data[0]
                this.loadLogDetail(version)
            },
            reloadHome () {
                this.reload()
            },
            handleLogout () {
                const newUrl = window.location.origin + (window.SITE_URL || '/') + 'logout'
                window.location.replace(newUrl)
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
            margin-right: 18px;
            width: 240px;
            background: #f0f1f5;
            &.read-only {
                background: #fff;
            }
        }
        .language-icon,
        .help-icon {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 32px;
            height: 32px;
            font-size: 16px;
            color: #979ba5;
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
        .language-icon {
            font-size: 18px;
            margin-right: 10px;
        }
        .user-avatar {
            margin-left: 16px;
            font-size: 14px;
            color: #96a2b9;
            cursor: pointer;
            .icon-down-shape {
                position: relative;
                top: -1px;
                color: #979ba5;
            }
            &:hover {
                color: #3a84ff;
                i {
                    color: #3a84ff;
                }
            }
        }
        /deep/ .bk-select.is-disabled {
            background: none;
        }
    }
</style>
<style lang="scss">
    .tippy-popper.more-language-tips,
    .tippy-popper.logout-tips,
    .tippy-popper.more-operation-tips {
        .tippy-tooltip {
            padding: 4px 0;
            border: 1px solid #dcdee5;
            box-shadow: 0 2px 6px 0 rgba(0,0,0,0.10);
            border-radius: 2px;
        }
        #more-language-html,
        #logout-html,
        #more-operation-html {
            .operate-item {
                display: block;
                height: 32px;
                line-height: 33px;
                padding: 0 16px;
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
        #more-language-html {
            .operate-item {
                padding: 0 14px;
                .bk-icon {
                    font-size: 14px;
                }
                &.active {
                    background-color: #eaf3ff;
                    color: #3a84ff;
                }
            }
        }
    }
</style>
