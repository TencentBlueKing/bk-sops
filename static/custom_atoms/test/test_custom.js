(function(){
    $.atoms.self_server_get_dfusage = [
        {
            tag_code: "self_server_ip",
            type: "input",
            attrs: {
                name: "主机IP",
                hookable: true,
                default: '10.0.1.80',
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
        },
        {
            tag_code: "self_server_system",
            type: "input",
            attrs: {
                name: "主机系统",
                default: "linux",
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "self_server_disk",
            type: "input",
            attrs: {
                name: "主机磁盘",
                hookable: true,
                default: '/home',
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
        },
        {
            tag_code: "self_server_username",
            type: "input",
            attrs: {
                name: "用户",
                hookable: true,
                default: '550407948',
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
        },
    ]
})();