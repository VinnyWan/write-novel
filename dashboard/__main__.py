"""Dashboard entry point: python -m dashboard --project-root /path/to/project"""
import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="write-novel Dashboard Server")
    parser.add_argument("--project-root", type=str, required=True, help="小说项目根目录")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址")
    parser.add_argument("--port", type=int, default=8765, help="监听端口")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if not project_root.is_dir():
        print(f"ERROR: 项目目录不存在: {project_root}", file=sys.stderr)
        sys.exit(1)

    print(f"项目路径: {project_root}")
    print(f"启动 Dashboard: http://{args.host}:{args.port}")

    import uvicorn
    from dashboard.app import create_app

    app = create_app(project_root)

    if not args.no_browser:
        import webbrowser
        webbrowser.open(f"http://{args.host}:{args.port}")

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
