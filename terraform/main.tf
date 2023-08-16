# Configure the AWS Provider
provider "aws" {
  region     = var.aws_region
  access_key = var.access_key
  secret_key = var.secret_key
}

# Raw S3 bucket resource
resource "aws_s3_bucket" "s3_raw_bucket" {
  bucket = var.raw_bucket
}

# Cleansed S3 bucket resource
resource "aws_s3_bucket" "s3_cleansed_bucket" {
  bucket = var.cleansed_bucket
}

# Athena S3 bucket resource
resource "aws_s3_bucket" "s3_athena" {
  bucket = var.athena_bucket
}

# Lambda resource
resource "aws_lambda_function" "aws_lambda_function" {
  filename      = var.lambda_function_transformations
  function_name = var.lambda_function_transformations
  role          = "arn:aws:iam::${var.account_id}:role/${var.lambda_s3_role}"
  handler       = "lambda_function.lambda_handler"
  layers        = ["arn:aws:lambda:eu-west-1:336392948345:layer:AWSSDKPandas-Python39:8"]
  runtime       = "python3.9"
  architectures = ["x86_64"]
  memory_size   = 1769
  timeout       = 900
  ephemeral_storage {
    size = 512
  }
  # Ignoring addition of filename since it is not essentially needed for 
  # lambda function to work but required in terraform code structure
  lifecycle {
    ignore_changes = [filename]
  }

}

# Glue databases
resource "aws_glue_catalog_database" "raw_db" {
  name = var.raw_db
}

resource "aws_glue_catalog_database" "cleansed_db" {
  name = var.cleansed_db
}

# Glue crawler
resource "aws_glue_crawler" "raw_crawler" {
  database_name = var.raw_db
  name          = var.crawler_raw
  role          = "arn:aws:iam::${var.account_id}:role/${var.glue_s3_role}"
  configuration = jsonencode(
    {
      CreatePartitionIndex = true
      Version              = 1
    }
  )
  s3_target {
    path = "s3://${var.raw_bucket}"
  }

}

# provisioner "local-exec" {
#   file = "variables.sh"
# }

# Glue tables
resource "aws_glue_catalog_table" "raw_catalog_table" {
  name          = var.raw_table
  database_name = var.raw_db
  owner         = "owner"
  table_type    = "EXTERNAL_TABLE"
  parameters = {
    classification                     = "json"
    "CrawlerSchemaDeserializerVersion" = "1.0"
    "CrawlerSchemaSerializerVersion"   = "1.0"
    "UPDATED_BY_CRAWLER"               = "${var.crawler_raw}"
    "compressionType"                  = "none"
    "typeOfData"                       = "file"
    "averageRecordSize"                = "${var.averageRecordSize}"
    "objectCount"                      = "${var.objectCount}"
    "recordCount"                      = "${var.recordCount}"
    "sizeKey"                          = "${var.sizeKey}"
  }

  storage_descriptor {
    location          = "s3://${var.raw_bucket}/"
    input_format      = "org.apache.hadoop.mapred.TextInputFormat"
    output_format     = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"
    number_of_buckets = -1
    parameters = {
      classification                     = "json"
      "CrawlerSchemaDeserializerVersion" = "1.0"
      "CrawlerSchemaSerializerVersion"   = "1.0"
      "UPDATED_BY_CRAWLER"               = "${var.crawler_raw}"
      "compressionType"                  = "none"
      "typeOfData"                       = "file"
      "averageRecordSize"                = "${var.averageRecordSize}"
      "objectCount"                      = "${var.objectCount}"
      "recordCount"                      = "${var.recordCount}"
      "sizeKey"                          = "${var.sizeKey}"
    }
    ser_de_info {
      parameters = {
        "paths" = "Activitiy_Duration,Activitiy_Max_Number_Group,Activitiy_Name,Activitiy_Organizer,Activitiy_Price,Country,Reviews"
      }
      serialization_library = "org.openx.data.jsonserde.JsonSerDe"
    }
  }
}

resource "aws_glue_catalog_table" "cleansed_catalog_table" {
  name          = var.cleansed_table
  database_name = var.cleansed_db
  table_type    = "EXTERNAL_TABLE"
  parameters = {
    classification       = "parquet"
    "projection.enabled" = false
  }

  storage_descriptor {
    location      = "s3://${var.cleansed_bucket}/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"
    ser_de_info {
      parameters = {
        "serialization.format" = "1"
      }
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }
  }
}

