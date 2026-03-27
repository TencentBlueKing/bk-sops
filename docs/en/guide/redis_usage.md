SOPS can use redis services with the following deployment modes. The configurations required for the corresponding mode are as follows:

## Single-instance Mode

The following environment variables need to be configured for single-instance mode

- BKAPP_REDIS_MODE: `single`
- BKAPP_REDIS_HOST: host of redis service
- BKAPP_REDIS_PORT: port of redis service
- BKAPP_REDIS_PASSWORD (Optional): redis access password
- BKAPP_REDIS_DB (Optional): redis db

## Cluster mode

The following environment variables need to be configured

- BKAPP_REDIS_MODE: `cluster`
- BKAPP_REDIS_HOST: the host of any node in the redis cluster
- BKAPP_REDIS_PORT: the port of any node in the redis cluster
- BKAPP_REDIS_PASSWORD (Optional): redis access password

## Sentinel Mode

The following environment variables need to be configured

- BKAPP_REDIS_MODE: replication
- BKAPP_REDIS_HOST: sentinel host. Supports multiple sentinel configurations. Hosts are separated by a `,`
- BKAPP_REDIS_PORT: sentinel port. Supports multiple sentinel configurations. Ports are separated by a `,`. The number of ports must be consistent with the number of sentinels.
- BKAPP_REDIS_PASSWORD (Optional): redis access password
- BKAPP_REDIS_SERVICE_NAME (Optional): redis cluster master service name
- BKAPP_REDIS_SENTINEL_PASSWORD (Optional): redis sentinel password. If left empty, redis password will be used
