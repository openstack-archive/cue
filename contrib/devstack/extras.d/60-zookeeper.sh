# check for service enabled
if is_service_enabled zookeeper; then

    if [[ "$1" == "source" ]]; then
        # Initial source of lib script
        source $TOP_DIR/lib/zookeeper
    fi

    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing Zookeeper"
        install_zookeeper

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring Zookeeper"
        configure_zookeeper

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "Initializing Zookeeper"
        init_zookeeper

        echo_summary "Starting Zookeeper"
        start_zookeeper
    fi

    if [[ "$1" == "unstack" ]]; then
        stop_zookeeper
    fi

    if [[ "$1" == "clean" ]]; then
        echo_summary "Cleaning Zookeeper"
        cleanup_zookeeper
    fi
fi
