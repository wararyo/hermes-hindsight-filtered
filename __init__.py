"""Hindsight memory, with scheduler-injected turns relabelled before they are retained.

Hermes hands a turn a plugin injected (``ctx.inject_message``) to memory providers as if the person
had typed it (NousResearch/hermes-agent#130622), so Hindsight retains a wake's instructions as the
user's own words. This provider is the installed Hindsight plugin with one change: such a turn's
user side is replaced by a short label first (see ``filtering.py``).

``name`` stays "hindsight": the provider is the same backend with the same settings
(``$HERMES_HOME/hindsight/config.json``, ``HINDSIGHT_*``), only selected through
``memory.provider: hindsight_filtered``.
"""

from __future__ import annotations

from plugins.memory import import_provider_module

from .filtering import InjectedTurnFilterMixin

UPSTREAM_PROVIDER = "hindsight"


def _upstream_provider_class() -> type:
    try:
        module = import_provider_module(UPSTREAM_PROVIDER)
    except ImportError as exc:
        raise ImportError(
            "hindsight_filtered wraps the Hindsight memory plugin, which is not installed: "
            "run `hermes plugins install hindsight` first"
        ) from exc
    return module.HindsightMemoryProvider


class FilteredHindsightMemoryProvider(InjectedTurnFilterMixin, _upstream_provider_class()):
    """Hindsight with injected turns relabelled in ``sync_turn``."""


def register(ctx) -> None:
    ctx.register_memory_provider(FilteredHindsightMemoryProvider())
