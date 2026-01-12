import os

# Only use gevent in production (gunicorn), skip in development (runserver)
# gevent causes threading issues with Django dev server and Redis connections
if os.getenv("dockerrun", "no") == "yes" and os.getenv("USE_GEVENT", "no") == "yes":
    from component.mysql_pool import patch_mysql
    from gevent import monkey
    monkey.patch_all(thread=False)
    patch_mysql()

