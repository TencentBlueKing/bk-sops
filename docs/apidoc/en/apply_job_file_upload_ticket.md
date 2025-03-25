### Function Description

Apply for a temporary upload credential for the plugin "JOB-Push Local File"

### Request Parameters

None

### Path Parameters

None

### Response Example

```
{
    "result": true,
    "data": {
        "ticket": "d8f8255a783639459f35c182c6671a89"
    }
}
```

### Response Description

| Name      | Type     | Description                           |
|---------|--------|------------------------------|
| result  | bool   | true/false whether the operation was successful            |
| data    | object | Success data when result=true, see below for details |
| data.ticket   | string | Job file upload temporary credential                          |
| message | string | Error message when result=false           |

