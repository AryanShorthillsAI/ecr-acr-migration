# ECR to ACR Migration Solution

This project provides a fully automated solution for migrating Docker container images from Amazon Elastic Container Registry (ECR) to Azure Container Registry (ACR).

It uses a Python script orchestrated by a GitHub Actions workflow to perform a server-side import (`az acr import`), which is the most efficient and cost-effective method. This approach avoids pulling images to the local disk, saving significant disk space and network bandwidth.

## Features

- **Automated Migration**: Trigger the entire migration process with a single click from the GitHub Actions tab.
- **Efficient & Cost-Effective**: Uses `az acr import` for a direct, server-side data transfer from AWS to Azure.
- **Zero Local Disk Usage**: The runner VM does not store the container images, making it suitable for runners with limited disk space.
- **Maintains Structure**: Replicates the ECR repository structure and image tags in ACR.
- **Handles Untagged Images**: Intelligently creates a new, stable tag for untagged (digest-only) images to ensure they are migrated.
- **Secure**: Uses GitHub Secrets to store sensitive credentials for AWS and Azure.

## How It Works

1.  **GitHub Actions Workflow**: The process is initiated by the `.github/workflows/migrate-images.yml` workflow. It can be triggered manually and accepts the AWS Account ID, ACR Name, and AWS Region as inputs.
2.  **Authentication**: The workflow securely logs into both Azure and AWS using credentials stored in GitHub Secrets.
3.  **Python Script (`migrate.py`)**:
    - The script is executed on a self-hosted runner.
    - It lists all repositories in the specified ECR registry.
    - For each repository, it lists all images (both tagged and untagged).
    - It then calls `az acr import`, providing temporary ECR credentials. This command instructs the ACR service to pull the image directly from ECR.
    - If an image in ECR is untagged, a new tag is created based on its digest (e.g., `sha256-a1b2c3...`) to allow it to be imported into ACR.

## Prerequisites

1.  **Azure Service Principal**: An Azure Service Principal with the `AcrPush` role on the target Azure Container Registry.
2.  **AWS IAM User**: An AWS IAM User with `ecr:GetAuthorizationToken` and `ecr:DescribeRepositories` permissions.
3.  **GitHub Self-Hosted Runner**: A self-hosted runner configured on an Azure VM with the following software installed:
    - Python 3.8+
    - Azure CLI
    - AWS CLI v2
4.  **GitHub Secrets**: The following secrets must be configured in your GitHub repository settings (`Settings` > `Secrets and variables` > `Actions`):
    - `AZURE_CREDENTIALS`: The JSON output from creating your Azure Service Principal.
    - `AWS_ACCESS_KEY_ID`: The access key for your AWS IAM user.
    - `AWS_SECRET_ACCESS_KEY`: The secret access key for your AWS IAM user.

## How to Use

1.  **Navigate to the Actions tab** in your GitHub repository.
2.  **Select the "Migrate ECR Images to ACR"** workflow from the list on the left.
3.  **Click the "Run workflow"** dropdown button on the right.
4.  **Enter the required inputs**:
    - `AWS Account ID for ECR`
    - `Name of the Azure Container Registry`
    
## ECR Images Architecture Support Table

**Account ID:** 460719294386  
**Region:** ap-northeast-3  
**Profile:** import-project-aryan  

## Summary
- **Total Images:** 64
- **Repositories with Images:** 8
- **Supported Architectures:** linux/amd64, linux/arm64

---

## Detailed Image Architecture Table

| Repository | Image Tag | Image URI | Architecture | Manifest Type | Size (GB) | Pushed Date |
|------------|-----------|-----------|--------------|---------------|-----------|-------------|
| **geneconnect-backend** | latest | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/geneconnect-backend@sha256:e3ab031dc90e92941e22cc11f0b0b33690c84ef152a793585236fad1bc495a20 | linux/amd64 | single-arch | 3.14 | 2025-06-23 |
| **geneconnect-backend** | test-fix1 | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/geneconnect-backend@sha256:f7a4fd25e3f150d6f22e0795b786c0558f6616bb1453193f4e4ce8efcab53e19 | linux/amd64 | single-arch | 6.07 | 2025-06-19 |
| **geneconnect-backend** | v1.0.1 | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/geneconnect-backend@sha256:be3f39cf4da1a1d7812aacdab19809f32dd8da582b209602e2ef7f5616a598c5 | linux/amd64 | single-arch | 9.10 | 2025-05-22 |
| **geneconnect-doctor** | latest | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/geneconnect-doctor@sha256:86cd2cac7ddc95e243e71ff517b19d70a4e041e3c24348de96d694df4de1de93 | linux/amd64 | single-arch | 0.05 | 2025-06-22 |
| **geneconnect-doctor** | v1.0.1 | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/geneconnect-doctor@sha256:a1c915dd5923ae21d3ef72fc36fbe2f1b08f465e5ee03affebcd3e76de60bee5 | linux/amd64 | single-arch | 0.29 | 2025-05-27 |
| **geneconnect-frontend** | latest | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/geneconnect-frontend@sha256:ea06e96d182fa0e5d7db7c4540a0695dd5b3e77dc7d52d3f7cb72c64e537f57d | linux/amd64 | single-arch | 0.05 | 2025-06-22 |
| **geneconnect-frontend** | v1.0.1 | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/geneconnect-frontend@sha256:9c19ed683f971b69399723bf1b1b191257a18ed7c04b452e11c64201c9d51c00 | linux/amd64 | single-arch | 0.23 | 2025-05-27 |
| **maruti** | elasticsearch-8.11.3 | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/maruti@sha256:dfd29b525bbcab4db2a4331ceec6afad439b575876a33031d20d28066636ddc8 | linux/amd64 | single-arch | 0.42 | 2025-04-09 |
| **maruti** | maruti-backend | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/maruti@sha256:1482d8354754f37cb532b1e16e039057a15f66f05da45fe8a07a51afe89ceda5 | **linux/arm64** | multi-arch | 0.42 | 2025-04-09 |
| **maruti** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/maruti@sha256:6c49417073bfaeba90c1b1f37db62f817ca44e06ac9d9c49770802cc3b86c405 | linux/amd64 | single-arch | 0.00 | 2025-04-09 |
| **maruti** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/maruti@sha256:a319bd7e48de2ede5ce140f019da90ccde05c0e12761fa12dc731ac0acc0315a | linux/amd64 | single-arch | 0.42 | 2025-04-09 |
| **maruti** | maruti-frontend | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/maruti@sha256:68daf205f2e0a4d9175f4fee3a5462741d66b76df48d08b3964d457532f96805 | **linux/arm64** | multi-arch | 0.41 | 2025-04-09 |
| **maruti** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/maruti@sha256:bd90a1129544f94e8f4b6540c7e5d31d95b81f20fd094db6ee02048ca94270de | linux/amd64 | single-arch | 0.00 | 2025-04-09 |
| **maruti** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/maruti@sha256:3df16f0b03e85aa3991478774924329df69761ce9c615c3b7ee599008134501a | linux/amd64 | single-arch | 0.41 | 2025-04-09 |
| **nifi** | v1.0.1 | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/nifi@sha256:5c714fdb2702abbf7c5afaae377229a2ffe247fb31131737cd7aa24bd5ea5780 | linux/amd64 | single-arch | 2.26 | 2025-06-23 |
| **pedigreevision** | qwen-sagemaker-training-2 | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:b82479a8c7c1882ee1f9bb2d8ac2d72355912aa35c9e5a414feb21d0b4e369b9 | linux/amd64 | multi-arch | 11.81 | 2025-05-29 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:69773a9a77a9e9f54380733863c919e4a83e0ac5a092f2360b91f0f01ca88fc1 | linux/amd64 | single-arch | 11.81 | 2025-05-29 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:43c7947cb14f2811d7585d3d54bf51dbdbc6a7c0dab2b6699ba02b8a57da1b56 | linux/amd64 | single-arch | 0.00 | 2025-05-29 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:0e774744b2b17c3598706dd470a1b1833fafa581e4341c62f0112569c8532b31 | linux/amd64 | multi-arch | 10.10 | 2025-05-27 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:1e97392689abb05e048510b1c07817e75eeac1c83e54fe92102c2ccaddefc18d | linux/amd64 | single-arch | 10.10 | 2025-05-27 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:a9d16b04765e231a552b84734d2dad2831bf70346ab44fe411b9da12b3230fad | linux/amd64 | single-arch | 0.00 | 2025-05-27 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:51f15962470ac019d342044f9e9334bb215eeb6118804ff774bdfdbb0066bfbc | linux/amd64 | multi-arch | 10.06 | 2025-05-27 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:7feaa9d79f42dea24e82963ccab52ab9c87ab1950227cf5861b060c82d63f655 | linux/amd64 | single-arch | 10.06 | 2025-05-27 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:fe5e0ec25395d57f1c3ec6d2708f9e47927eb5fc23566ec47eae60d93206b3a5 | linux/amd64 | single-arch | 0.00 | 2025-05-27 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:60ed8bcf84c8d02af142872d0ed6ec034776e0395c4c0ab32a62174687449304 | linux/amd64 | multi-arch | 3.87 | 2025-05-27 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:75772178eb1af401eae504e62dfb9310907a68172b0293076049d6db295717a4 | linux/amd64 | single-arch | 0.00 | 2025-05-27 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:00dcbae30a90140d51f15fa8ff64aacea277b06a165055fe1a42c3fe2fdceb33 | linux/amd64 | single-arch | 3.87 | 2025-05-27 |
| **pedigreevision** | qwen-sagemaker-training | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:7f07fecf6d586dd2900fc28a68ebc11c05aff1567e1578883ffea67cac46e1dc | linux/amd64 | multi-arch | 14.91 | 2025-05-27 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:4094461057002c89820ce7fa1d2529e8bd7039afe9134fa5a8ebad6522bc43ba | linux/amd64 | single-arch | 0.00 | 2025-05-27 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:729cd9cf3091701605285ba032adcca12776eea43f50641aee2f7175b0c08bb1 | linux/amd64 | single-arch | 14.91 | 2025-05-27 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:246088363f9016917ae801413251d3cd302cccc947105ef57d05d1da72b07107 | linux/amd64 | multi-arch | 11.67 | 2025-05-25 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:ef3d587b824cbcd7efc6914562b3da231b50b116f6cb6e7a8422e0b7085b5522 | linux/amd64 | single-arch | 0.00 | 2025-05-25 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:de126291b4579f6973ca2c1dfc7a0b08cbd5d8daa878334754dc25229a18c042 | linux/amd64 | single-arch | 11.67 | 2025-05-25 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:2afcb41510c1ac57c44396ff08d4e9240aef467e774510a02c02d64ab80c1c29 | linux/amd64 | multi-arch | 19.73 | 2025-05-25 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:c0da5ae6e5b643f21d4e47d30797eddae59c295df4a05bbda0d5675836ec194e | linux/amd64 | single-arch | 19.73 | 2025-05-25 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:d86f46999de6bba3e1a115aa324b953dd0be2b3e80314cdbf40708cae6dbe179 | linux/amd64 | single-arch | 0.00 | 2025-05-25 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:6551ba46fc8fe78baac43a10132f19ec4bf89a5ed768c9b756cd62f2638fecf2 | linux/amd64 | multi-arch | 16.04 | 2025-05-22 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:bd1a75541f432b8d0c6ae56f74f04eec9c5530da863dc348f14c751897ca7172 | linux/amd64 | single-arch | 0.00 | 2025-05-22 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:1343d36d25b4aeffdb188e4d0520e67badaf1e19010d586c5812d700631b7d38 | linux/amd64 | single-arch | 16.04 | 2025-05-22 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:596988a7034e6d06dc3e0df00f0de5e079336b7051b4e26a8fe3b9ccfad79b05 | linux/amd64 | multi-arch | 16.27 | 2025-05-22 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:1a8441a577383b2a2a5f9c653a3a34f8256577e93357f1769ac8d0042e930578 | linux/amd64 | single-arch | 0.00 | 2025-05-22 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:622f29832654543af68f835e23e553e4ac0f653b51ed2864c899069e9365a999 | linux/amd64 | single-arch | 16.27 | 2025-05-22 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:f2d3006c2611945114a48f080659cbec69d81ed1e485117e9905b2f9653bdcfb | linux/amd64 | multi-arch | 14.76 | 2025-05-22 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:46f4928d93077ab3f1c1cad192931e0c5a3620d4b2959b168f9da441ecbb9384 | linux/amd64 | single-arch | 0.00 | 2025-05-22 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:c62c24d4844c0267d4342ff426aebac4424bfdcaf1fbcca6e03b959b30d398ef | linux/amd64 | single-arch | 14.76 | 2025-05-22 |
| **pedigreevision** | backendimageV1.0.1 | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:f12a662c3fb2c2af465ae729e5929535f9f20cc7bb090be2b727921970f2b66a | linux/amd64 | single-arch | 7.87 | 2025-04-01 |
| **pedigreevision** | model-image | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:c0cc4f6ac6a7f343ee94c0dcf20964313550ca756e6772457fd2167ea2f2d733 | linux/amd64 | multi-arch | 4.20 | 2025-04-01 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:e84da017bf146834ae26b263d9bc809745e1e7d38014d0c783c48f868ab85eef | linux/amd64 | single-arch | 0.00 | 2025-04-01 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:768f10ed8ce5b5a77fdb862190295d97b94b822e23b41b8295a5d6db17afdb7f | linux/amd64 | single-arch | 4.20 | 2025-04-01 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:392cb838e21b5175572b308e0856dc7562e139c58f0f009b42194c3b342294f3 | linux/amd64 | multi-arch | 4.20 | 2025-04-01 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:8910e551cf69f6b9a274886856aa2fdd7c0baf42e7bebc594a0a5b64e0e4a6b9 | linux/amd64 | single-arch | 0.00 | 2025-04-01 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:6f5a9ac53def226347de57da9664a94eb520628d991461fa1e0e08555dea4405 | linux/amd64 | single-arch | 4.20 | 2025-04-01 |
| **pedigreevision** | frontendimageV1.0.1 | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:0eaa1891bde9a0d95a8819eecc5c2a516b10d7d3f353d1a7d22e2a58f949347b | linux/amd64 | single-arch | 0.07 | 2025-03-31 |
| **pedigreevision** | backend-image | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:8bc94079b6751d88f7ae035a3e84fad0818b95a009beba6792327c33bb4682d2 | linux/amd64 | single-arch | 9.01 | 2025-03-28 |
| **pedigreevision** | gunicorn-be | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:8402dd929a3db0732f3c45635d89f1d48cbd1c83cd5a0996530b3a831ebdd3d2 | linux/amd64 | single-arch | 8.95 | 2025-03-28 |
| **pedigreevision** | updated-backend-image | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:9648eba3e41044de667962be082f437ff61b008ad80b5a67cb13d60deca133ae | linux/amd64 | single-arch | 9.02 | 2025-03-28 |
| **pedigreevision** | frontend-image | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:ef204a2f7a4c1e4869648bda84d4c6f68a8b9cf34a7bb65774000fbfb0a7613f | linux/amd64 | single-arch | 0.07 | 2025-03-27 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:0f426c7ebd33e60139cf47946906b303e0b78c1f0a7ac36f704d2e43929f0d58 | linux/amd64 | multi-arch | 4.15 | 2025-03-26 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:b7da25f9574723dccd8ddbcd549b8b551584b765029ccbc0adde0e0aa861ee6b | linux/amd64 | single-arch | 0.00 | 2025-03-26 |
| **pedigreevision** | untagged | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision@sha256:c1e5817a90c8bcd800ba85a31d696991da44f8b97dc9274b73d6566b5f5b9fdd | linux/amd64 | single-arch | 4.15 | 2025-03-26 |
| **pedigreevision-backend** | docker-env--72afa1d | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision-backend@sha256:ea949577a430cc58488879a6012dff0ef14868a57f7237ef75684ccee6114c56 | linux/amd64 | single-arch | 3.67 | 2025-04-16 |
| **pedigreevision-backend** | dev--2465d57 | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision-backend@sha256:5fee86f9b745fa33e9381da477442426a9d0726823d725548cdf4e444aaea757 | linux/amd64 | single-arch | 3.66 | 2025-04-09 |
| **pedigreevision-backend** | 858-dockerdeploy--2465d57 | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision-backend@sha256:653cdad9abf276f8b75afdd2440768e0a8c84585a96c2d15c2a7120e63ca4792 | linux/amd64 | single-arch | 3.66 | 2025-04-07 |
| **pedigreevision-fe** | latest | 460719294386.dkr.ecr.ap-northeast-3.amazonaws.com/pedigreevision-fe@sha256:e66f107cf488be66f1aa535fb8f6ad000885d210466bcbce55b6bc8c1a9c7d02 | linux/amd64 | single-arch | 0.08 | 2025-05-28 |

---

## Architecture Summary by Repository

| Repository | Total Images | linux/amd64 | linux/arm64 | Notes |
|------------|--------------|-------------|-------------|-------|
| **geneconnect-backend** | 3 | ✅ 3 | ❌ 0 | All AMD64 |
| **geneconnect-doctor** | 2 | ✅ 2 | ❌ 0 | All AMD64 |
| **geneconnect-frontend** | 2 | ✅ 2 | ❌ 0 | All AMD64 |
| **maruti** | 7 | ✅ 5 | ✅ 2 | Mixed architectures |
| **nifi** | 1 | ✅ 1 | ❌ 0 | AMD64 only |
| **pedigreevision** | 45 | ✅ 45 | ❌ 0 | All AMD64 |
| **pedigreevision-backend** | 3 | ✅ 3 | ❌ 0 | All AMD64 |
| **pedigreevision-fe** | 1 | ✅ 1 | ❌ 0 | AMD64 only |

## Key Findings

1. **ARM64 Support**: Only the `maruti` repository contains ARM64 images:
   - `maruti-backend` (tagged)
   - `maruti-frontend` (tagged)

2. **Dominant Architecture**: 97% of images are Linux/AMD64

3. **Multi-Architecture Images**: Several images use OCI image index format for multi-platform support

4. **Repository Distribution**: 8 repositories contain images, 3 are empty

---

*Generated on: 2025-07-14*  
*Total Storage Used: ~500+ GB across all images*

    - `AWS Region of the ECR registry`
5.  **Click "Run workflow"**.

The workflow will start, and you can monitor its progress in the Actions tab. A log file (`ecr_to_acr_migration.log`) will also be created on the runner with detailed information about the migration process.
