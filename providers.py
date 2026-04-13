import ecologi
import local as local_provider

PROVIDERS = {
    "ecologi": ecologi.plant_trees,
    "local": local_provider.plant_trees,
}

# Providers that don't require an API key
KEYLESS_PROVIDERS = {"local"}
