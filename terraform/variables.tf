variable "aws_region" {
  description = "Region for the AWS services to run in."
  type        = string
  default     = "eu-west-1"
}

variable "access_key" {
  description = "AWS access key"
  type        = string
}

variable "secret_key" {
  description = "AWS secret key"
  type        = string
}

variable "account_id" {
  description = "AWS account id"
  type        = string
}

variable "raw_bucket" {
  description = "Bucket name for raw S3 bucket"
  type        = string
  default     = "tripadvisor-activities-malta-project"
}

variable "cleansed_bucket" {
  description = "Bucket name for cleansed S3 bucket"
  type        = string
  default     = "tripadvisor-activities-malta-project-cleansed"
}

variable "athena_bucket" {
  description = "Bucket containing queries from Athena"
  type        = string
  default     = "tripadvisor-activities-malta-project-athena"
}

variable "lambda_function_transformations" {
  description = "Lambda function used for transformations & loading cleansed data into S3 bucket in parquet format"
  type        = string
  default     = "tripadvisor-activities-malta-project-lambda-transformations"
}

variable "lambda_s3_role" {
  description = "Lambda - s3 role"
  type        = string
  default     = "tripadvisor-activities-malta-project-s3-lambda-role"
}

variable "glue_s3_role" {
  description = "Glue - s3 role"
  type        = string
  default     = "tripadvisor-activities-malta-project-glue-s3-role"
}

variable "raw_db" {
  description = "Name of raw db"
  type        = string
  default     = "tripadvisor-activities-malta-project-raw-db"
}

variable "cleansed_db" {
  description = "Name of cleansed db"
  type        = string
  default     = "tripadvisor-activities-malta-project-cleansed-db"
}

variable "raw_table" {
  description = "Name of raw table"
  type        = string
  default     = "tripadvisor_activities_malta_project"
}

variable "cleansed_table" {
  description = "Name of cleansed table"
  type        = string
  default     = "tripadvisor_activities_malta_project-cleansed-table"
}

variable "crawler_raw" {
  description = "Name of crawler"
  type        = string
  default     = "tripadvisor-activities-malta-project-raw-crawler"
}

variable "sizeKey" {
  description = "raw_catalog_table sizeKey"
  type        = string
}

variable "averageRecordSize" {
  description = "raw_catalog_table averageRecordSize"
  type        = string
}

variable "objectCount" {
  description = "raw_catalog_table objectCount"
  type        = string
}

variable "recordCount" {
  description = "raw_catalog_table recordCount"
  type        = string
}
