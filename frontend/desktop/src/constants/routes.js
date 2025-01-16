import i18n from '@/config/i18n/index.js'

const COMMON_ROUTE_LIST = [
    [
        {
            id: 'home',
            name: i18n.t('首页'),
            icon: 'icon-home-shape',
            url: '/home/'
        },
        {
            id: 'processHome',
            name: i18n.t('流程'),
            icon: 'icon-sitemap-shape',
            hasProjectId: true,
            subRoutes: ['processHome', 'processCommon', 'processCollect', 'templatePanel', 'projectCommonTemplatePanel'],
            url: '/template/home/'
        },
        {
            id: 'taskList',
            name: i18n.t('任务记录'),
            icon: 'common-icon-task-record',
            hasProjectId: true,
            subRoutes: ['taskExecute'],
            url: '/taskflow/home/list/'
        },
        {
            id: 'periodicTemplate',
            name: i18n.t('周期任务'),
            icon: 'common-icon-cycle-task',
            hasProjectId: true,
            url: '/taskflow/home/periodic/'
        },
        {
            id: 'clockedTemplate',
            name: i18n.t('计划任务'),
            icon: 'common-icon-clocked-task',
            hasProjectId: true,
            url: '/taskflow/home/clocked/'
        },
        {
            id: 'appMakerList',
            name: i18n.t('轻应用'),
            icon: 'icon-apps-shape',
            hasProjectId: true,
            url: '/appmaker/home/'
        }
    ],
    [
        {
            id: 'functionHome',
            name: i18n.t('职能化'),
            icon: 'icon-project',
            subRoutes: ['functionTemplateStep', 'functionTaskExecute'],
            url: '/function/home/'
        },
        {
            id: 'projectHome',
            name: i18n.t('项目管理'),
            icon: 'icon-work-manage',
            subRoutes: ['projectConfig'],
            url: '/project/home/'
        },
        {
            id: 'auditHome',
            name: i18n.t('审计中心'),
            icon: 'icon-order-shape',
            url: '/audit/home/'
        },
        {
            id: 'commonProcessList',
            name: i18n.t('公共流程管理'),
            icon: 'icon-execute',
            subRoutes: ['commonTemplatePanel'],
            url: '/common/home/'
        }
    ]
]
const ADMIN_ROUTE_LIST = [
    [
        {
            id: 'admin',
            name: i18n.t('管理员入口'),
            icon: 'icon-user-shape',
            children: [
                {
                    id: 'manage',
                    name: i18n.t('后台管理'),
                    subRoutes: ['adminSearch', 'adminPeriodic', 'adminClocked', 'sourceManage', 'packageEdit', 'cacheEdit', 'sourceSync'],
                    url: '/admin/manage/search/'
                },
                {
                    id: 'operation',
                    name: i18n.t('运营数据'),
                    subRoutes: ['statisticsTemplate', 'statisticsInstance', 'statisticsAtom', 'statisticsAppmaker'],
                    url: '/admin/statistics/template/'
                },
                {
                    id: 'atomDev',
                    name: i18n.t('插件开发'),
                    url: '/admin/atomdev/'
                }
            ]
        }
    ]
]

const APPMAKER_ROUTE_LIST = [
    [
        {
            id: 'appmakerTaskCreate',
            name: i18n.t('新建任务'),
            icon: 'icon-apps-shape'
        },
        {
            id: 'appmakerTaskHome',
            name: i18n.t('任务记录'),
            icon: 'icon-calendar-shape',
            subRoutes: ['appmakerTaskExecute']
        }
    ]
]

export { COMMON_ROUTE_LIST, ADMIN_ROUTE_LIST, APPMAKER_ROUTE_LIST }
