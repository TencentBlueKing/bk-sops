# FAQ

- Can SOPS plugins access enterprise internal IT systems?
> Yes. Please refer to "Standard Plugin Development" for access methods.

- Encountered an error after clicking execute task in SOPS: taskflow[id=1] get status error: node(nodee37e20…c7fb131) does not exist, may have not by 
executed. The task status in the task list is unknown. What could be the reason?
> The SOPS execution engine depends on Blueking RabbitMQ service and the celery process launched by the App. Please log into the server and make sure the services are started and running normally.
You can check the App's celery.log to locate the cause of the problem.

- SOPS executed the task, but the plugin node encountered an error: Trackback…TypeError:int() argument must be a string or a number,not ‘NoneType’. What could be the reason?
> The SOPS task flow execution status and information cache such as plugin input and output depend on Redis service. Please follow the instructions in the "SOPS Deployment Document" on the Blueking official site on your first deployment,
and redeploy after configuring Redis environment variable. By default, the Community Edition 5.1 supports using Redis service that comes with Blueking Community Edition. However, you may change the configuration to use a high-performance standalone Redis service.
