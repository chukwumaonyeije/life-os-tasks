Second Brain — LifeOS Tasks

This short doc contains suggested next steps to shape `life-os-tasks` into a personal second brain and simple deployment notes for Hostinger.

Goals

- Preserve immutable logs (ground truth) first
- Provide manual review & linking flows (no forced tagging at capture)
- Offer export/import for safe backups and migration
- Provide a simple search/recall layer (SQLite FTS or small client-side index)

Quick features to add next

- JSON export/import endpoint and a UI button that downloads/upload archives
- Lightweight search (server-side SQLite FTS or lunr/elasticlunr client-side)
- Tagging/linking via the review workflow and a concept/project model
- Daily/weekly digest export for long-term reflection

Hostinger deployment options

1) Static hosting (recommended for minimal exposure)

- Use the `static/` folder as a standalone UI. Hostinger can serve static files directly.
- If you only need the UI publicly available, deploy `static/` to the Hostinger site. Keep the API local when developing.

2) Self-hosted API (VPS or Hostinger VPS)

- Run the FastAPI app on a small VPS or a Hostinger VPS instance.
- Use Docker to package the app and Nginx (or Hostinger's reverse proxy) to route requests.
- Ensure TLS (Let's Encrypt) and a simple auth layer if the API is exposed.

3) Tunnel for ad-hoc remote access

- Use Cloudflare Tunnel or ngrok to expose your local FastAPI during development without a public host.

I can help with any of these next steps — e.g., adding export endpoints, wiring a simple search, or preparing exact Hostinger deployment commands.
