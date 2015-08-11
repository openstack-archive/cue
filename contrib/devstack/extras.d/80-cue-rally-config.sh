
if [[ "$1" == "stack" && "$2" == "post-config" ]]; then
    if [[ ! -z $RALLY_AUTH_URL ]]; then
        # rally deployment create
        tmpfile=$(mktemp)
        _create_deployment_config $tmpfile

        iniset $RALLY_CONF_DIR/$RALLY_CONF_FILE database connection `database_connection_url rally`
        recreate_database rally utf8
        # Recreate rally database
        $RALLY_BIN_DIR/rally-manage --config-file $RALLY_CONF_DIR/$RALLY_CONF_FILE db recreate

        rally --config-file /etc/rally/rally.conf deployment create --name cue-devstack2 --file $tmpfile
    fi
fi


# _create_deployment_config filename
function _create_deployment_config() {
    cat >$1 <<EOF
{
    "type": "ExistingCloud",
    "auth_url": "$KEYSTONE_AUTH_PROTOCOL://$KEYSTONE_AUTH_HOST:$KEYSTONE_AUTH_PORT/$RALLY_AUTH_VERSION",
    "admin": {
        "username": "admin",
        "password": "$ADMIN_PASSWORD",
        "project_name": "admin"
    }
}
EOF
}
