import sentry_sdk
from sentry_sdk.integrations.pymongo import PyMongoIntegration

def add_sentry(is_enabled: bool, dsn: str):
    if is_enabled and dsn is not None:
        sentry_sdk.init(
            dsn=dsn,

            integrations=[
                PyMongoIntegration(),
            ],

            traces_sample_rate=1.0,
        )
