resource "aws_ecr_repository" "chatbot_api_images" {
  name = "chatbot_api_images"

}

output "ecr_repository_url" {
    value = aws_ecr_repository.chatbot_api_images.repository_url
    description = "Use this url to push the api's Docker images.\nYou can import it in the EC2 instance.\n`docker push {url}`.\n More info: https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html"
}