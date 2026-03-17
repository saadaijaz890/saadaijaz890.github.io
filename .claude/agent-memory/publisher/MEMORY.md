# Publisher Agent Memory

## Repository Config
- Remote: calmxx → https://github.com/saadaijaz890/saadaijaz890.github.io.git (HTTPS)
- Branch: main
- Hooks: none detected

## Publish Log
- 2026-03-11: blogs/golden-retriever-puppy-crate-anxiety.html — commit c8d3c28
- 2026-03-11: blogs/labrador-retriever-puppy-crate-training.html — commit 29bb343
- 2026-03-11: blogs/german-shepherd-leash-reactivity-protocol.html — commit 15cb34d
- 2026-03-12: blogs/poodle-separation-anxiety-protocol.html — commit 2c92166
- 2026-03-13: blogs/french-bulldog-puppy-crate-training.html — commit df5d632
- 2026-03-17: 5 Beagle articles + OpenAI writer integration — commit fd22077
  - blogs/beagle-puppy-crate-training.html
  - blogs/beagle-alone-time-guide.html
  - blogs/beagle-departure-desensitization.html
  - blogs/beagle-apartment-howling.html
  - blogs/beagle-thunderstorm-fireworks.html
  - Also included: scripts/generate_article.py, requirements.txt, .gitignore, .claude/agents/writer.md, sw.js (deleted)
  - NOTE: .claude/settings.local.json was explicitly excluded — contains API key

- 2026-03-17: 5 Dachshund articles — commit e10291b
  - blogs/dachshund-puppy-crate-training.html
  - blogs/dachshund-alone-time-limits.html
  - blogs/dachshund-ivdd-confinement-anxiety.html
  - blogs/dachshund-nose-work-anxiety.html
  - blogs/dachshund-departure-desensitization.html

- 2026-03-17: Python scripts + agent updates — commit 89187f3
  - scripts/link_article.py (new)
  - scripts/publish_articles.py (new)
  - .claude/agents/linker.md (modified)
  - .claude/agents/publisher.md (modified)
  - NOTE: .claude/settings.local.json explicitly excluded

## Known Issues
- Remote is named `calmxx`, not `origin` — always use `git push calmxx main`
- Agent memory files (.claude/agent-memory/**) are frequently modified alongside content publishes — never stage them, stage specific content paths only
