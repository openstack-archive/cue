The contrib/devstack directory contrains the files to integrate Cue with Devstack.

To install Cue
    
    # Clone devstack and cue
    git clone https://github.com/openstack-dev/devstack.git
    git clone https://github.com/stackforge/cue.git

    # Install the cue plugins onto Devstack
    ./cue/contrib/devstack/install.sh

    # Copy the local.conf to your devstack 
    cp cue/contrib/devstack/local.conf devstack/

This will create the neccessary symlinks to the Cue-devstack-plugin, and setup
devstack with a local.conf that enables the Cue services and its dependencies.

