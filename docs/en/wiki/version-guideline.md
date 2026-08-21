# Version Guideline
SOPS version number is divided into three parts and followed by a version type. The format is {major}.{minor}.{patch}[-{pre-release-type}.{pre-release}]. The version number is managed according to the project release train.

Version number example: V3.1.32-beta

* Part 1: 
    3 represents the major version of SOPS. The current major version is 3. This number only changes when SOPS undergoes major version change.
* Part 2: 
    1 represents the iteration cycle of a version, which includes major structural adjustments or updates to dependent Blueking plugin platform. This number changes when the iteration cycle evolves forward.
* Part 3: 
    32 represents the current iteration cycle. The current iteration cycle may include a feature or multiple bugfixes. This number changes according to development progress. Generally, this number changes every 1 to 3 weeks.
* pre-release-type: 
    - alpha means internal test version. These releases should only be used by developers who are participating in this project. During alpha, we are constantly adding new features and fixing known bugs.
    - beta means open test version. This version should not be used by stable projects. During beta, new features will be added when appropriate, and known bugs will be fixed.
    - rc means release candidate version. This version can be used by all projects. During rc, no new feature will be added, and only bugs will be fixed. If no more bugs are found in the rc version, this version will be converted to release directly.
* pre-release:
    Decimal number. Increases after each version release.
