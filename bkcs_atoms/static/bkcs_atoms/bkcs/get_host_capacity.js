(function(){
	$.atoms.bkcs_get_host_capacity = [
		{
            tag_code: "server_ip",
            type: "input",
            attrs: {
                name: "ip",
                placeholder: "请输入ip",
                hookable: true,
                validation:[
                    {
                        type: "required",
                    }
                ]
            }
        },
        {
            tag_code: "disk",
            type: "input",
            attrs: {
                name: "disk",
                placeholder: "请输入分区",
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        }
	]
})();