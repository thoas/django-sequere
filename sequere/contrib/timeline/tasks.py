from django.core.paginator import Paginator

from celery.task import task


@task
def dispatch_action(uid, data):
    from sequere.backends import get_backend
    from sequere.contrib.timeline import Timeline, Action

    logger = dispatch_action.get_logger()

    backend = get_backend()()

    instance = backend.manager.get_from_uid(uid)

    if not instance:
        logger.error('No instance found for uid: %s' % uid)
    else:
        paginator = Paginator(instance.get_followers(), 10)

        action = Action.from_data(data)

        for num_page in paginator.num_pages:
            page = paginator.page(num_page)

            for obj, timestamp in page.object_list:
                timeline = Timeline(obj)
                timeline.save(action)
