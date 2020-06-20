import logging
import re
import threading
import time

from bot import download_dict, download_dict_lock

LOGGER = logging.getLogger(__name__)

MAGNET_REGEX = r"magnet:\?xt=urn:btih:[a-zA-Z0-9]*"

URL_REGEX = r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+"


class MirrorStatus:
    STATUS_UPLOADING = "<b>Trying To Upload</b>"
    STATUS_DOWNLOADING = "<b>Trying To Download</b>"
    STATUS_WAITING = "⏳ <b>Queued</b>"
    STATUS_FAILED = "<b>Failed.😶 Cleaning Download</b>"
    STATUS_CANCELLED = "🚫 <b>Cancelled</b>"
    STATUS_ARCHIVING = "💾 <b>Archiving</b>"


PROGRESS_MAX_SIZE = 100 // 8
PROGRESS_INCOMPLETE = ['▓', '▓', '▓', '▓', '▓', '▓', '▓']

SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']


class setInterval:
    def __init__(self, interval, action):
        self.interval = interval
        self.action = action
        self.stopEvent = threading.Event()
        thread = threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self):
        nextTime = time.time() + self.interval
        while not self.stopEvent.wait(nextTime - time.time()):
            nextTime += self.interval
            self.action()

    def cancel(self):
        self.stopEvent.set()


def get_readable_file_size(size_in_bytes) -> str:
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f'{round(size_in_bytes, 2)}{SIZE_UNITS[index]}'
    except IndexError:
        return 'File Too Large 🙄'


def getDownloadByGid(gid):
    with download_dict_lock:
        for dl in download_dict.values():
            if dl.status() == MirrorStatus.STATUS_DOWNLOADING or dl.status() == MirrorStatus.STATUS_WAITING:
                if dl.gid() == gid:
                    return dl
    return None


def get_progress_bar_string(status):
    completed = status.processed_bytes() / 8
    total = status.size_raw() / 8
    if total == 0:
        p = 0
    else:
        p = round(completed * 100 / total)
    p = min(max(p, 0), 100)
    cFull = p // 8
    cPart = p % 8 - 1
    p_str = '█' * cFull
    if cPart >= 0:
        p_str += PROGRESS_INCOMPLETE[cPart]
    p_str += '░' * (PROGRESS_MAX_SIZE - cFull)
    p_str = f"[{p_str}]"
    return p_str


def get_readable_message():
    with download_dict_lock:
        msg = ""
        for download in list(download_dict.values()):
            msg += f"<b>🗂 File Name :</b> <code>{download.name()}</code>"
            msg += f"\n<b>📊 Status :</b> <u>{download.status()}</u>"
            if download.status() != MirrorStatus.STATUS_ARCHIVING:
                msg += f"\n<code>{get_progress_bar_string(download)}</code>\n<b>💾 Size:</b> {download.size()} <b>🔥 Speed:</b> {download.speed()}" \
                    f"\n<b>⏳ Progress:</b> {download.progress()} <b>⏱ ETA:</b> {download.eta()}"
            if download.status() == MirrorStatus.STATUS_DOWNLOADING:
                if hasattr(download, 'is_torrent'):
                    msg += f"| ● <b>Peers :</b> {download.aria_download().connections} " \
                           f"| ● <b>Seeds :</b> {download.aria_download().num_seeders}"
                msg += f"\n<b>🚫 :</b> <code>/Cancel {download.gid()}</code>"
            msg += "\n\n"
        return msg


def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d'
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h'
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m'
    seconds = int(seconds)
    result += f'{seconds}s'
    return result


def is_url(url: str):
    url = re.findall(URL_REGEX, url)
    if url:
        return True
    return False


def is_magnet(url: str):
    magnet = re.findall(MAGNET_REGEX, url)
    if magnet:
        return True
    return False
