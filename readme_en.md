![](docs/resource/img/logo_en.png)
---
[![license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://github.com/TencentBlueKing/bk-sops/blob/master/LICENSE)
[![Coverage Status](https://codecov.io/gh/TencentBlueKing/bk-sops/branch/master/graph/badge.svg)](https://codecov.io/gh/TencentBlueKing/bk-sops)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/TencentBlueKing/bk-sops/pulls)

Standard OPS is a product in the Tencent Blueking product system, designed to arrange task process and execution
 through a visual graphical interface.

Standard OPS provides two core services. One is scheduling arrangement service: based on the capability of The BlueKing
 PaaS API Gateway to connect various system APIs of an enterprise, integrate the works among multiple systems within 
 the enterprise into a task flow, so as to achieve one-key automated scheduling.The other is self-service: Standard OPS
 shields the difference of the underlying system, allowing the operation and maintenance personnel to hand over the 
 daily operation and maintenance of the business to the personnel of the product, development, test, etc., to realize
 the self-service of the release and change of the business. By means of in-depth integration with BlueKing PaaS,
 Standard OPS provides users with “Min-APP” and “Functional Center”, so that we can further reduce the user's operating
 costs and increase the self-service rate.

The background uses Python as the development language and Django development framework. The front end uses Vue to
 develop the page, uses jQuery to develop the Standard Plugins, and through the configuration development mode, it
 greatly reduces the difficulty for users to develop front-end forms of Standard Plugins.

## Overview
- [Architecture Design](docs/en/guide/architecture.md)
- [Code Directory](docs/en/guide/code_structure.md)
- [Use Case](docs/en/guide/usecase.md)


## Features
- Multi-system access support: Standard OPS docks services such as Blueking Message Management, Configuration System, 
 Job System, and also supports user-defined access to the internal system of the enterprise.
- Visual task flow arrangement: combine Standard Plugins nodes into a flow template by dragging and dropping.
- Multiple process modes: support serial and parallel execution of Standard Plugins nodes, support sub-process, 
 automatic branch selection based on global variables, and configurable node failure handling.
- Parameter engine: support parameter sharing and parameter replacement.
- Interactive task execution: You can pause, continue, and cancel at any time during task execution. After the node
 fails, you can retry or skip.
- Universal Rights Management: Synchronize business roles from configuring system to support the permission control of
 flow templates.

If you want to know more about the above features, please refer to the
 [Blueking Standard OPS White Paper (In Chinese)](https://bk.tencent.com/docs/)


## Getting started
- [Development Background Deployment](docs/en/develop/dev_deploy.md)
- [Development Front-end Deployment](docs/en/develop/dev_web.md)
- [Production Source Deployment](docs/en/deploy/source_code_deploy.md)
- [Production Upload Deployment](docs/en/deploy/upload_pack_deploy.md)
- [Standard Plugin Development](docs/en/develop/dev_plugins.md)


## Usage
- [API Documents](https://bk.tencent.com/docs/document/6.0/167/13157)
- [Standard Plugin Documents](docs/en/guide/plugin_usage.md)
- [Standard Plugin Remote Importing](docs/en/guide/remote_plugins.md)
- [Variables Engine](docs/en/guide/variables_engine.md)
- [Tag Usage And Develop](docs/en/develop/tag_usage_dev.md)


## Releases
- [Published Releases(In Chinese)](https://github.com/TencentBlueKing/bk-sops/releases)


## BlueKing Community

- [BK-CMDB](https://github.com/TencentBlueKing/bk-cmdb): BlueKing CMDB is an enterprise-level management platform designed for assets and applications.
- [BK-CI](https://github.com/TencentBlueKing/bk-ci): BlueKing Continuous Integration platform is a free, open source CI service, which allows developers to automatically create - test - release workflow, and continuously, efficiently deliver their high-quality products.
- [BK-BCS](https://github.com/TencentBlueKing/bk-bcs): BlueKing Container Service is a container-based basic service platform that provides management service to microservice businesses.
- [BK-PaaS](https://github.com/TencentBlueKing/bk-paas): BlueKing PaaS is an open development platform that allows developers to efficiently create, develop, set up, and manage SaaS apps.
- [BK-SOPS](https://github.com/TencentBlueKing/bk-sops): BlueKing SOPS is a system that features workflow arrangement and execution using a graphical interface. It's a lightweight task scheduling and arrangement SaaS product of the Blueking system.
- [BK-JOB](https://github.com/TencentBlueKing/bk-job): BlueKing JOB is a set of operation and maintenance script management platform with the ability to handle a large number of tasks concurrently.

## Support
- [Source (In Chinese)](https://github.com/TencentBlueKing/bk-sops/tree/master)
- [Wiki (In Chinese)](https://github.com/TencentBlueKing/bk-sops/wiki) or ask for help
- [White paper(In Chinese)](https://bk.tencent.com/docs/)
- [BK forum](https://bk.tencent.com/s-mart/community)
- [BK DevOps online video tutorial(In Chinese)](https://bk.tencent.com/s-mart/video/)
- Contact us, technical exchange QQ group：878501914


## Contributing
If you have good ideas or suggestions, please let us know by Issues or Pull Requests and contribute to the Blue Whale
 Open Source Community. For Standard SOPS branch management, issues, and pr specifications, read the
 [Contributing Guide](docs/en/CONTRIBUTING.md)。

If you are interested in contributing, check out the [CONTRIBUTING.md](docs/en/CONTRIBUTING.md), also join our
 [Tencent OpenSource Plan](https://opensource.tencent.com/contribution).

## FAQ
[FAQ](docs/en/wiki/faq.md)


## License
Standard OPS is based on the MIT protocol. Please refer to [LICENSE](LICENSE.txt) for details.

We undertake not to change the open source license (MIT license) applicable to the current version of the project delivered to anyone in the future.
