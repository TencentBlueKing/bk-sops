export default [{
    "variableKey": "bk_timing",
    "tag_code": "bk_timing",
    "type": "input",
    "attrs": {
        "name": "定时时间",
        "placeholder": "秒(s) 或 时间(%Y-%m-%d %H:%M:%S)",
        "hookable": true,
        "validation": [
            {
                type: "custom",
                args: function(value) {
                    var result = {
                        result: false,
                        error_message: "请填写秒(s)且不超过8位数或时间(%Y-%m-%d %H:%M:%S)"
                    }
                    var number_regex = /^\d{1,8}$/;
                    if (number_regex.test(value)) {
                        result.result = true;
                    }

                    var date_time_regex = /^(((\d{3}[1-9]|\d{2}[1-9]\d{1}|\d{1}[1-9]\d{2}|[1-9]\d{3}))|(29-02-((\d{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][048]|[3579][26])00))))-((0[13578]|1[02])-((0[1-9]|[12]\d|3[01]))|((0[469]|11)-(0?[1-9]|[12]\d|30))|(0[2])-(0[1-9]|[1]\d|2[0-8])) ((0|[1])\d|2[0-3]):(0|[1-5])\d:(0|[1-5])\d$/;
                    if (date_time_regex.test(value)) {
                        result.result = true;
                    }

                    return result;
                }
            }
        ]
    }
}]