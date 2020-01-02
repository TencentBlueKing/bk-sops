# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
ANALYSIS_NO_DATA_PARAMS = {
    'type': 'object',
    'required': ['data', 'result'],
    'properties': {
        'data': {
            'type': 'object',
            'properties': {
                'groups': {
                    'type': 'array',
                    'items': {
                    }
                },
                'total': {
                    'type': 'number',
                },
            }
        },
        'result': {
            'type': 'boolean'
        }
    }
}

ANALYSIS_CATEGORY_AND_BUSINESS_PARAMS = {
    'type': 'object',
    'required': ['data', 'result'],
    'properties': {
        'data': {
            'type': 'object',
            'properties': {
                'groups': {
                    'type': 'array',
                    'items': {
                        'code': {
                            'string'
                        },
                        'name': {
                            'string'
                        },
                        'value': {
                            'number'
                        }
                    }
                },
                'total': {
                    'type': 'number',
                },
            }
        },
        'result': {
            'type': 'boolean'
        }
    }
}

ANALYSIS_TASK_CATEGORY_PARAMS = {
    'type': 'object',
    'required': ['data', 'result'],
    'properties': {
        'data': {
            'type': 'array',
            'items': {
                'name': {
                    'string'
                },
                'value': {
                    'string'
                }
            }
        },
        'result': {
            'type': 'boolean'
        }
    }
}
ANALYSIS_TASK_CATEGORY_NO_DATA_PARAMS = {
    'type': 'object',
    'required': ['data', 'result'],
    'properties': {
        'data': {
            'type': 'array',
            'items': {
            }
        },
        'result': {
            'type': 'boolean'
        }
    }
}

ANALYSIS_ATOM_TEMPLATE_PARAMS = {
    'type': 'object',
    'required': ['data', 'result'],
    'properties': {
        'data': {
            'type': 'object',
            'properties': {
                'groups': {
                    'type': 'array',
                    'items': {
                        'templateId': {
                            'number'
                        },
                        'businessId': {
                            'number'
                        },
                        'businessName': {
                            'string'
                        },
                        'templateName': {
                            'string'
                        },
                        'category': {
                            'string'
                        },
                        'editTime': {
                            'string'
                        },
                        'editor': {
                            'string'
                        }
                    }
                },
                'total': {
                    'type': 'number',
                },
            }
        },
        'result': {
            'type': 'boolean'
        }
    }
}

ANALYSIS_ATOM_INSTANCE_PARAMS = {
    'type': 'object',
    'required': ['data', 'result'],
    'properties': {
        'data': {
            'type': 'object',
            'properties': {
                'groups': {
                    'type': 'array',
                    'items': {
                        'instanceId': {
                            'number'
                        },
                        'businessId': {
                            'number'
                        },
                        'businessName': {
                            'string'
                        },
                        'instanceName': {
                            'string'
                        },
                        'category': {
                            'string'
                        },
                        'createTime': {
                            'string'
                        },
                        'creator': {
                            'string'
                        }
                    }
                },
                'total': {
                    'type': 'number',
                },
            }
        },
        'result': {
            'type': 'boolean'
        }
    }
}

ANALYSIS_ATOM_EXECUTE_PARAMS = {
    'type': 'object',
    'required': ['data', 'result'],
    'properties': {
        'data': {
            'type': 'object',
            'properties': {
                'groups': {
                    'type': 'array',
                    'items': {
                        'componentName': {
                            'string'
                        },
                        'executeTimes': {
                            'number'
                        },
                        'avgExecuteTime': {
                            'string'
                        },
                        'failedTimes': {
                            'number'
                        },
                        'failedTimesPercent': {
                            'string'
                        }
                    }
                },
                'total': {
                    'type': 'number',
                },
            }
        },
        'result': {
            'type': 'boolean'
        }
    }
}
ANALYSIS_TEMPLATE_CITE_PARAMS = {
    'type': 'object',
    'required': ['data', 'result'],
    'properties': {
        'data': {
            'type': 'object',
            'properties': {
                'groups': {
                    'type': 'array',
                    'items': {
                        'id': {
                            'number'
                        },
                        'templateName': {
                            'string'
                        },
                        'appmakerTotal': {
                            'number'
                        },
                        'relationshipTotal': {
                            'number'
                        },
                        'instanceTotal': {
                            'number'
                        }
                    }
                },
                'total': {
                    'type': 'number',
                },
            }
        },
        'result': {
            'type': 'boolean'
        }
    }
}
ANALYSIS_TEMPLATE_NODE_PARAMS = {
    'type': 'object',
    'required': ['data', 'result'],
    'properties': {
        'data': {
            'type': 'object',
            'properties': {
                'groups': {
                    'type': 'array',
                    'items': {
                        'templateId': {
                            'number'
                        },
                        'businessId': {
                            'number'
                        },
                        'businessName': {
                            'string'
                        },
                        'templateName': {
                            'string'
                        },
                        'category': {
                            'string'
                        },
                        'editTime': {
                            'string'
                        },
                        'editor': {
                            'string'
                        },
                        'atomTotal': {
                            'number'
                        },
                        'subprocessTotal': {
                            'number'
                        },
                        'gatewaysTotal': {
                            'number'
                        }
                    }
                },
                'total': {
                    'type': 'number',
                },
            }
        },
        'result': {
            'type': 'boolean'
        }
    }
}

ANALYSIS_APPMAKER_INSTANCE_PARAMS = {
    'type': 'object',
    'required': ['data', 'result'],
    'properties': {
        'data': {
            'type': 'object',
            'properties': {
                'groups': {
                    'type': 'array',
                    'items': {
                        'templateId': {
                            'number'
                        },
                        'businessId': {
                            'number'
                        },
                        'businessName': {
                            'string'
                        },
                        'templateName': {
                            'string'
                        },
                        'category': {
                            'string'
                        },
                        'editTime': {
                            'string'
                        },
                        'editor': {
                            'string'
                        },
                        'instanceTotal': {
                            'number'
                        }
                    }
                },
                'total': {
                    'type': 'number',
                },
            }
        },
        'result': {
            'type': 'boolean'
        }
    }
}
ANALYSIS_INSTANCE_NODE_PARAMS = {
    'type': 'object',
    'required': ['data', 'result'],
    'properties': {
        'data': {
            'type': 'object',
            'properties': {
                'groups': {
                    'type': 'array',
                    'items': {
                        'instanceId': {
                            'number'
                        },
                        'businessId': {
                            'number'
                        },
                        'businessName': {
                            'string'
                        },
                        'instanceName': {
                            'string'
                        },
                        'category': {
                            'string'
                        },
                        'createTime': {
                            'string'
                        },
                        'creator': {
                            'string'
                        },
                        'atomTotal': {
                            'number'
                        },
                        'subprocessTotal': {
                            'number'
                        },
                        'gatewaysTotal': {
                            'number'
                        }
                    }
                },
                'total': {
                    'type': 'number',
                },
            }
        },
        'result': {
            'type': 'boolean'
        }
    }
}
ANALYSIS_INSTANCE_DETAILS_PARAMS = {
    'type': 'object',
    'required': ['data', 'result'],
    'properties': {
        'data': {
            'type': 'object',
            'properties': {
                'groups': {
                    'type': 'array',
                    'items': {
                        'instanceId': {
                            'number'
                        },
                        'businessId': {
                            'number'
                        },
                        'businessName': {
                            'string'
                        },
                        'instanceName': {
                            'string'
                        },
                        'category': {
                            'string'
                        },
                        'createTime': {
                            'string'
                        },
                        'creator': {
                            'string'
                        },
                        'executeTime': {
                            'string'
                        }
                    }
                },
                'total': {
                    'type': 'number',
                },
            }
        },
        'result': {
            'type': 'boolean'
        }
    }
}

ANALYSIS_INSTANCE_TIME_PARAMS = {
    'type': 'object',
    'required': ['data', 'result'],
    'properties': {
        'data': {
            'type': 'object',
            'properties': {
                'groups': {
                    'type': 'array',
                    'items': {
                        'time': {
                            'string'
                        },
                        'value': {
                            'number'
                        }
                    }
                },
                'total': {
                    'type': 'number',
                },
            }
        },
        'result': {
            'type': 'boolean'
        }
    }
}
