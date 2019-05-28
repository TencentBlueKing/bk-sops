import artTemplate from './template-web.js'
import './jsplumb.min.js'
import '../css/jsPlumbToolkit-defaults.css'
import '../css/bkflow.scss'

(function ($, artTemplate) {
    $.fn.extend({
        dataflow: function (options) {
            // jQuery对象
            var _self = this

            // 默认配置
            var defaults = {
                canvas: null,  //画布
                template: null,  //可配置的模版
                tools: null,  // 流程拖动源
                selector: {
                    el: null,
                    x: 0, // 矩形框中心点画布 x 坐标
                    y: 0, // 矩形框中心点画布 y 坐标
                    nodes: []
                }, // 节点选择框
                locationConfig: {},  // 节点的类型和端点的位置
                lineWidth: 3,  // 线的宽度 默认为2
                fillColor: 'red',  // 高亮颜色
                defaultColor: '#ddd',  //默认颜色
                lineRadius: 1, // 线拐弯弧度
                pointColor: 'rgba(0,0,0,0.5)',  // 端点的颜色
                pointWidth: 5,  // 连接端点的半径
                pointDistance: 0,  // 端点与线的距离
                data: {
                    locations: [],
                    lines: []
                },  // 渲染的数据源
                id: 'chart',  // 配置渲染的节点id
                isEdit: true,  // 是否编辑
                dragSelection: false, // 是否支持框选节点
                dropElevent: null,  // 拖拽的数据源

                getDefaultLocation: null,  // 获取某一类型节点的初始化节点数据

                onCreateLocationBefore: null,  // 节点创建前回调
                onCreateLocationAfter: null,  // 节点创建后回调
                onRemoveLocationBefore: null,  // 删除节点前回调
                onRemoveLocationAfter: null,  // 删除节点后回调
                onLocationMoveAfter: null,  // 拖动节点时回调
                onLocationMove: null,  // 拖动节点停止后回调

                onCreateLineBefore: null,  // 创建连线前回调
                onCreateLineAfter: null,  // 创建连线后回调
                onRemoveLineBefore: null,  // 删除连线前的回调
                onRemoveLineAfter: null,  // 删除连线后的回调

                ondrawData: null,  // 渲染流程后回调

                onLineDragStop: null, // 节点端点拖拽连线结束回调
                onLabelBlur: null, // 连接线label失焦回调
                onCloseDragSelection: null // 关闭节点框选回调
            }

            // 最终配置，包括组装连线配置
            var opts = $.extend({}, defaults, options)
            opts.sourceEndpoint = {
                endpoint: 'Dot',
                paintStyle: { //出发点
                    stroke: opts.isEdit ? opts.pointColor : 'rgba(0, 0, 0, 0)',
                    fill: 'rgba(0, 0, 0, 0)',
                    radius: 7,
                },
                hoverPaintStyle: {
                    stroke: opts.isEdit ? opts.fillColor : 'rgba(0, 0, 0, 0)',
                    fill: opts.isEdit ? opts.fillColor : 'rgba(0, 0, 0, 0)',
                    radius: 7
                },
                isSource: true,
                isTarget: true,
                connector: [
                    'Flowchart',
                    {
                        stub: [5, 20],
                        gap: 8,
                        cornerRadius: opts.lineRadius,
                        alwaysRespectStubs: true
                    }
                ], //gap 线离开端点距离
                connectorStyle: { //描绘线的样式
                    strokeWidth: 2, // 线条宽度
                    stroke: opts.defaultColor, //填充颜色
                    joinstyle: 'round',
                    outlineStroke: 'transparent',
                    outlineWidth: 0 //线条外部宽度
                },
                connectorHoverStyle: {
                    strokeWidth: 2,
                    stroke: opts.isEdit ? opts.fillColor : opts.defaultColor,
                    fill: opts.isEdit ? opts.fillColor : opts.defaultColor
                },
                dragOptions: {
                    drag: function (e) { // 拖动端点触发的事件
                        $(e.el).find('circle').css('fill', '#fe621d')
                    }
                },
                maxConnections: -1 //是否允许多条线
            }
            opts.targetEndpoint = {
                endpoint: 'Dot',
                paintStyle: {
                    stroke: opts.isEdit ? opts.fillColor : 'rgba(0, 0, 0, 0)',
                    fill: 'rgba(0, 0, 0, 0)',
                    radius: 7
                },
                hoverPaintStyle: {
                    stroke: opts.isEdit ? opts.fillColor : 'rgba(0, 0, 0, 0)',
                    fill: opts.isEdit ? opts.fillColor : 'rgba(0, 0, 0, 0)',
                    radius: 7
                },
                connectorHoverStyle: {
                    strokeWidth: 4,
                    stroke: opts.isEdit ? opts.fillColor : opts.defaultColor
                },
                dragOptions: {
                    drag: function (e) {
                        $(e.el).find('circle').css('fill', '#fe621d')
                    }
                },
                connectorStyle: { //描绘线的样式
                    strokeWidth: 2, // 线条宽度
                    stroke: opts.defaultColor, //填充颜色
                    joinstyle: 'round',
                    outlineStroke: 'transparent',
                    outlineWidth: 0 //线条外部宽度
                },
                maxConnections: -1,
                isSource: true,
                isTarget: true,
                connector: [
                    'Flowchart',
                    {
                        stub: [5, 20],
                        gap: 3,
                        cornerRadius: opts.lineRadius,
                        alwaysRespectStubs: true
                    }
                ]
            }

            // 区分拖拽和单击事件的状态变量
            var nodeClickStatus = {
                pageX: undefined,
                pageY: undefined,
                isDragEvent: undefined
            }
            // 工具函数集合
            var handlerFactory = {
                initHtml: function (html, data) {
                    // 目前仅支持 art-template 原生模板渲染
                    var render = artTemplate.compile(html)
                    var ret = {
                        id: '#' + data.id,
                        str: render(data)
                    }
                    return ret
                },
                /**
                 * @description 
                */
                generateNodeId: function () {
                    var d = new Date().getTime()
                    function uuid () {
                        function s4 () {
                            return Math.floor((1 + Math.random()) * 0x10000)
                                .toString(16)
                                .substring(1)
                        }
                        return s4() + s4() + s4() + s4() + s4() + s4() + s4()
                    }
                    let newNodeId = `${options.id}${uuid()}`
                    if (document.getElementById(newNodeId)) {
                        this.generateNodeId()
                    }
                    return newNodeId
                },
                getName: function (obj) { //获取流程的名字
                    var name = $(obj).attr('data')
                    return name
                },
                /**
                 * 获取默认节点结构，补充必要字段
                 */
                getDefaultLocation: function (type) {
                    let defaultLocation = {}
                    if (opts.getDefaultLocation) {
                        defaultLocation = opts.getDefaultLocation(type)
                    }

                    defaultLocation.id = this.generateNodeId()
                    defaultLocation.x = 0
                    defaultLocation.y = 0
                    defaultLocation.type = type
                    return defaultLocation
                },
                /**
                 * 根据节点类型获取节点模板
                 * @param {String} dataType 节点类型
                 * @param {String} [opType] 节点操作方式，create（新增）、update（更新）
                 */
                getLocationTemplate: function (dataType) {
                    return $(opts.template).find('#' + dataType + '-template').html()
                },
            }

            // 画布内所有节点的容器，用于控制位移和缩放
            var $nodeContainer = {
                el: null, // 容器Dom
                left: 0, // 容器位移
                top: 0,
                zoom: 1 // 画布容器整体缩放值
            }

            // jsPlumb插件实例
            var instance = jsPlumb.getInstance({
                ConnectionOverlays: [ //配置链接线的样式
                    ['PlainArrow', {
                        location: 1, // 0-1
                        width: 8,
                        id: 'arrow',
                        length: 6,
                        events: { //终线箭头的点击事件
                            click: function (e) {
                                e.stopPropagation()
                            }
                        }
                    }],
                    ['Label', 
                        { label: '<i class="common-icon-dark-circle-close"></i>', id: 'label' }
                    ]
                ],
                Container: 'ktj-canvas' //容器id
            })
            jsPlumb.fire("jsPlumbDemoLoaded", instance)

            // flow插件初始化
            var init = function () {
                jsPlumb.setContainer(opts.canvas)

                // 将所有节点包裹在内置的DIV
                $(opts.canvas).append('<div class="bk-flow-container"></div>')
                $nodeContainer.el = $(opts.canvas).find('.bk-flow-container')

                // 加入基础样式class
                $(opts.tools).addClass('bk-flow-tool')
                _self.addClass('bk-flow-wrap')
                $(opts.canvas).addClass('bk-flow-canvas')

                _initDragging()
                _initEvent()

                if (Object.keys(opts.data).length > 0) {
                    _drawData(opts.data)
                }
            }

            /**
             * 初始化画布，统一管理画布之上的所有拖拽功能
             */
            var _initDragging = function () {
                var isMove = false
                var _obj = null         // 是否按下就放开
                var currentNode = null  // 当前选中拖动的对象

                var isCvsDragging = false // 当前操作是否是画布拖拽
                var initialLocation = {
                    x: 0,
                    y: 0
                }
                var mousePos = { // 鼠标位置相对于画布坐标
                    x: 0,
                    y: 0
                }

                _self
                    .off('mousedown')
                    .off('mousemove')
                    .off('mouseup')
                setMouseMoveEvent()

                // 设置鼠标移动事件，记录鼠标坐标
                function setMouseMoveEvent () {
                    _self.on('mousemove', opts.canvas, function (e) {
                        const canvasWrapperOffset = $(opts.canvas).offset()
                        mousePos = {
                            x: e.pageX - canvasWrapperOffset.left - $nodeContainer.left,
                            y: e.pageY - canvasWrapperOffset.top - $nodeContainer.top
                        }
                    })
                }
                
                // 画布拖拽、节点框选事件
                _self.on('mousedown', opts.canvas, canvasDragHanlder)

                function canvasDragHanlder (e) {
                    const canvasWrapperOffset = $(opts.canvas).offset() // 画布最外层元素相对于文档的偏移量
                    const posLeft = e.pageX - canvasWrapperOffset.left - $nodeContainer.left
                    const posTop = e.pageY - canvasWrapperOffset.top - $nodeContainer.top
                    initialLocation.x = e.pageX
                    initialLocation.y = e.pageY

                    if (opts.dragSelection) {
                        const selectWrapper = document.createElement('div')
                        selectWrapper.className = 'select-wrapper'
                        _self.find('.bk-flow-container').append(selectWrapper)
                        opts.selector.el = $(selectWrapper)
                        opts.selector.el.css({
                            left: posLeft,
                            top: posTop
                        })
                    }
                    _self.on('mousemove', opts.canvas, function (event) {
                        if (opts.dragSelection) {
                            selectionMoveHanlder(event, posLeft, posTop)
                        } else {
                            canvasMoveHandler(event)
                        }
                    })
                    $(document).one('mouseup', function (event) {
                        if (opts.dragSelection) {
                            selectionEndHandler(event)
                        } else {
                            canvasMoveEndHandler(event)
                        }
                        _self.off('mousemove', opts.canvas)
                        setMouseMoveEvent()
                    })
                }

                /**
                 * 画布移动事件回调
                 * @param {Object} e 事件对象
                 */
                function canvasMoveHandler (e) {
                    var distanceOnX = e.pageX - initialLocation.x + $nodeContainer.left
                    var distanceOnY = e.pageY - initialLocation.y + $nodeContainer.top
                    $nodeContainer.el.css({
                        left: distanceOnX,
                        top: distanceOnY
                    })
                }

                /**
                 * 画布移动结束事件回调
                 * @param {Object} e 事件对象
                 */
                function canvasMoveEndHandler (e) {
                    // 拖拽结束更新画布的位移值
                    $nodeContainer.left += e.pageX - initialLocation.x
                    $nodeContainer.top += e.pageY - initialLocation.y
                }

                /**
                 * 节点选择事件回调
                 * @param {Object} e 事件对象
                 * @param {Number} posLeft 选框相对于画布左偏移量
                 * @param {Number} posTop 选框相对于画布顶部偏移量
                 */
                function selectionMoveHanlder (e, posLeft, posTop) {
                    const distanceX = e.pageX - initialLocation.x
                    const distanceY = e.pageY - initialLocation.y
                    posLeft = distanceX > 0 ? posLeft : posLeft + distanceX
                    posTop = distanceY > 0 ? posTop : posTop + distanceY
                    opts.selector.el.css({
                        width: Math.abs(distanceX),
                        height: Math.abs(distanceY),
                        left: posLeft,
                        top: posTop
                    })
                    opts.selector.x = (posLeft + Math.abs(distanceX)) / 2
                    opts.selector.y = (posTop + Math.abs(distanceY)) / 2
                }

                /**
                 * 节点选择结束回调
                 * @param {Object} e 事件对象
                 */
                function selectionEndHandler (e) {
                    const locations = _self.find('.bk-flow-location')
                    
                    locations.each((index, node) => {
                        const $node = $(node)
                        if (opts.selector.el && isNodeInSelectionArea($node)) { // 暂时兼容鼠标在画布外释放
                            opts.selector.nodes.push(node)
                            $node.addClass('selected')
                        }
                    })
                    instance.addToDragSelection(opts.selector.nodes) // 多节点拖拽
                    
                    $(document).on('keydown', locationLineCopyHandler) // 节点、连线复制事件
                    $(document).on('keydown', locationLinePasteHandler) // 节点、连线粘贴事件
                    $(document).on('keydown', locationLineDeleteHandler) // 节点、连线删除事件
                    $(document).one('mousedown', function (event) { // 画布失焦
                        const $this = $(event.target)
                        if (!$this.hasClass('bk-flow-location')) {
                            clearSelector()
                        }
                    })
                    $('.bk-flow-location').one('mousedown', function (event) {
                        if (!$(this).hasClass('selected')) {
                            clearSelector()
                        }
                    })
                    opts.dragSelection = false // 关闭可拖拽状态
                    opts.onCloseDragSelection && opts.onCloseDragSelection()
                    _self.find('.select-wrapper').remove()
                }

                /**
                 * 清除选框及数据
                 */
                function clearSelector () {
                    _self.find('.bk-flow-location.selected').removeClass('selected')
                    $(document).off('keydown', locationLineCopyHandler)
                    $(document).off('keydown', locationLinePasteHandler)
                    $(document).off('keydown', locationLineDeleteHandler)
                    opts.selector.el = null
                    opts.selector.nodes = []
                    instance.clearDragSelection()
                }

                /**
                 * 判断节点是否在选择框里
                 * @param {Object} node 画布中所有节点集合
                 * @return {Boolean} 节点是否在选择框里
                 */
                function isNodeInSelectionArea ($node) {
                    const $selector = opts.selector.el
                    const selectorPos = $selector.position()
                    const nodePos = $node.position()
                    return selectorPos.left < nodePos.left &&
                            selectorPos.left + $selector.width() > nodePos.left &&
                            selectorPos.top < nodePos.top &&
                            selectorPos.top + $selector.height() > nodePos.top
                }

                /**
                 * 节点、连线复制回调
                 */
                function locationLineCopyHandler (e) {
                    if ((e.ctrlKey || e.metaKey) && e.keyCode === 67) {
                        const selectedLocationId = opts.selector.nodes.map(item => item.id)
                        opts.onCopyElement && opts.onCopyElement(selectedLocationId, opts.selector)
                    }
                }

                /**
                 * 节点、连线粘贴回调
                 */
                function locationLinePasteHandler (e) {
                    if ((e.ctrlKey || e.metaKey) && e.keyCode === 86) {
                        const offsetX = mousePos.x - opts.selector.x
                        const offsetY = mousePos.y - opts.selector.y
                        instance.clearDragSelection()
                        _self.find('.bk-flow-location.selected').removeClass('selected')
                        if (opts.onPasteElement) {
                            const locations = opts.onPasteElement(offsetX, offsetY)
                            const locationIds = []
                            locations.forEach(location => {
                                $('#' + location.id).addClass('selected')
                                locationIds.push(location.id)
                            })
                            instance.addToDragSelection(locationIds)
                        }
                    }
                }

                /**
                 * 节点、连线删除回调
                 */
                function locationLineDeleteHandler (e) {
                    if (e.keyCode === 46 || e.keyCode === 8) {
                        const selectedLocationId = opts.selector.nodes.map(item => item.id)
                        opts.onDeleteElement && opts.onDeleteElement(selectedLocationId)
                    }
                }

                // 工具栏节点添加事件
                _self.on('mousedown', opts.tools, toolsDragHandler)

                /**
                 * 工具栏节点鼠标点击按下事件回调
                 * @param {Object} e 事件对象
                 */
                function toolsDragHandler (e) {
                    var __this = $(this)

                    if (!opts.isEdit) {
                        return false
                    }

                    var type = __this.attr('data-type')
                    var _html = handlerFactory.getLocationTemplate(type, 'update')
                    var _loc = handlerFactory.getDefaultLocation(type)
                    var atomId = __this.attr('data-atomid')
                    var atomVersion = __this.attr('data-version')
                    var atomName = __this.attr('data-atomname')
                    _loc.atomId = atomId
                    _loc.atomVersion = atomVersion
                    atomName && (_loc.name = atomName)
                    if (type !== 'tasknode' && type !== 'subflow') {
                        _loc.name = ''
                    }
                    var _mouseDom = `
                        <div class="bk-flow-location" id="${_loc.id}" data-type="${_loc.type}">
                            ${handlerFactory.initHtml(_html, _loc).str}
                        </div>
                    `

                    // 将鼠标拖动节点，存在于 body 一级子节点
                    $('body').append(_mouseDom)
                    var top = $('body').scrollTop()
                    var x = e.pageX + 10
                    var y = e.pageY + 10
                    currentNode = $('body >.bk-flow-location')
                    // 把生成的数据绑定在DOM上
                    currentNode.data('raw', _loc)
                    $(currentNode).css({
                        left: x,
                        top: y,
                        position: 'fixed',
                        opacity: '0.7',
                        'z-index': 9999
                    })
                    isMove = true

                    _self.on('mousemove', toolsMoveHandler)
                    _self.one('mouseup', toolsMoveEndHandler)
                    return false
                }

                /**
                 * 工具栏节点点击拖拽事件回调
                 * @param {Object} e 事件对象
                 */
                function toolsMoveHandler (e) {
                    if (isMove) {
                        var top = $('body').scrollTop()
                        _obj = $('body >.bk-flow-location').length
                        $(currentNode).css({
                            left: e.pageX + 10,
                            top: e.pageY + 10 - top
                        })
                    }
                }

                /**
                 * 工具栏节点拖拽结束事件回调
                 * @param {Object} e 事件对象
                 */
                function toolsMoveEndHandler (e) {
                    if (isMove && _obj && opts.isEdit) {
                        var canvas = $(opts.canvas)
                        var scroll_top = canvas.scrollTop() // 画布纵向滚动高度
                        var scroll_left = canvas.scrollLeft() // 画布横向滚动高度
                        var w = parseInt(canvas.width())
                        var h = parseInt(canvas.height())
                        var left = canvas.offset().left
                        var top = canvas.offset().top
                        // 拖动不符合预期（不在画布内）的节点，直接删除，流程结束
                        var _x = e.pageX - (left + scroll_left)
                        var _y = e.pageY - (top + scroll_top)
                        if (_x < 0 || _x > w || _y < 0 || _y > h) {
                            $('body >.bk-flow-location').remove('*')
                            return false
                        }
                        // 拖动符合预期（在画布内）的节点，插入画布，设置正确位置，清除拖动节点
                        var loc = currentNode.data('raw')
                        loc.x = e.pageX + 10 - left + scroll_left - $nodeContainer.left
                        loc.y = e.pageY + 10 - top + scroll_top - $nodeContainer.top
                        _createLocation(loc)

                        $('body >.bk-flow-location').remove('*')
                    } else {
                        $('body >.bk-flow-location').remove('*')
                    }
                    isMove = false
                    _self.off('mousemove')
                }

                $(opts.canvas).on('mouseup', '.bk-flow-location', function (e) {
                    if (opts.onLocationMoveAfter) {
                        const selectedNodes = _self.find('.bk-flow-location.selected')
                        if (selectedNodes.length) {
                            selectedNodes.each((index, item) => {
                                opts.onLocationMoveAfter(_getLocationById($(item).attr('id')))
                            })
                        } else {
                            opts.onLocationMoveAfter(_getLocationById(this.id))
                        }
                    }
                })
                $(opts.canvas).on('click', '.bk-flow-location', function (e) {
                    e.stopPropagation()
                    if (nodeClickStatus.isDragEvent) {
                        nodeClickStatus.isDragEvent = false
                        return
                    } else {
                        const id = $(this).attr('id')
                        opts.onNodeClick && opts.onNodeClick (id)
                    }
                }).on('click', '.branch-condition', function (e) {
                    e.stopPropagation()
                    if (opts.isEdit) {
                        const $this = $(e.target)
                        $this.focus()
                        $this.one('blur', function (e) {
                            const labelData = {
                                id: $this.data('lineid'),
                                nodeId: $this.data('nodeid'),
                                name: $this.text()
                            }
                            opts.onLabelBlur && opts.onLabelBlur(labelData) 
                        })
                    }
                })
            }

            /**
             *  绑定事件
             */
            var _initEvent = function () {
                // var target = '[id^="' + opts.id + '"] .node-wrapper'
                // $(opts.canvas).on('dblclick', target, function (e) {
                //     opts.onDblClick && opts.onDblClick(this)
                //     e.stopPropagation()
                // })

                instance.unbind('connectionDragStop')
                instance.unbind('connectionDrag')
                instance.unbind('click')

                // 拖动连线结束时触发
                instance.bind('connectionDragStop', function (connection, originalEvent) {
                    // 连线不可连接至自身
                    if (connection.sourceId == connection.targetId) {
                        instance.detach(connection)
                        return false
                    }

                    let _line = _connection_to_line(connection)

                    if ((opts.onLineDragStop && !opts.onLineDragStop(_line, originalEvent, connection)) ||
                        (opts.onCreateLineBefore && !opts.onCreateLineBefore(_line))
                    ) {
                        instance.detach(connection)
                        return false
                    }

                    opts.onCreateLineAfter && opts.onCreateLineAfter(_line)
                })
                instance.bind('connectionDrag', function (conn) { //拖动线前触发
                    if (!opts.isEdit) {
                        instance.detach(conn)
                        return false
                    }
                })

                instance.bind('click', function (conn, originalEvent) {
                    if (!opts.isEdit) {
                        return false
                    }
                    if ($(originalEvent.target).hasClass('common-icon-dark-circle-close')) {
                        _deleteLine(conn.sourceId, conn.targetId)
                    }
                })
                instance.bind('mousemove', function (conn, originalEvent) {
                    if (!opts.isEdit) {
                        return false
                    }
                })
            }

            var _connection_to_line = function (conn) {
                let endPoints = conn.endpoints
                return {
                    source: {
                        arrow: endPoints[0].anchor.type,
                        id: conn.sourceId
                    },
                    target: {
                        arrow: endPoints[1].anchor.type,
                        id: conn.targetId
                    }
                }
            }

            /**
             * 初始化流程节点连线, 绑定事件
             */
            var _drawData = function (data) {
                instance.batch(function () {
                    if (data && Object.keys(data).length > 0) {
                        var template = $(opts.template)

                        // 初始化节点列表
                        for (var s = 0; s < data.locations.length; s++) {
                            _createLocation(data.locations[s])
                        }

                        // 初始化连线
                        for (var s = 0; s < data.lines.length; s++) {
                            _createLine(data.lines[s])
                        }
                    }

                    opts.ondrawData && opts.ondrawData()
                })
            }

            /**
             * 绑定节点 hover 高亮事件
             */
            var _highLight = function (obj) {
                $(obj).off()
                $(obj).on('mouseenter', function (e) {
                    var id = $(this).attr('id')
                    var lines = _getConnectionsByNodeId(id)
                    var endPoints = instance.getEndpoints(id)
                    var hglObj = lines.concat(lines, endPoints)
                    hglObj.forEach(function (item) {
                        item.setPaintStyle({
                            stroke: opts.fillColor,
                            fill: opts.fillColor
                        })
                    })

                }).on('mouseleave', function (e) {
                    var id = $(this).attr('id')
                    var lines = _getConnectionsByNodeId(id)
                    var endPoints = instance.getEndpoints(id)
                    lines.forEach(function (item) {
                        item.setPaintStyle({
                            stroke: opts.defaultColor,
                            fill: opts.defaultColor,
                            strokeWidth: 2
                        })
                    })
                    endPoints.forEach(function (item) {
                        item.setPaintStyle({
                            stroke: opts.pointColor,
                            fill: 'rgba(0, 0, 0, 0)'
                        })
                    })
                })
            }

            var _disabledEdit = function () {
                opts.isEdit = false

                el = document.querySelectorAll(opts.canvas + ' .bk-flow-location')
                instance.setDraggable(el, false)
            }

            var _enableEdit = function () {
                opts.isEdit = true

                el = document.querySelectorAll(opts.canvas + ' .bk-flow-location')
                instance.setDraggable(el, true)
            }

            /**
             * 初始化流程节点，使节点添加端点
             */
            var _addEndpoints = function (instance, toId, sourceAnchors, targetAnchors) {
                var self = this
                for (var i = 0; i < sourceAnchors.length; i++) {
                    var sourceUUID = sourceAnchors[i] + toId
                    instance.addEndpoint(toId, opts.sourceEndpoint, {
                        anchor: sourceAnchors[i],
                        uuid: sourceUUID
                    })
                }

                for (var j = 0; j < targetAnchors.length; j++) {
                    var targetUUID = targetAnchors[j] + toId
                    instance.addEndpoint(toId, opts.targetEndpoint, {
                        anchor: targetAnchors[j],
                        uuid: targetUUID
                    })
                }
            }

            /**
             * 移除节点
             */
            var _removeLocation = function (id) {
                let loc = _getLocationById(id)
                if (opts.onRemoveLocationBefore) {
                    if (!opts.onRemoveLocationBefore(loc)) {
                        return false
                    }
                }
                instance.remove(id)

                opts.onRemoveLocationAfter && opts.onRemoveLocationAfter(loc)
            }

            /**
             * 新增节点，更新画布内容
             */
            var _createLocation = function (location) {
                var template = $(opts.template)

                // 若不存在ID字段，则补充节点ID
                if (!location.id) {
                    location.id = handlerFactory.generateNodeId()
                }
                
                var _html = handlerFactory.getLocationTemplate(location.type, 'update')
                var locationObj = handlerFactory.initHtml(_html, location)
                var locationDom = `
                    <div class="bk-flow-location" id="${location.id}" data-type="${location.type}">
                        ${locationObj.str}
                    </div>
                `
                
                if (opts.onCreateLocationBefore) {
                    if (!opts.onCreateLocationBefore(location)) {return null}
                }

                $nodeContainer.el.append(locationDom)
                // 新增节点时若当前画布时放大或者缩小状态，需计算节点位移
                $(locationObj.id).css({
                    left: (1 / $nodeContainer.zoom) * location.x,
                    top: (1 / $nodeContainer.zoom) * location.y
                })
                
                // 绑定数据
                $(locationObj.id).data('raw', location)

                // 添加端点
                var endpointsPosition = []
                if (opts.locationConfig[location.type]) {
                    endpointsPosition = opts.locationConfig[location.type]
                }

                _addEndpoints(instance, location.id, endpointsPosition, [])

                if (opts.isEdit) {
                    // 使得节点可拖拽
                    var locationEl = jsPlumb.getSelector(opts.canvas + ' ' + `#${location.id}`)
                    instance.draggable(locationEl, {
                        grid: [5, 5],
                        start: function (event, id) {
                            nodeClickStatus.pageX = event.e.pageX
                            nodeClickStatus.pageY = event.e.pageY
                        },
                        stop: function (event, id) {
                            // _getBestArrow(id)
                            opts.onLocationMove && opts.onLocationMove(id)
                            if (event.e.pageX !== nodeClickStatus.pageX || event.e.pageY !== nodeClickStatus.pageY) {
                                nodeClickStatus.isDragEvent = true
                            } else {
                                nodeClickStatus.isDragEvent = false
                            }
                        }
                    })
                    _highLight(locationEl)
                }

                opts.onCreateLocationAfter && opts.onCreateLocationAfter(location)

                return location.id
            }

            /**
             * 新增连线，更新画布
             */
            var _createLine = function (line) {
                // 连线前看是否允许连接
                if (opts.onCreateLineBefore &&
                        !opts.onCreateLineBefore(line)) {
                    return false
                }
                var connect = instance.connect({
                    source: line.source.id,
                    target: line.target.id,
                    uuids: [line.source.arrow + line.source.id, line.target.arrow + line.target.id],
                    type: 'Flowchart'
                })

                opts.onCreateLineAfter && opts.onCreateLineAfter(line)
            }

            /**
             * 增加 label
             */
            var _addLabel = function (connect, labelData) {
                const label = connect.addOverlay(["Label", {
                    label: labelData.name,
                    location: -60,
                    cssClass: "branch-condition"
                }])
                var labelDom = label.getElement()
                opts.isEdit && (labelDom.contentEditable = 'plaintext-only')
                labelDom.dataset.lineid = labelData.id
                labelDom.dataset.nodeid = labelData.nodeId
            }

            /**
             * 删除连线
             * @param {String} source
             * @param {String} target
             */
            var _deleteLine = function (source, target) {
                let conns = instance.getConnections({ source: source, target: target })

                for (var i = 0; i < conns.length; i++) {
                    let line = _connection_to_line(conns[i])

                    if (opts.onRemoveLineBefore &&
                            !opts.onRemoveLineBefore(line)) {
                        return false
                    }

                    instance.detach(conns[i])

                    opts.onRemoveLineAfter && opts.onRemoveLineAfter(line)
                }
            }

            /**
             * 通过节点ID，更新DOM内容
             */
            var _updateLocationeById = function (id, data) {
                var $location = $('#' + id)

                // id 参数错误时，不执行节点数据更新
                if (!$location.length) {
                    return
                }

                var rawData = $location.data('raw')

                // 与之前赋值对象取共同集合，保证DOM渲染时，数据的完整性
                rawData = $.extend({}, rawData, data)

                var _html = handlerFactory.getLocationTemplate(rawData.type, 'update')
                var locationObj = handlerFactory.initHtml(_html, rawData)

                $location.html(locationObj.str)
                $location.data('raw', rawData)
            }

            /**
             * 获取节点配置，读取节点DOM位置信息，以及绑定的raw数据
             */
            var _getLocationById = function (id) {
                var $location = $('#' + id)
                var rawData = $location.data('raw')
                // 若画布存在拖拽，则获取节点位移时需加上位移距离 // 不需要加了
                rawData.x = parseInt($location.css('left'))
                rawData.y = parseInt($location.css('top'))
                return rawData
            }

            /**
             * 获取所有节点配置
             */
            var _getLocations = function () {
                var locations = []
                $(opts.canvas + ' ' + '.bk-flow-location').each(function (index, el) {
                    var loc = _getLocationById($(el).attr('id'))
                    locations.push(loc)
                })
                return locations
            }

            /**
             * 获取所有连线
             */
            var _getLines = function () {
                return instance.getAllConnections().map(function (val, index) {
                    return {
                        source: {
                            id: val.endpoints[0].anchor.elementId,
                            arrow: val.endpoints[0].anchor.type
                        },
                        target: {
                            id: val.endpoints[1].anchor.elementId,
                            arrow: val.endpoints[1].anchor.type
                        }
                    }
                })
            }

            /**
             * 通过节点ID获取所有连线，jsPlumb配置信息
             * @params {Int} id 节点ID
             * @params {String} type 连线的类型，可选 source，target，默认为 all
             */
            var _getConnectionsByNodeId = function (id, type) {
                if (!(arguments.length > 0)) {
                    throw '_getConnectionsByNodeId(id, type)必须传递节点id参数'
                }

                var id = id,
                    type = type || 'all'
                var connections = instance.getAllConnections()
                return connections.filter(function (val, index) {
                    switch (type) {
                        case 'all':
                            if (id == val.sourceId || id == val.targetId) {
                                return val
                            }
                            break
                        case 'source':
                            if (id == val.sourceId) {
                                return val
                            }
                            break
                        case 'target':
                            if (id == val.targetId) {
                                return val
                            }
                            break
                        default:
                            throw '_getConnectionsByNodeId(id, type)必须传递节点id参数'
                            break
                    }
                })
            }

            /**
             * 节点框选开关
             * @param {Boolean} dragSelection
             */
            function _setDragSelection (dragSelection) {
                opts.dragSelection = dragSelection
            }

            /**
             * 获取最优连线点
             * @todo: 代码&使用逻辑待优化
             */
            var _getBestArrow = function (id) {
                var dataflow = _self.data('dataflow')
                var ids = id
                var nodeIds = -1
                var locations = dataflow.getAllData().locations
                var lines = instance.getAllConnections()
                locations.forEach(d => {
                    if (d.id === ids) {
                        nodeIds = d.node_id
                    }
                })

                var _getNodeById = function (id) {
                    var dataflow = _self.data('dataflow')
                    var lines = dataflow.getLines()
                    var locations = dataflow.getAllData().locations
                    var nodes = {
                        parent: [],
                        children: []
                    }

                    lines.forEach(element => {
                        if (element.target.id === id) {
                            nodes.parent.push(element.source.id)
                        } else if (element.source.id === id) {
                            nodes.children.push(element.target.id)
                        }
                    });
                    return nodes
                };

                var nodes = _getNodeById(ids)
                // 父子节点
                var parentNode = nodes.parent
                var children = nodes.children
                // 父子节点和当前节点的endpoints
                var parentNodeEndpoints = {}
                var childNodeEndpoints = {}
                var currentNodeEndpoints = dataflow.getEndpoints(ids)
                parentNode.forEach(p => {
                    parentNodeEndpoints[p] = dataflow.getEndpoints(p)
                })
                children.forEach(p => {
                    childNodeEndpoints[p] = dataflow.getEndpoints(p)
                })
                // 获取父节点的最优连接点

                let tempArr = []
                parentNode.forEach(pN => {
                    tempArr = []
                    currentNodeEndpoints.forEach(c => {
                        parentNodeEndpoints[pN].forEach(p => {
                            tempArr.push({
                                cArrow: c.anchor.type,
                                pArrow: p.anchor.type,
                                distance: Math.pow(c.canvas.offsetLeft - p.canvas.offsetLeft, 2) + Math.pow(c.canvas.offsetTop - p.canvas.offsetTop, 2)
                            })
                        })
                        tempArr = tempArr.sort(compare('distance'))
                        function compare(property) {
                            return function (obj1, obj2) {
                                var value1 = obj1[property];
                                var value2 = obj2[property];
                                return value1 - value2;     // 升序
                            }
                        }
                    })
                    let theBestArrowGroup = tempArr[0]
                    lines.forEach((line, index) => {
                        if (line.sourceId === pN && line.targetId === ids) {
                            instance.detach(line)
                            var options = {
                                source: {
                                    id: pN,
                                    arrow: theBestArrowGroup.pArrow
                                },
                                target: {
                                    id: ids,
                                    arrow: theBestArrowGroup.cArrow
                                }
                            }
                            dataflow.createLine(options)
                        }
                    })
                })

                // 获取子节点的最优连接点
                let tempArr2 = []
                children.forEach(cN => {
                    tempArr2 = []
                    currentNodeEndpoints.forEach(c => {
                        childNodeEndpoints[cN].forEach(p => {
                            tempArr2.push({
                                cArrow: c.anchor.type,
                                pArrow: p.anchor.type,
                                distance: Math.pow(c.canvas.offsetLeft - p.canvas.offsetLeft, 2) + Math.pow(c.canvas.offsetTop - p.canvas.offsetTop, 2)
                            })
                        })
                        tempArr2 = tempArr2.sort(compare('distance'))
                        function compare(property) {
                            return function (obj1, obj2) {
                                var value1 = obj1[property];
                                var value2 = obj2[property];
                                return value1 - value2;     // 升序
                            }
                        }
                    })
                    let theBestArrowGroup = tempArr2[0]
                    lines.forEach((line, index) => {
                        if (line.sourceId === ids && line.targetId === cN) {
                            instance.detach(line)
                            var options = {
                                source: {
                                    id: ids,
                                    arrow: theBestArrowGroup.cArrow
                                },
                                target: {
                                    id: cN,
                                    arrow: theBestArrowGroup.pArrow
                                }
                            }
                            dataflow.createLine(options)
                        }
                    })
                })
            }

            var _strToNum = function (str, tpl) {
                var reg = new RegExp(tpl, 'g')

                return Number(str.replace(reg, ''))
            }

            var _isInArray = function (el, arr) {
                let result = {
                    result: false
                }

                arr.map(function (item, index) {
                    if (el === item) {
                        result = {
                            result: true,
                            index: index
                        }

                        return
                    }
                })

                return result
            }

            // +++++++++++++++++++++ 封装 DataFlow 对外暴露的对象 ++++++++++++++++

            /**
             *   dataflow初始化
             */
            var dataflow = function (obj) {
                var self = this
                init.call(this)
            }

            // 将插件对象添加至原型，可查询插件的配置
            dataflow.prototype.instance = instance

            /**
             * @argument
             * @zoom  type of num 缩放的倍数
             * @el 缩放的元素id
             * @transformOrigin 缩放的中心
             */
            dataflow.prototype.setZoom = function (zoom) {
                var transformOrigin = '0 0'
                $nodeContainer.el.css({
                    '-webkit-transform': 'matrix(' + zoom + ',0,0,' + zoom + ',0,0)',
                    '-moz-transform': 'matrix(' + zoom + ',0,0,' + zoom + ',0,0)',
                    '-ms-transform': 'matrix(' + zoom + ',0,0,' + zoom + ',0,0)',
                    'transform': 'matrix(' + zoom + ',0,0,' + zoom + ',0,0)',
                    '-webkit-transformOrigin': transformOrigin,
                    '-moz-transformOrigin': transformOrigin,
                    '-ms-transformOrigin': transformOrigin,
                    'transformOrigin': transformOrigin
                })
                $nodeContainer.zoom = zoom
                instance.setZoom(zoom)
            }
            /**
             * @description 还原画布：缩放还原 && 画布拖拽还原
             */
            dataflow.prototype.resetLocation = function () {
                $nodeContainer.el.css({
                    left: 0,
                    top: 0
                })
                $nodeContainer.left = 0
                $nodeContainer.top = 0
            }
            /**
             *  更新所有节点
             */
            dataflow.prototype.updateCanvas = function (data) {
                this.resetCanvas()

                var lines = data.lines
                var locations = data.locations
                var linesLen = lines.length
                var locationsLen = locations.length
                var $data = opts.data
                var $lines = $data.lines
                var $locations = $data.locations

                _drawData(data)

                // 重绘画布之后，将新的数据重新推入数组中
                $lines = data.lines
                $locations = data.locations
            }

            /**
             * 获取某个节点的anchors/endpoints
             * param id 指定节点的id
             */
            dataflow.prototype.getEndpoints = function (id) {
                var anchors = instance.getEndpoints(document.querySelector('#' + id))
                return anchors
            }

            /**
             *  移动指定节点的anchor的位置
             *  @param id 指定节点的id
             *  @param anchorDirection 需要移动的anchor所在的位置，可选值有Top, Right, Bottom, Left, 可传入单个值或数组
             *  @param direction anchor需要向哪个方向移动，可选值有up, down, left, right
             *  @param displacement 位移长度
             */
            dataflow.prototype.moveAnchors = function (id, anchorDirection, direction, displacement) {
                if (id === undefined) return

                // 将需要移动的anchor的位置转成小写
                anchorDirection = typeof anchorDirection === 'string' ? anchorDirection.toLocaleLowerCase() : anchorDirection.map(function (v) {
                    return v.toLowerCase()
                })

                // 当没有传入displacement时，认为需要移动所有anchor
                if (displacement === undefined) {
                    displacement = Math.abs(anchorDirection)
                    anchorDirection = undefined
                }

                // 处理displacement
                displacement = Math.abs(displacement)
                if (direction === 'up' || direction === 'left') {
                    displacement = -1 * displacement
                }

                var anchors = instance.getEndpoints(document.querySelector('#' + id))
                var styleDirection

                // 处理direction，将传入的物理方向转换成css属性
                if (direction === 'up' || direction === 'down') {
                    styleDirection = 'top'
                } else {
                    styleDirection = 'left'
                }

                // 遍历指定节点的所有anchor
                anchors.map(function (anchor) {
                    var type = anchor.anchor.type.toLowerCase()

                    if (anchorDirection === undefined) {      // 移动所有anchor
                        doDisplacement(anchor, styleDirection, displacement)
                    } else {
                        if (typeof anchorDirection === 'string') {        // 移动某个anchor
                            if (type === anchorDirection) {
                                doDisplacement(anchor, styleDirection, displacement)
                                return
                            }
                        } else if (anchorDirection instanceof Array) {        // 批量移动anchor
                            if (_isInArray(type, anchorDirection).result) {
                                doDisplacement(anchor, styleDirection, displacement)
                            }
                        }
                    }
                })

                // 执行位移动作
                function doDisplacement(anchor, direction, displacement) {
                    anchor.canvas.style[direction] = _strToNum(anchor.canvas.style[direction], 'px') + displacement + 'px'
                }
            }

            /**
             *  批量设置节点的拖动状态
             *  @param id 指定的节点的id，可以是字符串（设置单个节点）、数组（设置多个节点）、或不传（设置全部节点）
             *  @param status 指定节点需要被修改的拖动状态，可选值有true/false
             *  @demo
             *      setDraggable(false) - 设置全部节点为不可拖动
             *      setDraggable('xxx', true) - 设置某个节点可拖动
             *      setDraggable(['xxx', 'yyy', 'zzz'], false) - 批量设置部分节点不可拖动
             */
            dataflow.prototype.setDraggable = function (id, status) {
                var el
                if (status === undefined) {
                    status = id
                    id = undefined
                }

                if (id) {
                    if (typeof id === 'string') {
                        el = document.querySelector('#' + id)
                    } else if (id instanceof Array) {
                        el = id
                    }
                } else {
                    el = document.querySelectorAll(opts.canvas + ' .bk-flow-location')
                }

                instance.setDraggable(el, status)
            }

            // +++++++++++++++ 整理后的方法 +++++++++++++++

            /**
             * 获取所有节点、连线数据
             */
            dataflow.prototype.getAllData = function () {
                return {
                    lines: this.getLines(),
                    locations: this.getLocations()
                }
            }

            /**
             * 重置画布，清空数据
             */
            dataflow.prototype.resetCanvas = function () {
                var win = $(opts.canvas).find('.bk-flow-location')
                var _l = win.length
                for (var i = 0; i < _l; i++) {
                    _removeLocation($(win).eq(i).attr('id'))
                }
            }

            /**
             * 获取所有节点
             */
            dataflow.prototype.getLocations = function () {
                return _getLocations()
            }

            /**
             * 新增节点
             * @param {Object} location 节点配置，包括位置、类型信息和额外信息（id字段自动生成），数据格式：
             *  {
             *     x: 111,
             *     y: 222,
             *     type: 'xxxx'
             *     ...
             *  }
             */
            dataflow.prototype.createLocation = function (location) {
                return _createLocation(location)
            }

            /**
             * 通过节点ID，更新节点DOM内容
             * @param {String} id 节点ID
             * @param {Object} data 需要更新的节点配置，可以是完整的节点配置，也可以是局部配置，比如 {name: 'xxx'}
             */
            dataflow.prototype.updateLocationById = function (id, data) {
                return _updateLocationeById(id, data)
            }

            /**
             * 通过节点ID，返回节点配置
             * @return {Object} 数据格式：
             *  {
             *      id: 'ch111',
             *      x: 100,
             *      y: 200,
             *      type: 'xxx'
             *      ...
             *  }
             */
            dataflow.prototype.getLocationById = function (id) {
                return _getLocationById(id)
            }

            /**
             * 删除某个节点，删除方法会对 onRemoveNodeBefore、onRemoveNodeAfter 两个回调做处理
             * @param {String} id 画布节点ID
             */
            dataflow.prototype.deleteLocation = function (id) {
                _removeLocation(id)
            }

            /**
             * 获取所有连线
             */
            dataflow.prototype.getLines = function () {
                return _getLines()
            }

            /**
             * 连接指定的线，指定源节点和目标节点，以及连接点（Top、Bottom、Left、Right）
             * @param {Object} line 连线配置，数据格式
             *  {
             *      source: {id: 'ch2', arrow: 'Left'},
             *      target: {id: 'ch3', arrow: 'Top'},
             *  }
             */
            dataflow.prototype.createLine = function (line) {
                return _createLine(line)
            }

            /**
             * 删除指定连线
             * @param {String} source 连线起点 DOM-ID
             * @param {String} target 连线终点 DOM-ID
             */
            dataflow.prototype.deleteLine = function (source, target) {
                return _deleteLine(source, target)
            }

            dataflow.prototype.disabledEdit = function () {
                _disabledEdit()
            }

            dataflow.prototype.enableEdit = function () {
                _enableEdit()
            }
            /**
             * 修改指定连线的配置
             * @param {String} source 连线起点 DOM-ID
             * @param {String} target 连线终点 DOM-ID
             * @param {Array} config 连线配置 对应底层 api 不是增量修改 需要传全量配置：
             * eg: [
             *     'Flowchart', // 流程图种类
             *     {
             *          stub: [5, 20], // 起始端点连接线的最小长度
             *          gap: 8, // 线与端点点最小间隔
             *          cornerRadius: 2, // 折线弧度
             *          alwaysRespectStubs: true, // 允许 stub 配置生效
             *          midpoint: 0.9 // 折线比例
             *      }
             *  ]
             */
            dataflow.prototype.setConnector = function (source, target, config) {
                var connections = instance.getAllConnections().filter(item => {
                    return item.sourceId === source && item.targetId === target
                })
                connections.forEach(connection => {
                    connection.setConnector(config)
                })
            }

            /**
             * 添加指定label
             */
            dataflow.prototype.addLabel = function (line, labelName) {
                var connection = instance.getConnections({ source: line.source.id, target: line.target.id })[0]
                if(connection) {
                    _addLabel(connection, labelName)
                }
            }
            
            /**
             * 设置是否开启节点框选
             */
            dataflow.prototype.setDragSelection = function (val) {
                _setDragSelection(val)
            }

            // 绑定DataFlow实例
            return $.each(this, function () {
                var $this = $(this)
                if (!$this.data('dataflow')) {
                    $this.data('dataflow', new dataflow($this))
                }
            })
        }
    })
})(jQuery, artTemplate)

