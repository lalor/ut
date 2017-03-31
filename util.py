import subprocess


def execute_cmd(cmd):
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        return p.returncode, stderr
    return p.returncode, stdout


def valid_password(pwd):

    if len(pwd) < 3 or len(pwd) > 10:
        return False

    if pwd[0] not in string.ascii_letters:
        return False

    legal_chars = string.ascii_letters + string.digits + "_"
    for char in pwd:
        if char not in legal_chars:
            return False

    if pwd[-1] == "_":
        return False

    return True
