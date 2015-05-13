# check for service enabled
if is_service_enabled cue; then

    if [[ "$1" == "source" ]]; then
        # Initial source of lib script
        source $TOP_DIR/lib/cue
    fi

    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing Cue"
        install_cue

        echo_summary "Installing Cue Client"
        install_cueclient

        #echo_summary "Installing Cue Dashboard"
        #install_cuedashboard

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring Cue"
        configure_cue

        if is_service_enabled key; then
            echo_summary "Creating Cue Keystone Accounts"
            create_cue_accounts
        fi

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "Initializing Cue"
        init_cue

        echo_summary "Starting Cue"
        start_cue

        echo_summary "Creating Initial Cue Resources"
        create_cue_initial_resources
    fi

    if [[ "$1" == "unstack" ]]; then
        stop_cue
    fi

    if [[ "$1" == "clean" ]]; then
        echo_summary "Cleaning Cue"
        cleanup_cue
    fi
fi
