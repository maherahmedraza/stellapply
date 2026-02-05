# This file imports all models to ensure they are registered with SQLAlchemy's declarative base.
# It helps avoid circular dependency issues when models refer to each other across modules.

import src.modules.identity.domain.models  # noqa
import src.modules.persona.domain.models  # noqa
import src.modules.resume.domain.models  # noqa
import src.modules.job_search.domain.models  # noqa
