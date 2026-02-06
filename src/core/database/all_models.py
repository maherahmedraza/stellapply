# This file imports all models to ensure they are registered with SQLAlchemy's declarative base.
# It helps avoid circular dependency issues when models refer to each other across modules.

import src.modules.identity.domain.models  # noqa
import src.modules.persona.domain.models  # noqa
import src.modules.resume.domain.models  # noqa
import src.modules.job_search.domain.models  # noqa
import src.modules.applications.models  # noqa
import src.modules.profile.models  # noqa
import src.agent.browser.session_store  # noqa
import src.agent.models.entities  # noqa
import src.core.security.audit_log  # noqa
