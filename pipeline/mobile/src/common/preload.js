import store from '@/store'

const config = {
    fromCache: false,
    cancelWhenRouteChange: false
}

/**
 * 获取 user 信息
 *
 * @return {Promise} promise 对象
 */
function getUser () {
    return store.dispatch('userInfo', config)
}

export default function () {
    return Promise.all([
        getUser()
    ])
}
