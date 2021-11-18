# Issues Guide

## BUG Ticket
If you encounter a bug in SOPS, you can submit the bug to the community by [Submit Issue] (https://github.com/Tencent/bk-sops/issues/new)
to locate and fix the bug. You also need to provide more specific information to help the community locate and fix the problem.

The community needs you to provide the following basic information.
* The specifics of the issue. It might be a log or a screenshot of the error message from the web page.
* The version number you are currently using.
* The process of reproducing the issue.

For more complex issues, please provide more detailed information in time. The more information you provide, the faster we can locate and solve the issues.

The community has a template for you to fill out information regarding the issue:

```markdown
Issue description
=======
<Write your issue description here>


Reproducing the issue
=======
<The methods or steps required to reproduce the issue>


**Important Reminder**: Please try deploying the latest version first (Release list: https://github.com/Tencent/bk-sops/releases). If the issue cannot be reproduced in the latest version, then it means the issue has been fixed.


Key information
=======

**Important Reminder**: such key information will help us locate the issue as soon as possible

Please provide the following information:

 - [x] bk_sops   version (release version number or git tag): `<Example: V3.1.32-ce or git sha. Please don't use vague descriptions such as "latest version" or "current version">`
 - [ ] Blueking PaaS   version: `<Example: PaaS 3.0.58, PaaSAgent 3.0.9>`
 - [ ] bk_sops exception log
```

If you are not certain it's a bug or a feature, you can also submit an issue so we can take a look at it.

## BUG fixing
Once the community confirms that issue you submitted is a bug, there are many ways to fix the issue:
  - If you are familiar with the source code, you can fix the bug by yourself and submit the modified code to the community through PR. These codes will be merged into the main repository after review.
  - If you are familiar with python and vue, but you don't know how to fix the bug by yourself, the community can provide assist to help you fix the issue. When the issue is fixed, it will be merged into the main repository through PR.
  - Ask the community to fix the bug.

When the bug is fixed, you can deploy the fixed branch on your own machine or you can wait until the new version is released.

# Submit a request
If you find that the current SOPS version doesn't meet your demands, feel free to [create an issue] (https://github.com/Tencent/bk-sops/issues/new)
and tell us your request. Your request should be:
- able to be applied in a universal scenario.
- within the scope of application of the SOPS product.

For simple requests, you just need to describe it in the issue.

If your request is more complicated, it would be better if you can give an implementation plan on how this request should be fulfilled. The following is some of the information you can provide:
* The context of the request;
* A design solution on how to implement the feature;
* The components that need to be adjusted;
* The code of the feature;

After receiving your request, the community will review your request and solution. The workflow for processing requests is:

![Request Processing Workflow] (img/wiki_demand_flow.png)
