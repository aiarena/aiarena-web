from aiarena.celery import app


@app.task(ignore_result=True)
def celery_exception_test():
    raise Exception("Testing Celery exception")
