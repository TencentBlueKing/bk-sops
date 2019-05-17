(function () {
    $.atoms.transfer_host_to_faultmodule = [
        {
            tag_code: "bk_biz_id",
            type: "input",
            attrs: {
                name: gettext("业务ID"),
                placeholder: gettext("必填"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "bk_host_innerips",
            type: "input",
            attrs: {
                name: gettext("内网IP"),
                placeholder: gettext("多个IP使用;分隔"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        }
    ];
    $.atoms.transfer_host_to_resourcemodule = [
        {
            tag_code: "bk_biz_id",
            type: "input",
            attrs: {
                name: gettext("业务ID"),
                placeholder: gettext("必填"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        },
        {
            tag_code: "bk_host_innerips",
            type: "input",
            attrs: {
                name: gettext("内网IP"),
                placeholder: gettext("多个IP使用;分隔"),
                hookable: true
            },
            validation: [
                {
                    type: "required"
                }
            ]
        }
    ]
})();
