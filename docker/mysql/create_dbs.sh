#!/usr/bin/env bash

mysql -vv -uroot -e "CREATE DATABASE IF NOT EXISTS gabinet character set UTF8;"
mysql -vv -uroot -e "CREATE DATABASE IF NOT EXISTS medicines character set UTF8;"