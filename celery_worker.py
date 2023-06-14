#!/usr/bin/env python
import os

# from karmalegoweb import create_app, celery
from karmalegoweb import create_app

app = create_app()
app.app_context().push()

from karmalegoweb import celery
