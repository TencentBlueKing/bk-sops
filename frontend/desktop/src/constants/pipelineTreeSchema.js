import { STRING_LENGTH } from './index.js'
import { Validator } from 'jsonschema'

const NODE_ID_REG = '^node[0-9a-z]{28}$'
const LINE_ID_REG = '^line[0-9a-z]{28}$'
const VAR_KEY_REG = '^\\$\\{(\\w+)\\}$'

const serviceActivity = {
    id: '/ServiceActivity',
    title: '普通任务节点字段',
    type: 'object',
    properties: {
        id: {
            type: 'string',
            pattern: NODE_ID_REG
        },
        name: {
            type: 'string',
            minLenth: 1,
            maxLength: STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH
        },
        incoming: {
            type: 'string',
            pattern: LINE_ID_REG
        },
        outgoing: {
            type: 'string',
            pattern: LINE_ID_REG
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
                    minLenth: 1
                },
                data: {
                    type: 'object'
                }
            },
            required: ['code', 'data']
        },
        optional: {
            type: 'boolean'
        }
    },
    required: ['id', 'name', 'incoming', 'outgoing', 'type', 'component', 'optional']
}

const subProcess = {
    id: '/SubProcess',
    title: '子流程任务节点字段',
    type: 'object',
    properties: {
        id: {
            type: 'string',
            pattern: NODE_ID_REG
        },
        name: {
            type: 'string',
            minLenth: 1,
            maxLength: STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH
        },
        incoming: {
            type: 'string',
            pattern: LINE_ID_REG
        },
        outgoing: {
            type: 'string',
            pattern: LINE_ID_REG
        },
        type: {
            type: 'string',
            const: 'SubProcess'
        },
        constants: {
            type: 'object'
        },
        optional: {
            type: 'boolean'
        }
    },
    required: ['id', 'name', 'incoming', 'outgoing', 'type', 'constants', 'optional']
}

const constantItem = {
    id: '/ConstantItem',
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
            minLenth: 3
        },
        name: {
            type: 'string',
            minLenth: 1
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
    id: '/FlowItem',
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
    id: '/ExclusiveGateway',
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
    id: '/ParallelGateway',
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
    id: '/ConvergeGateway',
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
    id: '/LineItem',
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
                    type: 'string'
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
                    type: 'string'
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
    id: '/LocationItem',
    title: '任务节点字段',
    type: 'object',
    properties: {
        id: {
            type: 'string',
            pattern: NODE_ID_REG
        },
        type: {
            type: 'string'
        },
        x: {
            type: 'integer'
        },
        y: {
            type: 'integer'
        }
    },
    required: ['id', 'type', 'x', 'y']
}

const activitiesFieldSchema = {
    id: '/ActivitiesFieldSchema',
    type: 'object',
    patternProperties: {
        [NODE_ID_REG]: {
            anyOf: [
                { $ref: '/ServiceActivity' },
                { $ref: '/SubProcess' }
            ]
        }
    }
}

const constantsFieldSchema = {
    id: '/ConstantsFieldSchema',
    type: 'object',
    patternProperties: {
        [VAR_KEY_REG]: {
            $ref: '/ConstantItem'
        }
    }
}

const flowsFieldSchema = {
    id: '/FlowsFieldSchema',
    type: 'object',
    patternProperties: {
        [LINE_ID_REG]: {
            $ref: '/FlowItem'
        }
    }
}

const gatewayFieldSchema = {
    id: '/GatewayFieldSchema',
    type: 'object',
    patternProperties: {
        [NODE_ID_REG]: {
            anyOf: [
                { $ref: '/ExclusiveGateway' },
                { $ref: '/ParallelGateway' },
                { $ref: '/ConvergeGateway' }
            ]
        }
    }
}

const linesFieldSchema = {
    id: '/LinesFieldSchema',
    type: 'array',
    items: {
        $ref: '/LineItem'
    }
}

const locationFieldSchema = {
    id: '/LocationFieldSchema',
    type: 'array',
    items: {
        $ref: '/LocationItem'
    }
}

const endEventSchema = {
    id: '/EndEventSchema',
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
    id: '/StartEventSchema',
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
    id: '/OutputsFieldSchema',
    title: '变量输出字段',
    type: 'array',
    items: {
        type: 'string',
        pattern: VAR_KEY_REG
    }
}

export const pipelineTreeSchema = {
    id: '/pipelineSchema',
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

const schemaValidator = new Validator()

schemaValidator.addSchema(serviceActivity, '/ServiceActivity')
schemaValidator.addSchema(subProcess, '/SubProcess')
schemaValidator.addSchema(constantItem, '/ConstantItem')
schemaValidator.addSchema(flowItem, '/FlowItem')
schemaValidator.addSchema(parallelGateway, '/ParallelGateway')
schemaValidator.addSchema(convergeGateway, '/ConvergeGateway')
schemaValidator.addSchema(exclusiveGateway, '/ExclusiveGateway')
schemaValidator.addSchema(lineItem, '/LineItem')
schemaValidator.addSchema(locationItem, '/LocationItem')
schemaValidator.addSchema(activitiesFieldSchema, '/ActivitiesFieldSchema')
schemaValidator.addSchema(constantsFieldSchema, '/ConstantsFieldSchema')
schemaValidator.addSchema(flowsFieldSchema, '/FlowsFieldSchema')
schemaValidator.addSchema(gatewayFieldSchema, '/GatewayFieldSchema')
schemaValidator.addSchema(linesFieldSchema, '/LinesFieldSchema')
schemaValidator.addSchema(locationFieldSchema, '/LocationFieldSchema')
schemaValidator.addSchema(endEventSchema, '/EndEventSchema')
schemaValidator.addSchema(startEventSchema, '/StartEventSchema')
schemaValidator.addSchema(outputsFieldSchema, '/OutputsFieldSchema')

export default schemaValidator
