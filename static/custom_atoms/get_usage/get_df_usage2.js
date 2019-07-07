(function () {
    $.atoms.get_df_usage2 = [
        {
            tag_code: "host_ip",
            type: "input",
            attrs: {
                name: gettext("主机IP"),
                placeholder: gettext("输入IP地址，必填"),
                hookable: true
            },
        },
        {
            tag_code: "host_partition",
            type: "input",
            attrs: {
                name: gettext("磁盘分区"),
                placeholder: gettext("输入要查询的磁盘分区，必填"),
                hookable: true
            },
        },
        {
            tag_code: "script_timeout",
            type: "input",
            attrs: {
                name: gettext("超时时间"),
                placeholder: gettext("单位为秒，可选，默认1000"),
                hookable: true,
                validation: [
                    {
                        type: "custom",
                        args: function (value) {
                            var result = {
                                result: true,
                                error_message: ""
                            };
                            if (value && !Number(value)) {
                                result.result = false;
                                result.error_message = gettext("请输入数字");
                            }
                            return result;
                        }
                    }
                ]
            }
        }
    ]
})();