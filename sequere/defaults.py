KEY_SEPARATOR = ':'

BACKEND = 'sequere.backends.database.DatabaseBackend'
BACKEND_OPTIONS = {}
FAIL_SILENTLY = False

TIMELINE_BACKEND = 'sequere.contrib.timeline.backends.redis.RedisBackend'
TIMELINE_BACKEND_OPTIONS = {}
TIMELINE_IMPORT_ACTIONS_ON_FOLLOW = False
TIMELINE_REMOVE_ACTIONS_ON_UNFOLLOW = False

TIMELINE_DISPATCH_RANGE = 100
TIMELINE_POPULATE_RANGE = 100
