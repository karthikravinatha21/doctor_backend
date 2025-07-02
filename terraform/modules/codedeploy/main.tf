resource "aws_iam_role" "codedeploy" {
  name = "${var.project_name}-${var.environment}-codedeploy-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codedeploy.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "codedeploy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRole"
  role       = aws_iam_role.codedeploy.name
}

resource "aws_iam_role_policy_attachment" "codedeploy_asg" {
  policy_arn = "arn:aws:iam::aws:policy/AutoScalingFullAccess"
  role       = aws_iam_role.codedeploy.name
}

resource "aws_codedeploy_app" "app" {
  name = "${var.project_name}-${var.environment}"
  tags = var.tags
}

resource "aws_codedeploy_deployment_group" "deployment_group" {
  app_name              = aws_codedeploy_app.app.name
  deployment_group_name = "${var.project_name}-${var.environment}-group"
  service_role_arn      = aws_iam_role.codedeploy.arn

  deployment_style {
    deployment_option = "WITHOUT_TRAFFIC_CONTROL"
    deployment_type   = "IN_PLACE"
  }

  autoscaling_groups = [var.asg_name]

  # blue_green_deployment_config {
  #   deployment_ready_option {
  #     action_on_timeout = "CONTINUE_DEPLOYMENT"
  #   }

  #   green_fleet_provisioning_option {
  #     action = "COPY_AUTO_SCALING_GROUP"
  #   }

  #   terminate_blue_instances_on_deployment_success {
  #     action                           = "TERMINATE"
  #     termination_wait_time_in_minutes = 5
  #   }
  # }

  # load_balancer_info {
  #   target_group_info {
  #     name = split("/", var.target_group_arn)[length(split("/", var.target_group_arn)) - 1]
  #   }
  # }

  auto_rollback_configuration {
    enabled = true
    events  = ["DEPLOYMENT_FAILURE"]
  }

  alarm_configuration {
    enabled = true
    alarms  = ["${var.project_name}-${var.environment}-deployment-alarm"]
  }

  ec2_tag_set {
    ec2_tag_filter {
      key   = "Environment"
      type  = "KEY_AND_VALUE"
      value = var.environment
    }

    ec2_tag_filter {
      key   = "Project"
      type  = "KEY_AND_VALUE"
      value = var.project_name
    }
  }

  tags = var.tags
}

# Create CloudWatch alarm for deployment monitoring
resource "aws_cloudwatch_metric_alarm" "deployment_alarm" {
  alarm_name          = "${var.project_name}-${var.environment}-deployment-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors EC2 CPU utilization during deployments"

  dimensions = {
    AutoScalingGroupName = var.asg_name
  }

  tags = var.tags
}
