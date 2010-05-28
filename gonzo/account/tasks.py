from celery.decorators import task

@task()
def test_task(x, y):
    return x + y
