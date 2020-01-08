/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
import tools from '@/utils/tools.js'

const gatewayShiftX = 210
// 起始位置
const startPointX = 40
const startPointY = 100
// 每一个偏移大小
const shiftX = 152
const toolShiftX = 14
const shiftY = 110
// 偏差高
const deviationY = 15
// 工具栏大小
const toolsWidth = 60
const tabContentWidth = 414
const maxShiftX = 100
// 浏览器宽度 - 工具栏大小 - 全局变量栏大小
const maxWidth = Math.max(document.body.clientWidth - toolsWidth - tabContentWidth - maxShiftX, 1200)
// 起始位置信息
let lastNodeX = 60
let lastNodeY = 100
// 由于网关排序问题，需要记录最大高度
let gatewayShiftY = 0
// 每一行的最大高度数组
const gatewayShiftYList = [0]
// 一一配对网关 如分支网关id -> 汇聚网关id
let gatewayGroup = {}
// 记录当前的网关
const gatewayStack = []
// 网关执行序列
let gatewayCycleList = {}
// 当前节点
let lastPoint = null
// 结束节点
let endPoint = null
// 循环的当前Id
let nowId = null
// 每一个节点的执行序列,分组用于nowId的切换
let group = {}
// 整合所有的除头结点的数据
let newLocations = {}
// 用于判断是否遇到了网关节点
const gatewayFlagList = []
// 用于控制换行时起始位置
let isStartPoint = false
// 最后一个节点类型，用于控制在下一个节点的宽度大小
let lastPointType = 'startpoint'
// 控制网关执行次数
let gatewayCycleExecute = {}
// 新建的节点连线
let lines = null
// 新建节点位置
let locations = []
// 用于重置网关中的Y轴变量
const resetGatewayList = []
// 用于判断上一个节点是否是汇聚网关
let lastLocations = null
// 获取换行的线段line
let overBorderLine = []
// 每一层级的最大宽度 {0：1200}
let convergegatewayMaxWidthTier = {}
// 每一层的最大高度 {0: 1200}
let convergegatewayMaxHeightTier = {}
// 当前层级
let nowTier = -1
// 用于计算线段比例
let nextLineNodeY = 0

const formatPositionUtils = {
    formatPosition (oldLines, oldLocations) {
        lastLocations = oldLocations
        lines = oldLines
        overBorderLine = []
        // 分组信息
        for (const line of lines) {
            const sourceId = line.source.id
            const targetId = line.target.id
            if (group[sourceId]) {
                group[sourceId].push(targetId)
            } else {
                group[sourceId] = [targetId]
            }
        }
        // 循环旧节点
        for (const location of oldLocations) {
            const type = location['type']
            if (type === 'startpoint') {
                // 用于放置至最开始
                lastPoint = location
                nowId = location.id
            } else if (type === 'endpoint') {
                // 用于放置至最后
                endPoint = location
            } else {
                const locationId = location.id
                // 添加进入循环数组
                newLocations[locationId] = location
                // 获取一一对应的网关关系
                if (type === 'parallelgateway' || type === 'branchgateway') {
                    gatewayCycleList[locationId] = {}
                    gatewayCycleExecute[locationId] = {}
                    // 递归获得分支或并行网关执行序列
                    const [gatewayRecursionList] = this.recursionGateway(gatewayStack, locationId, oldLocations)
                    for (const x in gatewayRecursionList) {
                        for (const y in gatewayRecursionList[x]) {
                            const nodeId = gatewayRecursionList[x][y]
                            gatewayCycleList[locationId][nodeId] = oldLocations.find(location => location.id === nodeId)
                        }
                        // 用于控制递归继续执行序列
                        // 需要减去最后的多余的结束节点数量
                        gatewayCycleExecute[locationId][x] = gatewayRecursionList[x].length - 1
                    }
                }
            }
        }
        // 清除多余的locations中的相关节点
        for (const x in gatewayCycleList) {
            for (const y in gatewayCycleList[x]) {
                for (const z in gatewayCycleList[x][y]) {
                    const id = gatewayCycleList[x][y][z]
                    if (newLocations[id] === undefined) {
                        continue
                    }
                    delete newLocations[id]
                }
            }
        }
        // 重新赋值节点位置
        locations = []
        // 先添加起始节点
        const locationJson = tools.deepClone(lastPoint)
        // 绘制开始节点
        locationJson['x'] = startPointX
        locationJson['y'] = startPointY
        locations.push(locationJson)
        // 进行节点循环判断
        this.recursionData(newLocations)
        // 需要判断是否进行换行
        this.isOverBorder()
        // 结束节点最后绘制
        this.computeAndDrawNode(endPoint)
        // 需要重新赋值全局变量 防止第二次点击编排按钮时出现问题
        const result = { 'lines': lines, 'locations': locations, 'overBorderLine': overBorderLine }
        this.initData()
        return result
    },
    /**
     * 找到网关的执行序列
     * @param {*} gatewayStack 网关Id序列
     * @param {*} locationId 当前网关Id
     * @param {*} oldLocations 传递进来的locations信息
     * @param {*} tier 网关的层级
     */
    recursionGateway (gatewayStack, locationId, oldLocations, tier = 0) {
        // 全部分支递归分支数组
        const gatewayRecursionList = []
        // 获取网关的执行序列
        const groupLocationList = group[locationId]
        // 某一条分支的递归数组
        let recursionList = []
        // 当前id
        let findId = null

        for (const locationIndex in groupLocationList) {
            gatewayStack.push(locationId)
            // 获得网关的第一个节点
            findId = groupLocationList[locationIndex]
            while (true) {
                // 获取节点
                const findLocation = oldLocations.find(location => location.id === findId)
                const findType = findLocation['type']
                if (findType === 'convergegateway') {
                    // 继续进行下一条分支 只有最后一次需要执行下面的逻辑
                    if (locationIndex + 1 !== groupLocationList.length) {
                        gatewayGroup[gatewayStack.pop()] = findId
                        recursionList.push(findId)
                        break
                    }
                } else if (findType === 'parallelgateway' || findType === 'branchgateway') {
                    tier++
                    recursionList.push(findId)
                    // 进行递归 获取网关中最后节点
                    const result = this.recursionGateway(gatewayStack, findId, oldLocations, tier)
                    // 需要传递网关最后的节点
                    findId = result[1]
                } else {
                    recursionList.push(findId)
                }
                // 继续找下一个节点
                findId = group[findId][0]
            }
            // 某一条分支
            gatewayRecursionList.push(recursionList)
            recursionList = []
        }
        return [gatewayRecursionList, findId]
    },
    /**
     * 执行节点线路绘制
     * @param {*} newLocations 执行序列
     * @param {*} newLastNodeX 当前x值
     * @param {*} newLastNodeY 当前y值
     */
    recursionData (newLocations, newLastNodeX = null, newLastNodeY = null) {
        // 循环执行节点
        /* eslint-disable */
        for (const i in newLocations) {
        /* eslint-enable */
            // 某个节点的下一个执行序列
            const lastList = group[nowId]
            // 出现undefined或空节点即可结束
            if (lastList === undefined || newLocations[lastList[0]] === undefined) {
                break
            }
            // 上一个Id
            const lastId = nowId
            if (newLastNodeX === null) {
                newLastNodeX = lastNodeX
            }
            if (newLastNodeY === null) {
                newLastNodeY = lastNodeY
            }
            const executeLength = lastList.length
            for (let executeNodeIndex = 0; executeNodeIndex < executeLength; executeNodeIndex++) {
                nowId = lastList[executeNodeIndex]
                let location = newLocations[nowId]
                // 下一个节点为空,不需要继续执行
                if (location === undefined) {
                    break
                }
                // 只是普通的节点
                if (gatewayCycleExecute[lastId] === undefined) {
                    // 绘画之前需要考虑边界问题
                    this.isOverBorder()
                    this.computeAndDrawNode(location, executeLength)
                } else {
                    // 并行或分支网关某一条分支执行序列
                    const gatewayCycleExecuteLength = gatewayCycleExecute[lastId][executeNodeIndex]
                    let copynewLastNodeX = newLastNodeX
                    let copynewLastNodeY = newLastNodeY
                    for (let gatewayIndex = 0; gatewayIndex < gatewayCycleExecuteLength; gatewayIndex++) {
                        if (gatewayIndex === 0 && executeNodeIndex > 0) {
                            // 第二行开始需要计算Y轴高度 上一级一定有高度 网关必然有两层及以上
                            // 还需要减去偏差高
                            copynewLastNodeY = convergegatewayMaxHeightTier[nowTier] + shiftY
                        }
                        const result = this.computeAndDrawNode(location, executeLength, executeNodeIndex, copynewLastNodeX, copynewLastNodeY, gatewayIndex, gatewayCycleExecuteLength)
                        copynewLastNodeX = result[0]
                        if (result[1] !== null) {
                            // Y值不为空
                            copynewLastNodeY = result[1]
                            // 这里做判断
                        }
                        nowId = group[nowId]
                        if (gatewayIndex + 1 === gatewayCycleExecuteLength) {
                            // 连接汇聚网关的每一个节点
                            // 用于获得最大的Y位置 但不用来绘制汇聚网关 （获得下一层的高度，并替换至当前层级高度）
                            const nextTierMaxHeight = convergegatewayMaxHeightTier[nowTier + 1] || 0
                            const nowTierMaxHeight = convergegatewayMaxHeightTier[nowTier] || 0
                            const lastTierMaxHeight = convergegatewayMaxHeightTier[nowTier - 1] || 0
                            const maxNodeY = Math.max(copynewLastNodeY, nextTierMaxHeight, nowTierMaxHeight)
                            if (nextTierMaxHeight) {
                                // 不能直接赋值（存在一个执行序列有两个分支并行网关，但高度不一致，需要取最大的）
                                convergegatewayMaxHeightTier[nowTier] = maxNodeY
                                delete convergegatewayMaxHeightTier[nowTier + 1]
                            } else {
                                convergegatewayMaxHeightTier[nowTier] = copynewLastNodeY + deviationY
                            }
                            if (nowTier !== 0) {
                                convergegatewayMaxHeightTier[nowTier - 1] = Math.max(convergegatewayMaxHeightTier[nowTier], lastTierMaxHeight)
                            }
                            // 用于获得最大的X位置 用来绘制汇聚网关
                            const nextTierMaxWidth = convergegatewayMaxWidthTier[nowTier + 1] || 0
                            const nowTierMaxWidth = convergegatewayMaxWidthTier[nowTier] || 0
                            const maxNodeX = Math.max(copynewLastNodeX, nowTierMaxWidth)
                            if (nextTierMaxWidth) {
                                convergegatewayMaxWidthTier[nowTier] = Math.max(maxNodeX, nextTierMaxWidth)
                            } else {
                                convergegatewayMaxWidthTier[nowTier] = maxNodeX
                            }
                        }
                        // 继续执行序列
                        location = newLocations[nowId]
                    }
                }
                // 绘制汇聚网关
                if (executeNodeIndex + 1 === executeLength && executeNodeIndex > 0) {
                    const location = newLocations[gatewayGroup[lastId]]
                    // 存储层级及最大高度
                    // 获得最大的X位置
                    const nowTierMaxWidth = convergegatewayMaxWidthTier[nowTier]
                    if (nowTierMaxWidth) {
                        convergegatewayMaxWidthTier[nowTier] = nowTierMaxWidth
                    } else {
                        convergegatewayMaxWidthTier[nowTier] = lastNodeX
                    }
                    const [resultNodeX] = this.computeAndDrawNode(location, executeLength, 0, convergegatewayMaxWidthTier[nowTier], newLastNodeY)
                    if (nowTierMaxWidth) {
                        convergegatewayMaxWidthTier[nowTier] = Math.max(resultNodeX, nowTierMaxWidth)
                    } else {
                        convergegatewayMaxWidthTier[nowTier] = resultNodeX
                    }
                    newLastNodeX = convergegatewayMaxWidthTier[nowTier]
                    // 清除网关信号标识
                    gatewayFlagList.pop()
                    nowId = location.id
                    break
                }
            }
        }
        return newLastNodeX
    },
    /**
     *
     * @param {*} location 节点
     * @param {*} executeLength 执行序列长度
     * @param {*} executeNodeIndex 当前节点在执行序列的index
     * @param {*} newLastNodeX 网关中的节点X值
     * @param {*} newLastNodeY 网关中的节点Y值
     * @param {*} gatewayIndex 节点所处网关节点的inex
     * @param {*} gatewayCycleExecuteLength 网关执行序列长度
     */
    computeAndDrawNode (location, executeLength = null, executeNodeIndex = 0, newLastNodeX = null, newLastNodeY = null, gatewayIndex = 0, gatewayCycleExecuteLength = 0) {
        if (location === undefined) {
            // 空节点不需要继续
            return
        }
        // 拷贝一份location用于替换x,y值
        const locationJson = tools.deepClone(location)
        const type = location['type']
        if (type === 'tasknode' || type === 'subflow') {
            // 是否是在网关中的节点
            let gatewayFlag = null
            // 当前是否有网关
            if (gatewayFlagList.length - 1 >= 0) {
                gatewayFlag = gatewayFlagList[gatewayFlagList.length - 1]
            } else {
                gatewayFlag = false
            }
            // 在网关当中
            if (gatewayFlag) {
                const nodeY = newLastNodeY - deviationY
                newLastNodeX += shiftX * 1.2
                locationJson['x'] = newLastNodeX
                locationJson['y'] = nodeY
                locations.push(locationJson)
                gatewayShiftYList.push(nodeY + deviationY)

                const sourceLine = lines.find(line => line.target.id === location.id)
                const targetLine = lines.find(line => line.source.id === location.id)
                // 入线模式尾箭头为左入
                sourceLine.target.arrow = 'Left'
                if (executeNodeIndex === 0) {
                    // 网关的第一个节点
                    sourceLine.source.arrow = 'Right'
                    targetLine.target.arrow = 'Left'
                } else {
                    // 第二个开始汇聚节点应该在最下方
                    if (gatewayIndex === 0) {
                        // 网关第N行（N>2）第一个节点
                        sourceLine.source.arrow = 'Bottom'
                        targetLine.source.arrow = 'Right'
                        if (gatewayCycleExecuteLength === 1) {
                            // 只有一个节点 连线需要接到汇聚网关下方
                            targetLine.target.arrow = 'Bottom'
                        } else {
                            // 其余为右线
                            targetLine.target.arrow = 'Left'
                        }
                    } else {
                        // 左出下入的线
                        sourceLine.source.arrow = 'Right'
                        targetLine.target.arrow = 'Bottom'
                    }
                }
                if (executeNodeIndex + 1 === executeLength) {
                    // 最后一个节点
                    lastNodeX += shiftX / 1.2
                    if (gatewayShiftY < nodeY) {
                        gatewayShiftY = nodeY
                    }
                }
                lastPointType = type
                return [newLastNodeX, null]
            } else {
                // 不在网关中
                // 上一个节点还是tasknode或者subflow节点
                if (lastPointType === 'tasknode' || lastPointType === 'subflow') {
                    lastNodeX += toolShiftX * 6
                }
                // 修改箭头方向
                lines.find(line => line.target.id === location.id).source.arrow = 'Right'
                lines.find(line => line.target.id === location.id).target.arrow = 'Left'

                if (!isStartPoint) {
                    lastNodeX += shiftX / 1.5
                } else {
                    // 换行处理
                    isStartPoint = false
                    lastNodeX = startPointX
                }
                locationJson['x'] = lastNodeX
                // 因为不对齐的问题 需要额外减去一定距离进行对齐
                locationJson['y'] = lastNodeY - deviationY
                locations.push(locationJson)
                lastPointType = type
            }
        } else if (type === 'parallelgateway' || type === 'branchgateway') {
            // 添加网关信号 用于重置Y轴值
            resetGatewayList.push(true)
            // 修改输出的箭头方向
            const targetLine = lines.find(line => line.target.id === location.id)
            targetLine.target.arrow = 'Left'
            if (executeNodeIndex === 0) {
                targetLine.source.arrow = 'Right'
            } else {
                // 上一个节点的type
                const { type: lastNodeType } = this.getPreviousPoint(location.id)
                if (lastNodeType === 'parallelgateway' || lastNodeType === 'branchgateway') {
                    targetLine.source.arrow = 'Bottom'
                } else {
                    targetLine.source.arrow = 'Right'
                }
            }
            if (lastPointType === 'tasknode' || lastPointType === 'subflow') {
                // 分支或并行节点前是个标准插件节点需要增加一半距离
                lastNodeX += shiftX / 2
            }
            lastPointType = type
            // 当前的Y值
            let nodeY = null

            // 网关节点标记位，用于排列后续标准插件节点
            gatewayFlagList.push(true)
            // 是否是嵌套网关的网关，需要高度切换
            let gatewayFlag = null
            if (gatewayFlagList.length - 1 >= 0) {
                // 获得上一个分支网关
                gatewayFlag = gatewayFlagList[gatewayFlagList.length - 1]
            } else {
                gatewayFlag = false
            }

            if (gatewayFlag && gatewayFlagList.length !== 1) {
                // 需要加回偏差高
                nodeY = newLastNodeY
            } else {
                nodeY = lastNodeY
            }
            let nowTierMaxWidth = convergegatewayMaxWidthTier[nowTier]
            // 增加层级
            nowTier++
            if (newLastNodeX !== null) {
                if (isStartPoint) {
                    // 换行的第一个直接置为起始节点
                    locationJson['x'] = newLastNodeX
                    newLastNodeX = lastNodeX
                    isStartPoint = false
                    const line = lines.find(line => line.target.id === location.id)
                    this.addOverBorderLine({ 'source': line.source.id, 'target': line.target.id })
                } else {
                    newLastNodeX += shiftX * 1.5
                    locationJson['x'] = newLastNodeX
                }
                locationJson['y'] = nodeY
                locations.push(locationJson)
                // 增加当前节点的高度
                // 进行需要携带 x,y信息进行递归分支节点
                lastNodeX = this.recursionData(gatewayCycleList[nowId], newLastNodeX, nodeY)
            } else {
                if (isStartPoint) {
                    // 换行的第一个直接置为起始节点
                    locationJson['x'] = lastNodeX
                    isStartPoint = false
                    const line = lines.find(line => line.target.id === location.id)
                    this.addOverBorderLine({ 'source': line.source.id, 'target': line.target.id })
                } else {
                    lastNodeX += shiftX / 1.2
                    locationJson['x'] = lastNodeX
                }
                locationJson['y'] = lastNodeY
                locations.push(locationJson)
                // 增加当前节点的高度
                // 进行递归分支节点
                this.recursionData(gatewayCycleList[nowId])
            }
            // 删除当前层级内容，并转移至上一级
            const lastTierMaxWidth = convergegatewayMaxWidthTier[nowTier - 1]
            nowTierMaxWidth = convergegatewayMaxWidthTier[nowTier]
            if (convergegatewayMaxWidthTier[nowTier - 1]) {
                convergegatewayMaxWidthTier[nowTier - 1] = Math.max(lastTierMaxWidth, nowTierMaxWidth)
            } else {
                convergegatewayMaxWidthTier[nowTier - 1] = nowTierMaxWidth
            }
            if (nowTier === 0) {
                lastNodeX = nowTierMaxWidth
            }
            delete convergegatewayMaxWidthTier[nowTier]
            nowTier--
            return [lastNodeX, null]
        } else if (type === 'convergegateway') {
            resetGatewayList.pop()
            // 更换分支网关连接线段箭头
            const sourceLine = lines.find(line => line.target.id === location.id)
            const targetLine = lines.find(line => line.source.id === location.id)
            targetLine.source.arrow = 'Right'
            if (lastLocations.find(location => sourceLine.source.id === location.id).type === 'convergegateway') {
                // 设置连接分支网关的线在左部
                sourceLine.target.arrow = 'Left'
            }

            if (newLastNodeX !== null) {
                // 在嵌套网关循环中
                newLastNodeX += gatewayShiftX * 1.3
                locationJson['x'] = newLastNodeX
                locationJson['y'] = newLastNodeY
            } else {
                // 不在嵌套循环
                lastNodeX += gatewayShiftX * 1.3
                locationJson['x'] = lastNodeX
                locationJson['y'] = lastNodeY
            }
            locations.push(locationJson)
            lastPointType = type
            if (newLastNodeX !== null) {
                return [newLastNodeX, newLastNodeY]
            } else {
                return [lastNodeX, lastNodeY]
            }
        } else if (type === 'endpoint') {
            // 需要切换箭头
            const line = lines.find(line => line.target.id === location.id)
            line.target.arrow = 'Left'
            line.source.arrow = 'Right'
            if (isStartPoint) {
                lastNodeX = startPointX
                isStartPoint = false
                const line = lines.find(line => line.target.id === location.id)
                this.addOverBorderLine({ 'source': line.source.id, 'target': line.target.id })
            } else if (lastPointType === 'tasknode' || lastPointType === 'subflow' || lastPointType === 'startpoint') {
                // 结束节点前是个标准插件节点需要增加1.5倍距离
                lastNodeX += shiftX * 1.5
            } else if (lastPointType === 'convergegateway') {
                // 结束网关之前是个并行网关只需要增加一倍距离
                lastNodeX += shiftX
            }
            locationJson['x'] = lastNodeX
            locationJson['y'] = lastNodeY
            locations.push(locationJson)
        }
    },
    isOverBorder () {
        if (lastNodeX + shiftX * 1.5 > maxWidth) {
            // 超出最大边距，重新置为起始位置
            lastNodeX = startPointX
            // 某一行的最大高度
            if (gatewayShiftY === 0) {
                gatewayShiftY = shiftY
            }
            // 分支网关中的最大高度
            const newgatewayShiftY = Math.max(...gatewayShiftYList)
            if (gatewayShiftY < newgatewayShiftY) {
                gatewayShiftY = newgatewayShiftY
            }
            // 计算第二行起的高度
            if (newgatewayShiftY !== 0) {
                nextLineNodeY = (gatewayShiftY + shiftY) * 1
                if (lastNodeY < nextLineNodeY) {
                    lastNodeY += nextLineNodeY
                }
            } else {
                lastNodeY += gatewayShiftY * 1.5
            }
            // 标志第二行开始
            isStartPoint = true
            // X轴值节点位置设置为空
            gatewayShiftYList.splice(0, gatewayShiftYList.length)
            gatewayShiftYList.push(0)
            gatewayShiftY = 0
        }
    },
    // 初始化信息
    initData () {
        group = {}
        lastPoint = null
        lastNodeX = 60
        lastNodeY = 100
        lastPointType = 'startpoint'
        gatewayShiftY = 0
        gatewayShiftYList.splice(0, gatewayShiftYList.length)
        gatewayShiftYList.push(0)
        gatewayFlagList.splice(0, gatewayFlagList.length)
        gatewayStack.splice(0, gatewayStack.length)
        resetGatewayList.splice(0, resetGatewayList.length)
        isStartPoint = false
        gatewayCycleList = {}
        newLocations = {}
        gatewayGroup = {}
        gatewayCycleExecute = {}
        convergegatewayMaxWidthTier = {}
        convergegatewayMaxHeightTier = {}
        nowTier = -1
    },
    // 获取当前节点的下一个节点
    getNextPoint (id) {
        const nextPointId = lines.find(line => line.source.id === id).target.id
        return locations.find(location => location.id === nextPointId)
    },
    // 获取上一个节点
    getPreviousPoint (id) {
        const previousPointId = lines.find(line => line.target.id === id).source.id
        return locations.find(location => location.id === previousPointId)
    },
    isLocationAllNode (locations) {
        const typeList = ['startpoint', 'endpoint', 'tasknode', 'subflow']
        return locations.every((location) => {
            return typeList.includes(location.type)
        })
    },
    addOverBorderLine ({ source, target }) {
        overBorderLine.push({ 'source': source, 'target': target, 'midpoint': Number(gatewayShiftY / nextLineNodeY).toFixed(2) })
        gatewayShiftY = 0
    }
}

export default formatPositionUtils
