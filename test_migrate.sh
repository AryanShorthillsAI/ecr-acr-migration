#!/bin/bash
set -e

# Check required variables
if [[ -z "$AWS_ACCOUNT_ID" || -z "$AWS_REGION" || -z "$ACR_NAME" || -z "$REPO_NAME" || -z "$IMAGE_TAG" ]]; then
  echo "❌ Required environment variables not set."
  echo "Make sure AWS_ACCOUNT_ID, AWS_REGION, ACR_NAME, REPO_NAME, and IMAGE_TAG are set."
  exit 1
fi

ECR_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
ACR_URL="$ACR_NAME.azurecr.io"

old_image="$ECR_URL/$REPO_NAME:$IMAGE_TAG"
new_image="$ACR_URL/$REPO_NAME:$IMAGE_TAG"

echo "📦 Target Image: $old_image ➝ $new_image"

echo "🔐 Logging in to Azure ACR..."
az acr login --name "$ACR_NAME"

echo "🔐 Logging in to AWS ECR..."
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_URL"

echo "🔍 Pulling image from ECR..."
docker pull "$old_image"

echo "🔄 Tagging image for ACR..."
docker tag "$old_image" "$new_image"

echo "📤 Pushing to ACR..."
docker push "$new_image"

echo "🧹 Cleaning up local Docker images..."
docker rmi "$new_image" "$old_image" || true

echo "✅ Migration complete for $IMAGE_TAG"
