import os
import shutil
import socket
import glob

import toml
from loguru import logger

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
config_file = f"{root_dir}/config.toml"


def load_config():
    # fix: IsADirectoryError: [Errno 21] Is a directory: '/MoneyPrinterTurbo/config.toml'
    if os.path.isdir(config_file):
        shutil.rmtree(config_file)

    if not os.path.isfile(config_file):
        example_file = f"{root_dir}/config.example.toml"
        if os.path.isfile(example_file):
            shutil.copyfile(example_file, config_file)
            logger.info("copy config.example.toml to config.toml")

    logger.info(f"load config from file: {config_file}")

    try:
        _config_ = toml.load(config_file)
    except Exception as e:
        logger.warning(f"load config failed: {str(e)}, try to load as utf-8-sig")
        with open(config_file, mode="r", encoding="utf-8-sig") as fp:
            _cfg_content = fp.read()
            _config_ = toml.loads(_cfg_content)
    return _config_


def save_config():
    with open(config_file, "w", encoding="utf-8") as f:
        _cfg["app"] = app
        _cfg["azure"] = azure
        _cfg["siliconflow"] = siliconflow
        _cfg["ui"] = ui
        f.write(toml.dumps(_cfg))


_cfg = load_config()
app = _cfg.get("app", {})
whisper = _cfg.get("whisper", {})
proxy = _cfg.get("proxy", {})
azure = _cfg.get("azure", {})
siliconflow = _cfg.get("siliconflow", {})
ui = _cfg.get(
    "ui",
    {
        "hide_log": False,
    },
)

hostname = socket.gethostname()

log_level = _cfg.get("log_level", "DEBUG")
listen_host = _cfg.get("listen_host", "0.0.0.0")
listen_port = _cfg.get("listen_port", 8080)
project_name = _cfg.get("project_name", "MoneyPrinterTurbo")
project_description = _cfg.get(
    "project_description",
    "<a href='https://github.com/harry0703/MoneyPrinterTurbo'>https://github.com/harry0703/MoneyPrinterTurbo</a>",
)
project_version = _cfg.get("project_version", "1.2.7")
reload_debug = False

app["redis_host"] = os.getenv(
    "MPT_APP_REDIS_HOST",
    os.getenv("REDIS_HOST", app.get("redis_host", "localhost")),
)

imagemagick_path = app.get("imagemagick_path", "")
if imagemagick_path and os.path.isfile(imagemagick_path):
    os.environ["IMAGEMAGICK_BINARY"] = imagemagick_path

ffmpeg_path = app.get("ffmpeg_path", "")
existing_ffmpeg_env = os.getenv("IMAGEIO_FFMPEG_EXE", "")
existing_ffmpeg_env_is_valid = bool(
    existing_ffmpeg_env and os.path.isfile(existing_ffmpeg_env)
)
if ffmpeg_path and os.path.isfile(ffmpeg_path):
    os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_path
elif os.name == "nt" and not existing_ffmpeg_env_is_valid:
    # 兼容便携版目录结构：优先自动探测上级 lib/ffmpeg 下的 ffmpeg.exe。
    candidate_patterns = [
        os.path.abspath(os.path.join(root_dir, "..", "lib", "ffmpeg", "**", "ffmpeg.exe")),
        os.path.abspath(os.path.join(root_dir, "lib", "ffmpeg", "**", "ffmpeg.exe")),
    ]
    detected_ffmpeg = ""
    for pattern in candidate_patterns:
        matched = sorted(glob.glob(pattern, recursive=True))
        if matched:
            detected_ffmpeg = matched[0]
            break

    if detected_ffmpeg and os.path.isfile(detected_ffmpeg):
        os.environ["IMAGEIO_FFMPEG_EXE"] = detected_ffmpeg
        logger.info(f"auto detected ffmpeg: {detected_ffmpeg}")

logger.info(f"{project_name} v{project_version}")
