output "instance_id" {
  value = aws_instance.pls_g5.id
}

output "public_ip" {
  value = aws_instance.pls_g5.public_ip
}
