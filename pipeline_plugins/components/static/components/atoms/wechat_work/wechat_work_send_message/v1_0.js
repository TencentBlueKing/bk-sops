$.atoms.wechat_work_send_message = [
    {
        "type": "textarea",
        "attrs": {
            "name": gettext("会话ID"),
            "hookable": true,
            "validation": [
                {
                    "type": "required"
                }
            ],
            "placeholder": gettext("通过在群里@企业微信机器人获取，多个用换行分隔"),
        },
        "tag_code": "wechat_work_chat_id"
    },
    {
        "tag_code": "msgtype",
        "type": "radio",
        "attrs": {
            "name": gettext("消息格式"),
            "hookable": false,
            "items": [
                {"name": gettext("文本(text)"), "value": "text"},
                {"name": gettext("Markdown"), "value": "markdown"},
            ],
            "default": "text",
            "validation": [
                {
                    "type": "required"
                }
            ],
        },
    },
    {
        "type": "textarea",
        "attrs": {
            "name": gettext("消息内容"),
            "hookable": true,
            "validation": [
                {
                    "type": "required"
                }
            ]
        },
        "tag_code": "message_content"
    },
    {
        "type": "input",
        "attrs": {
            "name": gettext("提醒人"),
            "hookable": true,
            "placeholder": gettext("提醒群指定成员(@某个成员)，多个成员用 `,` 分隔，@all表示提醒所有人")
        },
        "events": [],
        "methods": {},
        "tag_code": "wechat_work_mentioned_members"
    }
]