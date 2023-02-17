import colorlog
from pythonjsonlogger import jsonlogger

try:
    import ujson as json
except ImportError:
    import json


class ColoredExtraFormatter(colorlog.ColoredFormatter):
    def format(self, record):
        message_extra = {
            k: v
            for k, v in json.loads(jsonlogger.JsonFormatter().format(record)).items()
            if k not in ['message']
        }
        result = [super().format(record)]
        if message_extra:
            color = self.color(self.log_colors, record.levelname)
            reset = colorlog.escape_codes["reset"]
            result.append(f'{color}%s{reset}' % f'{reset}\n{color}'.join(
                json.dumps(message_extra, indent=4, ensure_ascii=False).split('\n')
            ))
        return '\n'.join(result)
