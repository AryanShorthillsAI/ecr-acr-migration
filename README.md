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
    - `AWS Region of the ECR registry`
5.  **Click "Run workflow"**.

The workflow will start, and you can monitor its progress in the Actions tab. A log file (`ecr_to_acr_migration.log`) will also be created on the runner with detailed information about the migration process.
