#!/usr/bin/env bash
file="backup.pgsql"
if [[ ! -f "$file" ]]
then
    echo "$0: File '${file}' not found."
    exit 1
fi
echo "Restoring database..."
pg_restore --clean --if-exists --host 127.0.0.1 --port 5432  --no-owner --no-privileges --dbname price-picker-dev backup.pgsql
echo "Database restored successfully."