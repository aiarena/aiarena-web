from aiarena.core.tasks import celery_exception_test


def http_500(request):
    celery_exception_test.delay()
    raise Exception("Testing HTTP 500")
