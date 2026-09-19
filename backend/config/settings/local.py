import os
os.environ.setdefault('DJANGO_SECRET_KEY','local-only-change-before-deployment-7fc048fa')
from .base import *
DEBUG = True

# Keep a fresh checkout runnable without requiring a local PostgreSQL service.
# An explicit DATABASE_URL still wins when a developer has PostgreSQL available.
DATABASES = {'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "local.sqlite3"}')}
