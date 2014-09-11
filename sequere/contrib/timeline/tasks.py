from django.core.paginator import Paginator

from celery.task import task


@task
def dispatch_action(uid, data, dispatch=True):
    from sequere.backends.redis.connection import manager
    from sequere.models import get_followers

    from . import Timeline, Action

    logger = dispatch_action.get_logger()

    instance = manager.get_from_uid(uid)

    if not instance:
        logger.error('No instance found for uid: %s' % uid)
    else:
        paginator = Paginator(get_followers(instance), 10)

        action = Action.from_data(data)

        for num_page in paginator.page_range:
            page = paginator.page(num_page)

            for obj, timestamp in page.object_list:
                if action.actor == obj:
                    continue

                timeline = Timeline(obj)
                timeline.save(action, dispatch=dispatch)


def populate_actions(from_uid, to_uid, method):
    from sequere.backends.redis.connection import manager

    from . import Timeline

    from_instance = manager.get_from_uid(from_uid)

    to_instance = manager.get_from_uid(to_uid)

    paginator = Paginator(Timeline(from_instance).get_public(), 10)

    timeline = Timeline(to_instance)

    for num_page in paginator.page_range:
        page = paginator.page(num_page)

        for action in page.object_list:
            getattr(timeline, method)(action, dispatch=False)


@task
def import_actions(from_uid, to_uid):
    populate_actions(from_uid, to_uid, 'save')


@task
def remove_actions(from_uid, to_uid):
    populate_actions(from_uid, to_uid, 'delete')
