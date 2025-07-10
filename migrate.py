import boto3
import subprocess
import logging
import os
from botocore.exceptions import ClientError


# ============ CONFIGURATION (Constants) ============ 
LOG_FILE = "ecr_to_acr_migration.log"

# ============ SETUP LOGGING ============ 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)

def check_acr_exists(acr_name, subscription_id):
    try:
        result = subprocess.run(
            ["az", "acr", "show", "--name", acr_name, "--subscription", subscription_id],
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError:
        logging.critical(f"❌ ACR '{acr_name}' not found in subscription '{subscription_id}'")
        return False


def get_ecr_credentials(ecr_client):
    """Gets temporary ECR login credentials."""
    try:
        logging.info("Getting ECR authentication token...")
        response = ecr_client.get_authorization_token()
        auth_data = response['authorizationData'][0]
        token = auth_data['authorizationToken']
        # The username is always 'AWS' for ECR, and the password is the token
        return "AWS", token
    except ClientError as e:
        logging.error(f"❌ Could not get ECR credentials: {e}")
        raise

def get_all_repositories(ecr_client):
    """Gets a list of all repository names from ECR."""
    repos = []
    paginator = ecr_client.get_paginator('describe_repositories')
    try:
        for page in paginator.paginate():
            for repo in page['repositories']:
                repos.append(repo['repositoryName'])
    except ClientError as e:
        logging.error(f"❌ Could not list ECR repositories: {e}")
        raise
    return repos

def get_image_ids(repository_name, ecr_client):
    """Gets all image identifiers (tags and digests) for a repository."""
    image_ids = []
    paginator = ecr_client.get_paginator('list_images')
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

def migrate_image_via_acr_import(repo, image_id, ecr_user, ecr_pass, ecr_uri, acr_name):
    """Migrates a single image using 'az acr import', only if it has a tag."""
    tag = image_id.get('imageTag')

    if not tag:
        logging.info(f"ℹ️ Skipping untagged image in {repo} (digest: {image_id.get('imageDigest')}). Only tagged images are migrated.")
        return

    # If we reach here, it means 'tag' exists.
    source_image = f"{ecr_uri}/{repo}:{tag}"
    target_image = f"{repo}:{tag}"
    logging.info(f" Importing tagged image {source_image} to {acr_name}...")

    command = [
        "az", "acr", "import",
        "--name", acr_name,
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
        # Retrieve environment variables inside main
        aws_region = os.environ.get("AWS_REGION")
        ecr_account_id = os.environ.get("ECR_ACCOUNT_ID")
        acr_name = os.environ.get("ACR_NAME")
        azure_subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")

        if not check_acr_exists(acr_name, azure_subscription_id):
            raise Exception("Aborting migration due to missing ACR.")

        # Check for mandatory variables
        if not all([aws_region, ecr_account_id, acr_name, azure_subscription_id]):
            raise ValueError("AWS_REGION, ECR_ACCOUNT_ID, ACR_NAME, and AZURE_SUBSCRIPTION_ID environment variables must be set.")

        ecr_uri = f"{ecr_account_id}.dkr.ecr.{aws_region}.amazonaws.com"
        
        # Initialize ECR client here
        ecr_client = boto3.client('ecr', region_name=aws_region)

        # Set the Azure subscription context
        logging.info(f"Setting Azure subscription to: {azure_subscription_id}")
        subprocess.run(["az", "account", "set", "--subscription", azure_subscription_id], check=True, capture_output=True, text=True)

        ecr_user, ecr_pass = get_ecr_credentials(ecr_client) # Pass ecr_client
        repos = get_all_repositories(ecr_client) # Pass ecr_client
        logging.info(f"Found {len(repos)} repositories in ECR.")

        for repo in repos:
            logging.info(f"Processing repository: {repo}")
            
            subprocess.run(
                ["az", "acr", "repository", "create", "--name", acr_name, "--repository", repo],
                capture_output=True,
                text=True
            )

            image_ids = get_image_ids(repo, ecr_client) # Pass ecr_client
            if not image_ids:
                logging.info(f"No images found in {repo}, skipping.")
                continue
            
            logging.info(f"Found {len(image_ids)} images in {repo}. Starting migration...")
            for image_id in image_ids:
                migrate_image_via_acr_import(repo, image_id, ecr_user, ecr_pass, ecr_uri, acr_name) # Pass ecr_uri, acr_name

    except Exception as e:
        logging.critical(f"A critical error occurred during the migration process: {e}")

if __name__ == "__main__":
    main()