import os
import subprocess
import json
from dotenv import load_dotenv
load_dotenv()

# Read from environment
aws_account_id = os.environ["AWS_ACCOUNT_ID"]
aws_region = os.environ["AWS_REGION"]
acr_name = os.environ["ACR_NAME"]

ecr_url = f"{aws_account_id}.dkr.ecr.{aws_region}.amazonaws.com"
acr_url = f"{acr_name}.azurecr.io"

# Login to ACR and ECR
subprocess.run(["az", "acr", "login", "--name", acr_name])
subprocess.run([
    "docker", "login", "--username", "AWS",
    "--password", subprocess.check_output([
        "aws", "ecr", "get-login-password", "--region", aws_region
    ]).decode().strip(),
    ecr_url
])

# Get list of ACR repos and tags
repos = json.loads(subprocess.check_output(["az", "acr", "repository", "list", "--name", acr_name]))
for repo in repos:
    tags = json.loads(subprocess.check_output([
        "az", "acr", "repository", "show-tags",
        "--name", acr_name, "--repository", repo
    ]))
    for tag in tags:
        old_image = f"{acr_url}/{repo}:{tag}"
        new_image = f"{ecr_url}/{repo}:{tag}"
        print(f"Migrating {old_image} ➝ {new_image}")

        # Ensure ECR repo exists
        try:
            subprocess.run([
                "aws", "ecr", "describe-repositories",
                "--repository-name", repo,
                "--region", aws_region
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            subprocess.run([
                "aws", "ecr", "create-repository",
                "--repository-name", repo,
                "--region", aws_region
            ], check=True)

        subprocess.run(["docker", "pull", old_image], check=True)
        subprocess.run(["docker", "tag", old_image, new_image], check=True)
        subprocess.run(["docker", "push", new_image], check=True)

        # 🧹 Clean up to save disk space
        subprocess.run(["docker", "rmi", new_image, old_image], check=True)
