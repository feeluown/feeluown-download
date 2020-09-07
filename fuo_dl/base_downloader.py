import asyncio
import os
import logging

logger = logging.getLogger(__name__)


class Downloader:
    async def run(self, url, filepath, **kwargs):
        pass

    def clean(self, filepath):
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:  # noqa
                logger.exception(f'remove {filepath} failed, this should not happen')
            else:
                logger.info('download file faield, remove the tmp file')


class CurlDownloader(Downloader):
    async def run(self, url, filepath, **kwargs):
        try:
            proc = await asyncio.create_subprocess_exec(
                'curl', url, '--output', filepath)
        except FileNotFoundError:
            logger.error("can't start download, curl is not installed")
            raise
        else:
            await proc.wait()
        return proc.returncode == 0
