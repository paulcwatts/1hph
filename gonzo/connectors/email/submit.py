
if __name__ == '__main__':
    import os,sys
    from gonzo.connectors import email
    email.submit_from_file(os.environ, sys.stdin)
