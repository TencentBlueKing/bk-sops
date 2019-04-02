import chalk from 'chalk'

export async function response(getArgs, postArgs, req) {
    console.log(chalk.cyan('req', req.method))
    console.log(chalk.cyan('getArgs', JSON.stringify(getArgs, null, 0)))
    console.log(chalk.cyan('postArgs', JSON.stringify(postArgs, null, 0)))
    console.log()
    const invoke = getArgs.invoke
    if (invoke === 'userInfo') {
        return {
            code: 0,
            data: {
                test: 'succuess'
            },
            message: 'ok'
        }
    }
    return {
        code: 0,
        data: {}
    }
}
