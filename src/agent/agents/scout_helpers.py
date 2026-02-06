from urllib.parse import quote
from typing import List, Dict

from src.modules.profile.schemas import SearchPreferencesSchema


class SearchURLBuilder:
    """Builds search URLs for various job boards from user preferences."""

    @staticmethod
    def build_urls(preferences: SearchPreferencesSchema) -> List[Dict[str, str]]:
        sources = []
        # Default to remote if no locations specified, or ensuring coverage
        locations = preferences.locations if preferences.locations else ["Remote"]

        for role in preferences.target_roles:
            for location in locations:
                # LinkedIn
                # Note: LinkedIn URLs can vary by region. Defaulting to www.linkedin.com which usually redirects or handles geo.
                sources.append(
                    {
                        "platform": "linkedin",
                        "search_url": f"https://www.linkedin.com/jobs/search/?keywords={quote(role)}&location={quote(location)}",
                    }
                )

                # Indeed (Handling generic vs region specific could be complex, sticking to simple parameterized urls)
                # Using a generic approach, or specific regions if known.
                # Ideally, we should detect region from location, but for now we follow the user requirement example (indeed.de) or generic.
                # If location implies Germany, use de.indeed.com?
                # For MVP, we might add multiple variants or rely on the agent to handle redirects?
                # Let's stick to the prompt's example structure but make it robust.

                # Check for Germany in location to pick de.indeed? Or just use www.indeed.com for global?
                # The user prompt example used de.indeed.com. Let's add common variants if needed,
                # or just Indeed specific to the inferred intent.
                # For now, let's assume global or parameterized based on user intent if provided,
                # but the prompt specifically mentioned "de.indeed.com" in the example context.
                # I will add a generic one and maybe a German one if "Berlin" or "Germany" is in location.

                if any(
                    x in location.lower()
                    for x in ["berlin", "germany", "deutschland", "munich", "Hamburg"]
                ):
                    sources.append(
                        {
                            "platform": "indeed",
                            "search_url": f"https://de.indeed.com/jobs?q={quote(role)}&l={quote(location)}",
                        }
                    )
                    sources.append(
                        {
                            "platform": "stepstone",
                            "search_url": f"https://www.stepstone.de/jobs/{quote(role.replace(' ', '-'))}/in-{quote(location.lower())}",
                        }
                    )
                else:
                    sources.append(
                        {
                            "platform": "indeed",
                            "search_url": f"https://www.indeed.com/jobs?q={quote(role)}&l={quote(location)}",
                        }
                    )

        return sources
