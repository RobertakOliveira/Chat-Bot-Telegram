resource "aws_cloudwatch_dashboard" "chatbot_dashboard" { //cria um recurso do tipo dashboard no cloudwatch
  dashboard_name = "chatbot-telegram-dashboard-${var.owner_tag}" //da o nome visível no console aws (deve ser único)

  dashboard_body = jsonencode({ //estruturação do dashboard em JSON
    widgets = [ //criação dos widgets com tipo, tamanho e propriedades

    //Widget 1 - CPU Utilization
      {
        type = "metric", 
        x = 0,
        y = 0,
        width = 6,
        height = 6,
        properties = {
          title = "Uso de CPU", //titulo do widget
          metrics = [
            [ "AWS/EC2", "CPUUtilization", "InstanceId", var.instance_id ]
          ],
          period = 300, //5 minutos para atualizar
          stat = "Average",
          region = var.aws_region,
          view = "timeSeries"
        }
      },

    //Widget 2 - Network in/out
      {
        type = "metric",
        x = 6,
        y = 0,
        width = 6,
        height = 6,
        properties = {
          title = "Network In/Out", //titulo do widget
          metrics = [
            [ "AWS/EC2", "NetworkIn", "InstanceId", var.instance_id ],
            [ ".", "NetworkOut", ".", "." ]
          ],
          period = 300, //5 minutos para atualizar
          stat = "Sum",
          region = var.aws_region,
          view = "timeSeries"
        }
      },

    //Widget 3 - Status de saúde
      {
        type = "metric",
        x = 0,
        y = 6,
        width = 12,
        height = 6,
        properties = {
          title = "Status de Saúde", //titulo do widget
          metrics = [
            [ "AWS/EC2", "StatusCheckFailed", "InstanceId", var.instance_id ]
          ],
          period = 300, //5 minutos para atualizar
          stat = "Maximum",
          region = var.aws_region,
          view = "singleValue"
        }
      },

    //Widget 4 - Logs do Sistema (configuração pendente - log_group_name)
    #   {
    #     type = "log",
    #     x = 0,
    #     y = 18,
    #     width = 12,
    #     height = 6,
    #     properties = {
    #       title = "Logs do Sistema", //titulo do widget
    #       query = "fields @timestamp, @message | sort @timestamp desc | limit 20",
    #       region = var.aws_region,
    #       logGroupNames = [ var.log_group_name ]
    #     }
    #   }

    ]
  })
}

//Alarme 1 - Alerta de uso da CPU maior que 80%
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "ec2-cpu-utilization-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Alerta: CPU acima de 80% por 5 minutos"

  dimensions = {
    InstanceId = var.instance_id
  }

  tags = {
    Name        = "ec2-cpu-utilization-high"
    Project     = "ChatbotTelegram"
    CostCenter  = "TI123"
  }
  
}

//Alarme 2 - Alerta de falhas no status check
resource "aws_cloudwatch_metric_alarm" "status_failed" {
  alarm_name          = "ec2-status-check-failed"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "StatusCheckFailed"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Maximum"
  threshold           = 0
  alarm_description   = "Alerta: Falha na verificação de status da EC2"

  dimensions = {
    InstanceId = var.instance_id
  }

  tags = {
    Name        = "ec2-status-check-failed"
    Project     = "ChatbotTelegram"
    CostCenter  = "TI123"
  }

}