from distutils.version import StrictVersion


def is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


def increment(version, type=None):
    if version.count('.') != 2:
        raise ValueError('Invalid version literal. Correct format: 1.0.0')
    major, minor, patch = version.split('.')

    if not (is_int(major) and is_int(minor) and is_int(patch)):
        raise ValueError('Invalid version literal. It contains non-integer value.')

    if type == 'major':
        major = int(major) + 1
        minor = 0
        patch = 0
    elif type == 'minor':
        minor = int(minor) + 1
        patch = 0
    else:
        patch = int(patch) + 1

    return '.'.join([str(major), str(minor), str(patch)])


def latest(versions):
    if len(versions) > 0:
        return sorted(versions, key=StrictVersion)[-1]
