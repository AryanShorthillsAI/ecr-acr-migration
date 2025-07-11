#!/bin/bash
set -e

REPO_NAME="geneconnect-doctor"  # ✅ Change to your ECR repo name for testing

ECR_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
ACR_URL="$ACR_NAME.azurecr.io"

echo "🔐 Logging in to Azure ACR..."
az acr login --name "$ACR_NAME"

echo "🔐 Logging in to AWS ECR..."
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_URL"

echo "📦 Fetching image tags from ECR repo: $REPO_NAME"
tags=$(aws ecr list-images --repository-name "$REPO_NAME" --region "$AWS_REGION" --query 'imageIds[*].imageTag' --output text)

for tag in $tags; do
  if [ "$tag" = "None" ]; then
    echo "⚠️ Skipping untagged image..."
    continue
  fi

  old_image="$ECR_URL/$REPO_NAME:$tag"
  new_image="$ACR_URL/$REPO_NAME:$tag"

  echo "🚀 Migrating: $old_image ➝ $new_image"

  docker pull "$old_image"
  docker tag "$old_image" "$new_image"
  docker push "$new_image"

  echo "🧹 Cleaning up local Docker images..."
  docker rmi "$new_image" "$old_image" || true
done
