#!/bin/bash
set -e

ECR_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
ACR_URL="$ACR_NAME.azurecr.io"

echo "📦 Target ECR repository: $REPO_NAME"

echo "🔐 Logging in to Azure ACR..."
az acr login --name "$ACR_NAME"

echo "🔐 Logging in to AWS ECR..."
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_URL"

echo "📦 Fetching image tags from ECR repo: $REPO_NAME"
tags=$(aws ecr list-images --repository-name "$REPO_NAME" --region "$AWS_REGION" --query 'imageIds[*].imageTag' --output text)

# Skip list
skip_tags=("qwen-sagemaker-training" "qwen-sagemaker-training-2")

for tag in $tags; do
  if [ "$tag" = "None" ]; then
    echo "⚠️ Skipping untagged image..."
    continue
  fi

  # Skip manually excluded tags
  if [[ " ${skip_tags[@]} " =~ " ${tag} " ]]; then
    echo "⚠️ Skipping excluded tag: $tag"
    continue
  fi

  old_image="$ECR_URL/$REPO_NAME:$tag"
  new_image="$ACR_URL/$REPO_NAME:$tag"

  echo "🔍 Checking if $new_image already exists in ACR..."
  if az acr repository show-manifests --name "$ACR_NAME" --repository "$REPO_NAME" --query "[?tags[?contains(@, '$tag')]]" --output tsv | grep -q "$tag"; then
    echo "✅ $new_image already exists. Skipping..."
    continue
  fi

  echo "🚀 Migrating: $old_image ➝ $new_image"
  docker pull "$old_image"
  docker tag "$old_image" "$new_image"
  docker push "$new_image"

  echo "🧹 Cleaning up local Docker images..."
  docker rmi "$new_image" "$old_image" || true
done
