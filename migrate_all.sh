#!/bin/bash
set -e

ECR_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
ACR_URL="$ACR_NAME.azurecr.io"

echo "🔐 Logging in to Azure ACR..."
az acr login --name "$ACR_NAME"

echo "🔐 Logging in to AWS ECR..."
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_URL"

echo "📦 Fetching list of existing repositories in Azure ACR..."
acr_repos=$(az acr repository list --name "$ACR_NAME" --output tsv)

echo "📦 Fetching all ECR repositories..."
repos=$(aws ecr describe-repositories --region "$AWS_REGION" --query 'repositories[*].repositoryName' --output text)

for REPO_NAME in $repos; do
  echo "📁 Checking if '$REPO_NAME' already exists in ACR..."

  if echo "$acr_repos" | grep -q "^$REPO_NAME$"; then
    echo "✅ Repository '$REPO_NAME' already exists in ACR. Skipping..."
    continue
  fi

  echo "📦 Processing repository: $REPO_NAME"

  tags=$(aws ecr list-images \
    --repository-name "$REPO_NAME" \
    --region "$AWS_REGION" \
    --query 'imageIds[?imageTag!=`null`].imageTag' \
    --output text)

  if [ -z "$tags" ]; then
    echo "⚠️ No tagged images found in $REPO_NAME. Skipping..."
    continue
  fi

  for tag in $tags; do
    old_image="$ECR_URL/$REPO_NAME:$tag"
    new_image="$ACR_URL/$REPO_NAME:$tag"

    echo "🚀 Migrating: $old_image ➝ $new_image"

    docker pull "$old_image"
    docker tag "$old_image" "$new_image"
    docker push "$new_image"

    echo "🧹 Cleaning up local Docker images..."
    docker rmi "$new_image" "$old_image" || true
  done
done
