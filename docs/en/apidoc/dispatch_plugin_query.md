### Function Description

Plugin request forwarding

### Request Parameters

#### Interface Parameters

| Field    | Type     | Required | Description                     |
|----------|----------|----------|---------------------------------|
| url      | string   | Yes      | The actual plugin API path to request |
| method   | string   | No       | HTTP method, supports "GET" or "POST", default is "GET" |
| data     | dict     | No       | Request data when method is POST |

### Request Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "url": "/pipeline/xxxxxxx/xxx/",
    "method": "GET"
}
```

### Response Example

```
{
   "result": true/false,
   "data": {
      No fixed structure, depends on the backend API response
   }
}
```

### Response Parameters

| Field      | Type      | Description      |
|------------|-----------|------------------|
| result     | bool      | true/false - whether the operation succeeded |
| data       | dict      | When result=true, contains successful data (see below) |
| message    | string    | When result=false, contains error message |

#### data
No fixed structure, depends on the backend API response