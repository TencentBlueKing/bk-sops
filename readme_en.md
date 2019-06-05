# BlueKing Standard OPS（Community Edition）
![](docs/resource/img/bk_sops.png)
---
[![license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://github.com/Tencent/bk-sops/blob/master/LICENSE)
[![Release](https://img.shields.io/badge/release-3.3.15-brightgreen.svg)](https://github.com/Tencent/bk-sops/releases)
[![travis-ci](https://travis-ci.com/Tencent/bk-sops.svg?branch=master)](https://travis-ci.com/Tencent/bk-sops)
[![Coverage Status](https://codecov.io/gh/Tencent/bk-sops/branch/master/graph/badge.svg)](https://codecov.io/gh/Tencent/bk-sops)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Tencent/bk-sops/pulls)

Standard OPS is a product in the Tencent Blueking product system, designed to arrange task process and execution through a visual graphical interface.

Standard OPS provides two core services. One is scheduling arrangement service: based on the capability of The BlueKing PaaS API Gateway to connect various system APIs of an enterprise, integrate the works among multiple systems within the enterprise into a task flow, so as to achieve one-key automated scheduling.The other is self-service: Standard OPS shields the difference of the underlying system, allowing the operation and maintenance personnel to hand over the daily operation and maintenance of the business to the personnel of the product, development, test, etc., to realize the self-service of the release and change of the business. By means of in-depth integration with BlueKing PaaS, Standard OPS provides users with “Min-APP” and “Functional Center”, so that we can further reduce the user's operating costs and increase the self-service rate.

The background uses Python as the development language and Django development framework. The front end uses Vue to develop the page, uses jQuery to develop the atom, and through the configuration development mode, it greatly reduces the difficulty for users to develop atomic front-end forms.

## Overview
- [Architecture Design (In Chinese)](docs/overview/architecture.md)
- [Code Directory (In Chinese)](docs/overview/code_structure.md)
- [Use Scenario (In Chinese)](docs/overview/usecase.md)


## Features
- Multi-system access support: Standard OPS docks services such as Blueking Message Management, Configuration System, Job System, and also supports user-defined access to the internal system of the enterprise.
- Visual task flow arrangement: combine atomic nodes into a flow template by dragging and dropping.
- Multiple process modes: support serial and parallel execution of atoms, support sub-process, automatic branch selection based on global variables, and configurable node failure handling.
- Parameter engine: support parameter sharing and parameter replacement.
- Interactive task execution: ou can pause, continue, and cancel at any time during task execution. After the node fails, you can retry or skip.
- Universal Rights Management: Synchronize business roles from configuring system to support the permission control of flow templates.

If you want to know more about the above features, please refer to the [Blueking Standard OPS White Paper (In Chinese)](http://docs.bk.tencent.com/product_white_paper/gcloud/)


## Getting started
- [Development Background Deployment (In Chinese)](docs/install/dev_deploy.md)
- [Development Front-end Deployment (In Chinese)](docs/install/dev_web.md)
- [Production Source Deployment (In Chinese)](docs/install/source_code_deploy.md)
- [Production Upload Deployment (In Chinese)](docs/install/upload_pack_deploy.md)
- [Standard Plugin Development](docs/develop/dev_plugins.md)
- [API Documents](docs/apidoc/readme.md)


## Support
- [Source (In Chinese)](https://github.com/Tencent/bk-sops/tree/master)
- [Wiki (In Chinese)](https://github.com/Tencent/bk-sops/wiki) or ask for help
- [White paper(In Chinese)](http://docs.bk.tencent.com/product_white_paper/gcloud/)
- [BK forum](https://bk.tencent.com/s-mart/community)
- [BK DevOps online video tutorial](In Chinese)(https://cloud.tencent.com/developer/edu/major-100008)
- Contact us, technical exchange QQ group  
<img src="docs/resource/img/qq_group.jpg" width="250" hegiht="250" align=center />


## Contributing
If you have good ideas or suggestions, please let us know by Issues or Pull Requests and contribute to the Blue Whale Open Source Community. For Standard SOPS branch management, issues, and pr specifications, read the [Contributing Guide](docs/CONTRIBUTING.md)。

If you are interested in contributing, check out the [CONTRIBUTING.md], also join our [Tencent OpenSource Plan](https://opensource.tencent.com/contribution).

## FAQ
[FAQ (In Chinese)](docs/wiki/faq.md)


## License
Standard OPS is based on the MIT protocol. Please refer to [LICENSE](LICENSE.txt) for details.
