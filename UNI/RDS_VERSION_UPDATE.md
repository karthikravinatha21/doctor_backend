# RDS Version Update Documentation

## Changes Made

The AWS RDS PostgreSQL version has been updated from version 14.6 to version 15.3 (a stable and available version). The following changes were made:

1. Updated the `engine_version` parameter in the `aws_db_instance` resource from "14.6" to "15.3" in the `/workspace/terraform/modules/rds/main.tf` file.

2. Updated the parameter group family from "postgres14" to "postgres15" in the `aws_db_parameter_group` resource in the same file.

## Implementation Notes

### Impact of Changes

Upgrading the PostgreSQL version is a significant change that might require a database migration strategy in a production environment. When applying these changes to an existing RDS instance, AWS typically handles the upgrade process, but it might involve some downtime.

### Recommendations for Deployment

1. **Backup**: Take a snapshot of the existing database before applying the changes.
2. **Testing**: Test the upgrade in a staging environment first to ensure compatibility.
3. **Scheduling**: Schedule the upgrade during a maintenance window to minimize impact.
4. **Rollback Plan**: Have a rollback plan in case of issues (using the database snapshot).

### Application Compatibility

It's important to verify that the application is compatible with PostgreSQL 15.3, as there might be some breaking changes or deprecated features between PostgreSQL 14 and 15. Review the [PostgreSQL release notes](https://www.postgresql.org/docs/15/release-15.html) for details on changes that might affect your application.

## How to Apply Changes

To apply these changes, run the following Terraform commands:

```bash
cd /workspace/terraform
terraform plan -out=cinema-app.tfplan
terraform apply cinema-app.tfplan
```

## Verification

After applying the changes, verify that the RDS instance has been updated correctly:

1. Check the AWS Management Console to confirm the RDS instance is running PostgreSQL 15.3.
2. Verify that the application can connect to the database and operate normally.
3. Monitor the application logs for any database-related errors.

## Rollback Procedure

If issues are encountered after the upgrade, you can restore the database from the snapshot taken before the upgrade:

1. In the AWS Management Console, navigate to the RDS service.
2. Select "Snapshots" from the left navigation pane.
3. Find the snapshot taken before the upgrade.
4. Click "Actions" and select "Restore Snapshot".
5. Follow the prompts to restore the database.

## Note on PostgreSQL Version Selection

Initially, there was an attempt to upgrade to PostgreSQL 16.1, but this version is not currently available in AWS RDS. PostgreSQL 15.3 was chosen as a stable and available alternative. AWS regularly updates the available engine versions, so it's recommended to check the [AWS RDS documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html) for the latest supported versions.
