import { STRING_LENGTH } from './index.js'
import Ajv from 'ajv'

const NODE_ID_REG = '^n[0-9a-z]+'
const LINE_ID_REG = '^l[0-9a-z]+'
const VAR_KEY_REG = '^\\${[\\.\\w]+}$'

const flowNode = {
    $id: '/FlowNode',
    title: '流程节点字段',
    type: 'object',
    properties: {
        id: {
            type: 'string',
            pattern: NODE_ID_REG
        },
        incoming: {
            type: 'string',
            pattern: LINE_ID_REG
        },
        outgoing: {
            type: 'string',
            pattern: LINE_ID_REG
        },
        optional: {
            type: 'boolean'
        },
        state_name: {
            type: 'string'
        }
    },
    required: ['id', 'incoming', 'outgoing', 'optional']
}

const serviceActivity = {
    $id: '/ServiceActivity',
    title: '普通任务节点字段',
    allOf: [
        { $ref: '/FlowNode' },
        {
            type: 'object',
            properties: {
                name: {
                    type: 'string',
                    minLength: 1,
                    maxLength: STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH
                },
                type: {
                    type: 'string',
                    const: 'ServiceActivity'
                },
                component: {
                    type: 'object',
                    properties: {
                        code: {
                            type: 'string',
                            minLength: 1
                        },
                        data: {
                            type: 'object'
                        }
                    },
                    required: ['code', 'data']
                },
                error_ignorable: {
                    type: 'boolean'
                },
                // can_retry 为旧数据字段，retryable 为新规范字段
                can_retry: {
                    type: 'boolean'
                },
                retryable: {
                    type: 'boolean'
                },
                // isSkipped 为旧数据字段，skippable 为新规范字段
                isSkipped: {
                    type: 'boolean'
                },
                skippable: {
                    type: 'boolean'
                }
            },
            required: ['name', 'type', 'component'],
            oneOf: [ // 这两个旧字段统一替换，不存在交叉存在的情况
                {
                    required: ['error_ignorable', 'can_retry', 'isSkipped']
                },
                {
                    required: ['error_ignorable', 'retryable', 'skippable']
                }
            ]
        }
    ]
}

const subProcess = {
    $id: '/SubProcess',
    title: '子流程任务节点字段',
    allOf: [
        { $ref: '/FlowNode' },
        {
            type: 'object',
            properties: {
                template_id: {
                    type: ['string', 'number']
                },
                name: {
                    type: 'string',
                    minLength: 1,
                    maxLength: STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH
                },
                type: {
                    type: 'string',
                    const: 'SubProcess'
                },
                constants: {
                    type: 'object'
                },
                version: {
                    type: 'string'
                }
            },
            required: ['template_id', 'name', 'type', 'constants']
        }
    ]
}

const constantItem = {
    $id: '/ConstantItem',
    title: '全局变量字段',
    type: 'object',
    properties: {
        custom_type: {
            type: 'string'
        },
        desc: {
            type: 'string'
        },
        index: {
            type: 'integer',
            minimum: 0
        },
        key: {
            type: 'string',
            pattern: VAR_KEY_REG,
            minLength: 3
        },
        name: {
            type: 'string',
            minLength: 1
        },
        show_type: {
            type: 'string'
        },
        source_info: {
            type: 'object',
            patternProperties: {
                [NODE_ID_REG]: {
                    type: 'array'
                }
            }
        }
    },
    required: ['custom_type', 'desc', 'index', 'key', 'name', 'show_type', 'source_info']
}

const flowItem = {
    $id: '/FlowItem',
    title: 'flow item',
    type: 'object',
    properties: {
        id: {
            type: 'string',
            pattern: LINE_ID_REG
        },
        is_default: {
            type: 'boolean'
        },
        source: {
            type: 'string',
            pattern: NODE_ID_REG
        },
        target: {
            type: 'string',
            pattern: NODE_ID_REG
        }
    },
    required: ['id', 'is_default', 'source', 'target']
}

const exclusiveGateway = {
    $id: '/ExclusiveGateway',
    title: '分支网关节点字段',
    type: 'object',
    properties: {
        conditions: {
            type: 'object',
            patternProperties: {
                [LINE_ID_REG]: {
                    type: 'object',
                    properties: {
                        evaluate: {
                            type: 'string'
                        }
                    },
                    required: ['evaluate']
                }
            }
        },
        id: {
            type: 'string',
            pattern: NODE_ID_REG
        },
        incoming: {
            type: 'string',
            pattern: LINE_ID_REG
        },
        name: {
            type: 'string'
        },
        outgoing: {
            type: 'array',
            items: {
                type: 'string',
                pattern: LINE_ID_REG
            }
        },
        type: {
            type: 'string',
            const: 'ExclusiveGateway'
        }
    },
    required: ['conditions', 'id', 'incoming', 'name', 'outgoing', 'type']
}

const parallelGateway = {
    $id: '/ParallelGateway',
    title: '并行网关节点字段',
    type: 'object',
    properties: {
        id: {
            type: 'string',
            pattern: NODE_ID_REG
        },
        incoming: {
            type: 'string',
            pattern: LINE_ID_REG
        },
        name: {
            type: 'string'
        },
        outgoing: {
            type: 'array',
            items: {
                type: 'string',
                pattern: LINE_ID_REG
            }
        },
        type: {
            type: 'string',
            const: 'ParallelGateway'
        }
    },
    required: ['id', 'incoming', 'name', 'outgoing', 'type']
}

const convergeGateway = {
    $id: '/ConvergeGateway',
    title: '汇聚网关节点字段',
    type: 'object',
    properties: {
        id: {
            type: 'string',
            pattern: NODE_ID_REG
        },
        incoming: {
            type: 'array',
            items: {
                type: 'string',
                pattern: LINE_ID_REG
            }
        },
        name: {
            type: 'string'
        },
        outgoing: {
            type: 'string',
            pattern: LINE_ID_REG
        },
        type: {
            type: 'string',
            const: 'ConvergeGateway'
        }
    },
    required: ['id', 'incoming', 'name', 'outgoing', 'type']
}

const lineItem = {
    $id: '/LineItem',
    type: 'object',
    properties: {
        id: {
            type: 'string',
            pattern: LINE_ID_REG
        },
        source: {
            type: 'object',
            properties: {
                arrow: {
                    type: 'string',
                    minLength: 1
                },
                id: {
                    type: 'string',
                    pattern: NODE_ID_REG
                }
            },
            required: ['id']
        },
        target: {
            type: 'object',
            properties: {
                arrow: {
                    type: 'string',
                    minLength: 1
                },
                id: {
                    type: 'string',
                    pattern: NODE_ID_REG
                }
            },
            required: ['id']
        }
    },
    required: ['id', 'source', 'target']
}

const locationItem = {
    $id: '/LocationItem',
    title: '任务节点字段',
    type: 'object',
    properties: {
        id: {
            type: 'string',
            pattern: NODE_ID_REG
        },
        type: {
            type: 'string',
            minLength: 1
        },
        name: {
            type: 'string'
        },
        x: {
            type: 'number'
        },
        y: {
            type: 'number'
        }
    },
    required: ['id', 'type', 'x', 'y']
}

const activitiesFieldSchema = {
    $id: '/ActivitiesFieldSchema',
    type: 'object',
    patternProperties: {
        [NODE_ID_REG]: {
            type: 'object',
            properties: {
                type: {
                    type: 'string',
                    enum: ['ServiceActivity', 'SubProcess']
                }
            },
            allOf: [
                {
                    if: { properties: { type: { const: 'ServiceActivity' } } },
                    then: {
                        $ref: '/ServiceActivity'
                    }
                },
                {
                    if: { properties: { type: { const: 'SubProcess' } } },
                    then: {
                        $ref: '/SubProcess'
                    }
                }
            ]
        }
    }
}

const constantsFieldSchema = {
    $id: '/ConstantsFieldSchema',
    type: 'object',
    patternProperties: {
        [VAR_KEY_REG]: {
            $ref: '/ConstantItem'
        }
    }
}

const flowsFieldSchema = {
    $id: '/FlowsFieldSchema',
    type: 'object',
    patternProperties: {
        [LINE_ID_REG]: {
            $ref: '/FlowItem'
        }
    }
}

const gatewayFieldSchema = {
    $id: '/GatewayFieldSchema',
    type: 'object',
    patternProperties: {
        [NODE_ID_REG]: {
            type: 'object',
            properties: {
                type: {
                    type: 'string',
                    enum: ['ExclusiveGateway', 'ParallelGateway', 'ConvergeGateway']
                }
            },
            allOf: [
                {
                    if: { properties: { type: { const: 'ExclusiveGateway' } } },
                    then: { $ref: '/ExclusiveGateway' }
                },
                {
                    if: { properties: { type: { const: 'ParallelGateway' } } },
                    then: { $ref: '/ParallelGateway' }
                },
                {
                    if: { properties: { type: { const: 'ConvergeGateway' } } },
                    then: { $ref: '/ConvergeGateway' }
                }
            ]
        }
    }
}

const linesFieldSchema = {
    $id: '/LinesFieldSchema',
    type: 'array',
    items: {
        $ref: '/LineItem'
    }
}

const locationFieldSchema = {
    $id: '/LocationFieldSchema',
    type: 'array',
    items: {
        $ref: '/LocationItem'
    }
}

const endEventSchema = {
    $id: '/EndEventSchema',
    title: '结束节点字段',
    type: 'object',
    properties: {
        id: {
            type: 'string',
            pattern: NODE_ID_REG
        },
        incoming: {
            type: 'string',
            pattern: LINE_ID_REG
        },
        name: {
            type: 'string'
        },
        outgoing: {
            type: 'string',
            maxLength: 0
        },
        type: {
            type: 'string',
            const: 'EmptyEndEvent'
        }
    },
    required: ['id', 'incoming', 'name', 'outgoing', 'type']
}

const startEventSchema = {
    $id: '/StartEventSchema',
    title: '开始节点字段',
    type: 'object',
    properties: {
        id: {
            type: 'string',
            pattern: NODE_ID_REG
        },
        incoming: {
            type: 'string',
            maxLength: 0
        },
        name: {
            type: 'string'
        },
        outgoing: {
            type: 'string',
            pattern: LINE_ID_REG
        },
        type: {
            type: 'string',
            const: 'EmptyStartEvent'
        }
    },
    required: ['id', 'incoming', 'name', 'outgoing', 'type']
}

const outputsFieldSchema = {
    $id: '/OutputsFieldSchema',
    title: '变量输出字段',
    type: 'array',
    items: {
        type: 'string',
        pattern: VAR_KEY_REG
    }
}

export const pipelineTreeSchema = {
    $id: '/pipelineSchema',
    title: 'pipeline_tree字段',
    properties: {
        activities: {
            $ref: '/ActivitiesFieldSchema'
        },
        constants: {
            $ref: '/ConstantsFieldSchema'
        },
        flows: {
            $ref: '/FlowsFieldSchema'
        },
        gateways: {
            $ref: '/GatewayFieldSchema'
        },
        line: {
            $ref: '/LinesFieldSchema'
        },
        location: {
            $ref: 'LocationFieldSchema'
        },
        end_event: {
            $ref: '/EndEventSchema'
        },
        start_event: {
            $ref: '/StartEventSchema'
        },
        outputs: {
            $ref: '/OutputsFieldSchema'
        }
    },
    required: ['activities', 'constants', 'flows', 'gateways', 'line', 'location', 'end_event', 'start_event', 'outputs']
}

const ajv = new Ajv()

ajv.addSchema(flowNode, '/FlowNode')
ajv.addSchema(serviceActivity, '/ServiceActivity')
ajv.addSchema(subProcess, '/SubProcess')
ajv.addSchema(constantItem, '/ConstantItem')
ajv.addSchema(flowItem, '/FlowItem')
ajv.addSchema(parallelGateway, '/ParallelGateway')
ajv.addSchema(convergeGateway, '/ConvergeGateway')
ajv.addSchema(exclusiveGateway, '/ExclusiveGateway')
ajv.addSchema(lineItem, '/LineItem')
ajv.addSchema(locationItem, '/LocationItem')
ajv.addSchema(activitiesFieldSchema, '/ActivitiesFieldSchema')
ajv.addSchema(constantsFieldSchema, '/ConstantsFieldSchema')
ajv.addSchema(flowsFieldSchema, '/FlowsFieldSchema')
ajv.addSchema(gatewayFieldSchema, '/GatewayFieldSchema')
ajv.addSchema(linesFieldSchema, '/LinesFieldSchema')
ajv.addSchema(locationFieldSchema, '/LocationFieldSchema')
ajv.addSchema(endEventSchema, '/EndEventSchema')
ajv.addSchema(startEventSchema, '/StartEventSchema')
ajv.addSchema(outputsFieldSchema, '/OutputsFieldSchema')

export default ajv.compile(pipelineTreeSchema)
