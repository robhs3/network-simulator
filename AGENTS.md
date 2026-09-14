# Network Simulator

This is an educational Python network simulator.

## Primary goal

The simulator should model networking behavior realistically enough to
reinforce networking concepts. Do not bypass protocol behavior merely to
produce the correct final result.

## Design principles

- Maintain clear separation between Layer 2 and Layer 3 behavior.
- Switches primarily process Ethernet frames.
- Routers process IP packets and construct new Layer 2 frames when forwarding.
- ARP should be used to resolve next-hop MAC addresses where appropriate.
- VLAN behavior should distinguish access and trunk interfaces.
- Prefer explicit networking behavior over shortcuts.

## Development rules

- Existing tests should remain passing.
- Run tests with:

    uv run pytest

- Run linting with:

    uv run ruff check .

- Format with:

    uv run ruff format .

- Explain significant architectural changes before implementing them.
- Do not redesign unrelated code while fixing a specific bug.