# TherapyBot Cleanup Plan

## Files to DELETE (redundant/temporary):
- `test_*.py` (all root-level test files - move to /tests)
- `voice_test.html`
- `test_frontend_endpoints.html` 
- `test_curl_commands.md`
- `project_synopsis.txt`
- `frontend/test-results/` (old test results)
- `backend/test-results/` (old test results)
- `frontend/-p/` (empty directory)
- `backend/app/services.py/` (duplicate services folder)
- `backend/app/routers/__init__py` (typo file)

## Files to MOVE:

### To /docs:
- `AI_FALLBACK_EXAMPLES.md`
- `AI_SETUP_GUIDE.md`
- `CURL_TESTS.md`
- `DELIVERABLES_SUMMARY.md`
- `ENDPOINT_FIXES.md`
- `MANUAL_TESTING.md`
- `SPEECH_RECOGNITION_FIXES.md`
- `TEST_RESULTS.md`
- `TESTING.md`
- `VERTEX_AI_FIXES.md`

### To /tests:
- All `test_*.py` files from root
- `run_tests.py`

### To /reports:
- `frontend/playwright-report/`
- Any generated test reports

## Keep in ROOT:
- `README.md`
- `docker-compose*.yml`
- `.env*`
- `.gitignore`
- `Makefile`
- `quick_test.py`
- `start-*.sh`