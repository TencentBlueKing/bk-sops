import { TEMPLATE_NODE_NAME_MAX_LENGTH } from './index.js'
import { Validator } from 'jsonschema'

const NODE_ID_REG = '^node[0-9a-z]{28}$'
const LINE_ID_REG = '^line[0-9a-z]{28}$'
const VAR_KEY_REG = '^\$\{(\w+)\}$'

const serviceActivity = {
    id: '/serviceActivity',
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
            maxLength: TEMPLATE_NODE_NAME_MAX_LENGTH
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
    id: '/subProcess',
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
            maxLength: TEMPLATE_NODE_NAME_MAX_LENGTH
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
    id: '/constantItem',
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
                NODE_ID_REG: {
                    type: 'array'
                }
            }
        }
    },
    required: ['custom_type', 'desc', 'index', 'key', 'name', 'show_type', 'source_info']
}

const flowItem = {
    id: '/flowItem',
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
    id: '/exclusiveGateway',
    title: '分支网关节点字段',
    type: 'object',
    properties: {
        conditions: {
            type: 'object',
            patternProperties: {
                LINE_ID_REG: {
                    type: 'object',
                    properties: {
                        evaluate: {
                            type: 'string'
                        }
                    }
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
        type: 'ExclusiveGateway'
    },
    required: ['conditions', 'id', 'incoming', 'name', 'outgoing', 'type']
}

const parallelGateway = {
    id: '/parallelGateway',
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
        type: 'ParallelGateway'
    },
    required: ['id', 'incoming', 'name', 'outgoing', 'type']
}

const convergeGateway = {
    id: '/convergeGateway',
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
        type: 'ConvergeGateway'
    },
    required: ['id', 'incoming', 'name', 'outgoing', 'type']
}

const lineItem = {
    id: '/lineItem',
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
    id: '/locationItem',
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
    id: '/activitiesFieldSchema',
    type: 'Array',
    patternProperties: {
        NODE_ID_REG: {
            type: 'object',
            oneOf: [
                { $ref: '/serviceActivity' },
                { $ref: '/subProcess' }
            ]
        }
    }
}

const constantsFieldSchema = {
    id: '/constantsFieldSchema',
    type: 'object',
    patternProperties: {
        [VAR_KEY_REG]: {
            $ref: '/constantItem'
        }
    }
}

const flowsFieldSchema = {
    id: '/flowsFieldSchema',
    type: 'object',
    patternProperties: {
        LINE_ID_REG: {
            $ref: '/flowItem'
        }
    }
}

const gatewayFieldSchema = {
    id: '/gatewayFieldSchema',
    type: 'object',
    patternProperties: {
        NODE_ID_REG: {
            type: 'object',
            oneOf: [
                { $ref: '/exclusiveGateway' },
                { $ref: '/parallelGateway' },
                { $ref: '/convergeGateway' }
            ]
        }
    }
}

const linesFieldSchema = {
    id: '/linesFieldSchema',
    type: 'array',
    items: {
        $ref: '/lineItem'
    }
}

const locationFieldSchema = {
    id: '/locationFieldSchema',
    type: 'array',
    items: {
        $ref: '/locationItem'
    }
}

const endEventSchema = {
    id: '/endEventSchema',
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
    id: '/startEventSchema',
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
    id: '/outputsFieldSchema',
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
            $ref: '/activitiesFieldSchema'
        },
        constants: {
            $ref: '/constantsFieldSchema'
        },
        flows: {
            $ref: '/flowsFieldSchema'
        },
        gateways: {
            $ref: '/gatewayFieldSchema'
        },
        line: {
            $ref: '/linesFieldSchema'
        },
        location: {
            $ref: '/locationFieldSchema'
        },
        end_event: {
            $ref: '/endEventSchema'
        },
        start_event: {
            $ref: '/startEventSchema'
        },
        outputs: {
            $ref: '/outputsFieldSchema'
        }
    },
    required: ['activities', 'constants', 'flows', 'gateways', 'line', 'location', 'end_event', 'start_event', 'outputs']
}

const schemaValidator = new Validator()

schemaValidator.addSchema(serviceActivity, '/serviceActivity')
schemaValidator.addSchema(subProcess, '/subProcess')
schemaValidator.addSchema(constantItem, '/constantItem')
schemaValidator.addSchema(flowItem, '/flowItem')
schemaValidator.addSchema(parallelGateway, '/parallelGateway')
schemaValidator.addSchema(convergeGateway, '/convergeGateway')
schemaValidator.addSchema(exclusiveGateway, '/exclusiveGateway')
schemaValidator.addSchema(lineItem, '/lineItem')
schemaValidator.addSchema(locationItem, '/locationItem')
schemaValidator.addSchema(activitiesFieldSchema, '/activitiesFieldSchema')
schemaValidator.addSchema(constantsFieldSchema, '/constantsFieldSchema')
schemaValidator.addSchema(flowsFieldSchema, '/flowsFieldSchema')
schemaValidator.addSchema(gatewayFieldSchema, '/gatewayFieldSchema')
schemaValidator.addSchema(linesFieldSchema, '/linesFieldSchema')
schemaValidator.addSchema(locationFieldSchema, '/locationFieldSchema')
schemaValidator.addSchema(endEventSchema, '/endEventSchema')
schemaValidator.addSchema(startEventSchema, '/startEventSchema')
schemaValidator.addSchema(outputsFieldSchema, '/outputsFieldSchema')

export default schemaValidator
