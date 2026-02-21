# macOS fork safety 이슈 해결을 위한 환경 변수 추가
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Gunicorn으로 실행 (4개의 워커 사용)
uv run gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000