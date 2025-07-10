import boto3
import subprocess
import logging
import os
from botocore.exceptions import ClientError


# ============ CONFIGURATION (from Environment Variables) ============
AWS_REGION = os.environ.get("AWS_REGION")
ECR_ACCOUNT_ID = os.environ.get("ECR_ACCOUNT_ID")
ACR_NAME = os.environ.get("ACR_NAME")

# Check for mandatory variables
if not all([AWS_REGION, ECR_ACCOUNT_ID, ACR_NAME]):
    raise ValueError("AWS_REGION, ECR_ACCOUNT_ID, and ACR_NAME environment variables must be set.")

ECR_URI = f"{ECR_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com"
LOG_FILE = "ecr_to_acr_migration.log"

# ============ SETUP LOGGING ============
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)

# ============ INIT AWS ============
ecr = boto3.client('ecr', region_name=AWS_REGION)

def get_ecr_credentials():
    """Gets temporary ECR login credentials."""
    try:
        logging.info("Getting ECR authentication token...")
        response = ecr.get_authorization_token()
        auth_data = response['authorizationData'][0]
        token = auth_data['authorizationToken']
        # The username is always 'AWS' for ECR, and the password is the token
        return "AWS", token
    except ClientError as e:
        logging.error(f"❌ Could not get ECR credentials: {e}")
        raise

def get_all_repositories():
    """Gets a list of all repository names from ECR."""
    repos = []
    paginator = ecr.get_paginator('describe_repositories')
    try:
        for page in paginator.paginate():
            for repo in page['repositories']:
                repos.append(repo['repositoryName'])
    except ClientError as e:
        logging.error(f"❌ Could not list ECR repositories: {e}")
        raise
    return repos

def get_image_ids(repository_name):
    """Gets all image identifiers (tags and digests) for a repository."""
    image_ids = []
    paginator = ecr.get_paginator('list_images')
    try:
        for page in paginator.paginate(repositoryName=repository_name):
            image_ids.extend(page['imageIds'])
    except ClientError as e:
        # Handle repository not found gracefully
        if e.response['Error']['Code'] == 'RepositoryNotFoundException':
            logging.warning(f"⚠️ Repository {repository_name} not found in ECR.")
            return []
        else:
            logging.error(f"❌ Could not list images for repo {repository_name}: {e}")
            raise
    return image_ids

def migrate_image_via_acr_import(repo, image_id, ecr_user, ecr_pass):
    """Migrates a single image using 'az acr import', only if it has a tag."""
    tag = image_id.get('imageTag')

    if not tag:
        logging.info(f"ℹ️ Skipping untagged image in {repo} (digest: {image_id.get('imageDigest')}). Only tagged images are migrated.")
        return

    # If we reach here, it means 'tag' exists.
    source_image = f"{ECR_URI}/{repo}:{tag}"
    target_image = f"{repo}:{tag}"
    logging.info(f" Importing tagged image {source_image} to {ACR_NAME}...")

    command = [
        "az", "acr", "import",
        "--name", ACR_NAME,
        "--source", source_image,
        "--image", target_image,
        "--username", ecr_user,
        "--password", ecr_pass,
        "--force" # Overwrite the tag if it already exists in ACR
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logging.info(f"✅ Successfully imported as {target_image}")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Failed to import {source_image}.")
        # Check for a common error when the repo doesn't exist in ACR
        if "repository not found" in e.stderr:
            logging.error("   Hint: The repository might not exist in ACR. Trying to create it...")
            # The main loop already attempts to create the repo, but we can be more explicit here.
            # For simplicity, we'll just log the hint. A more advanced script could retry after creation.
        logging.error(f"   Return Code: {e.returncode}")
        logging.error(f"   Stderr: {e.stderr}")


def main():
    """Main function to orchestrate the ECR to ACR migration."""
    try:
        ecr_user, ecr_pass = get_ecr_credentials()
        repos = get_all_repositories()
        logging.info(f"Found {len(repos)} repositories in ECR.")

        for repo in repos:
            logging.info(f"Processing repository: {repo}")
            
            # Proactively create the repository in ACR to avoid import errors.
            # This command is idempotent; it does nothing if the repo already exists.
            subprocess.run(
                ["az", "acr", "repository", "create", "--name", ACR_NAME, "--repository", repo],
                capture_output=True,
                text=True
            )

            image_ids = get_image_ids(repo)
            if not image_ids:
                logging.info(f"No images found in {repo}, skipping.")
                continue
            
            logging.info(f"Found {len(image_ids)} images in {repo}. Starting migration...")
            for image_id in image_ids:
                migrate_image_via_acr_import(repo, image_id, ecr_user, ecr_pass)

    except Exception as e:
        logging.critical(f"A critical error occurred during the migration process: {e}")

if __name__ == "__main__":
    main()
