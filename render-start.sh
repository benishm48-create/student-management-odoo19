#!/bin/bash

odoo \
  --http-interface=0.0.0.0 \
  --http-port=${PORT:-10000} \
  --db_host=${DB_HOST} \
  --db_port=${DB_PORT:-5432} \
  --db_user=${DB_USER} \
  --db_password=${DB_PASSWORD}
