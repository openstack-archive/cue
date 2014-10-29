from oslo.config import cfg


API_SERVICE_OPTS = [
    cfg.StrOpt('host_ip',
               default='0.0.0.0',
               help='The listen IP for the Cue API server.'),
    cfg.IntOpt('port',
               default=6385,
               help='The port for the Cue API server.'),
    cfg.IntOpt('max_limit',
               default=1000,
               help='The maximum number of items returned in a single '
                    'response from a collection resource.'),
    ]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='api',
                         title='Options for the cue-api service')
CONF.register_group(opt_group)
CONF.register_opts(API_SERVICE_OPTS, opt_group)