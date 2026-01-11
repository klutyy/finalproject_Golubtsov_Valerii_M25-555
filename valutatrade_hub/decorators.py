import functools
from datetime import datetime


def log_action(mode='INFO', verbose=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timestamp = datetime.now()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                print(
                    f'{mode} {timestamp} {func.__name__.upper()} '
                    f'args={args} kwargs={kwargs} result={e}'
                )
                raise
            else:
                if verbose:
                    print(
                        f'{mode} {timestamp} {func.__name__.upper()} '
                        f'args={args} kwargs={kwargs} result=OK'
                    )
                return result

        return wrapper
    return decorator