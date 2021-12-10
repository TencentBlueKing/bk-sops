![](https://github.com/Tencent/bk-sops/blob/master/docs/wiki/img/wiki_sops.png)
# SOPS. A mature, stable flow schedule engine!

## Introduction
>SOPS is a SaaS product in the Tencent Blueking product system. It implements cross-system automated scheduling for operation and maintenance demands. Based on a mature and stable flow schedule engine and the capability of the Blueking PaaS API Gateway to connect various system APIs of an enterprise, it can integrate the works among multiple systems within the enterprise into a task flow. It can integrate services within the Tencent Blueking system (such as: CMDB, JOB, Notification Service, etc.) and support custom plugins. The users can connect their own system and achieve one-key automated scheduling.
![](https://github.com/Tencent/bk-sops/blob/master/docs/wiki/img/wiki_product.png)

## Features
![](https://github.com/Tencent/bk-sops/blob/master/docs/wiki/img/wiki_feature.png)

## Positioning
Referring to its own development, Tencent Blueking divides the development of operation and maintenance into four stages.
- Stage 1: Relieve developers from basic operation and maintenance jobs and open the era of WEB automation
- Stage 2: Enter the era of automated scheduling. Use open APIs to connect everything
- Stage 3: Provide a full range of operation support. Use tools to lead operation and maintenance tasks.
- Stage 4: Explore the value of operation and maintenance. Use data-driven operation analysis to achieve intelligent decision and support operation

SOPS uses a powerful flow scheduling engine and integrates operation and maintenance systems to achieve the second stage of operation and maintenance, provide a full range of operation support, and lay a solid foundation for smart operation and maintenance.

## Value
The Blueking system provides basic platforms and features such as CMDB, JOB, Notification Service, etc., and assists enterprises by reliving themselves from basic operation and maintenance tasks. Some enterprises may have used other operation and maintenance system before Blueking, and it may take quite some time before transferring from the old system to Blueking products. Some enterprises can use Blueking's powerful development framework and complete operation and maintenance training system to develop a custom operation and management system.

When the systems inside the enterprise each performs its own functions, the operation and maintenance personnel can make full use of the advantages of a certain system to complete the task in a certain scenario, such as using the operation platform to execute scripts and distribute files. However, in a complex operation and maintenance scenario such as new version release, it is often necessary to perform multiple tasks in a certain order across multiple systems, such as version preparation and warning blocking before release, process start/stop and version update during release, testing, checking and removing warning blocking after release. In such scenario, the SOPS can use its cross-system scheduling capability to place these tasks in a flow template to improve release efficiency. In the next release, this flow can be reused. The SOPS can standardize and automate business releases.

SOPS shields the difference among the underlying systems, allowing the operation and maintenance personnel to hand over the daily operation and maintenance of the business to product, development, testing personnel, and achieve self-service release and modification. Through in-depth integration with Blueking PaaS, SOPS provides users with "Min-APP" and "Functional Center", so that we can further reduce the user's operating costs and increase the self-service rate.  

## Future
We hope that through open source, we can improve the cohesion of IT operation and maintenance community and bring more sense of belonging and interactions to the community; We believe that your participation will make this community more powerful and more extraordinary.
![](https://github.com/Tencent/bk-sops/blob/master/docs/wiki/img/wiki_future.png)

## About the open source license
SOPS uses the MIT open source license. MIT is similar to BSD, it has a high license compatibility. The author only keeps the copyright of the software and puts very limited restriction on the software. The user must include the original license in the release version, whether the software is released in binary or in source code form.

## Discussion is welcomed
![](https://github.com/Tencent/bk-sops/blob/master/docs/wiki/img/wiki_communication.png)


## Tencent Blueking
The Tencent Blueking system consists of platform-level products and universal SaaS services. The platforms include control platform, CMDB, JOB, PaaS platform, etc. The universal SaaS includes node management, SOPS, log query, Blueking monitoring, failure correction, etc. It provides one-stop technical solutions for users on various clouds (public, private, and hybrid clouds) with different scenarios and different demands.

Tencent Blueking product structure - Community Edition  
![](https://github.com/Tencent/bk-sops/blob/master/docs/wiki/img/wiki_blueking.png)

Description:  
1. Tencent Blueking is an integrated system, which means each product in the system has to work in conjunction to bring out the system's maximum value.    
2. In the community edition, the currently open source products are: CMDB, PaaS Platform, and SOPS;  
3. CMDB and PaaS platform can be deployed and used independently as atomic platforms;  
4. The SOPS must be used in conjunction with the whole system.

Open source product links  
SOPS: https://github.com/Tencent/bk-sops  
PaaS Platform: https://github.com/Tencent/bk-PaaS  
CMDB: https://github.com/Tencent/bk-cmdb  
Container Service Platform: https://github.com/Tencent/bk-bcs  
