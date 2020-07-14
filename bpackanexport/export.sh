#!/bin/bash

apply()
{
  echo
  echo ">>> Executing bpa-ckan-export($ckanurl): $action"
  echo
  bpa-ckan-export "$action" -k "$apikey" -u $ckanurl -p "$targetdir" $extra_args
}

action="$1"
apikey="$2"
targetdir="$3"
if [ x"$DEV_MODE" != x ]; then
  ckanurl="$CKAN_URL"
  extra_args="--verify-ssl False"
else
  ckanurl="$4"
fi

usage()
{
  echo "$0 <action> <apikey> <targetdir> <ckanurl>"
  exit 1
}

if [ x"$action" = x ]; then
  usage
fi

if [ x"$apikey" = x ]; then
  usage
fi

if [ x"$targetdir" = x ]; then
  usage
fi

if [ x"$DEV_MODE" = x ] && [ x"$ckanurl" = x ];then
  usage
fi

apply