import os
import argparse
from donkeycarmanager.helpers.logging import setup_logging


def main():
    setup_logging()
    script_dir = os.path.dirname(os.path.realpath(__file__))

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        os.environ['DONKEYCARMANAGER_LOG_LEVEL'] = 'DEBUG'  # Ugly fix due to uvicorn that can't pass any options

    import uvicorn
    uvicorn.run('donkeycarmanager.app:app', host="0.0.0.0", port=8000,
                reload=True, reload_dirs=[script_dir],
                ws_ping_interval=2, ws_ping_timeout=6, timeout_keep_alive=2,
                log_config=f"{script_dir}/config/logging.yaml")


if __name__ == "__main__":
    main()
