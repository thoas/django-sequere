from __future__ import unicode_literals

from django.core.paginator import Paginator

from celery.task import task


@task
def dispatch_action(action_uid, dispatch=True):
    from sequere.models import get_followers
    from sequere.contrib.timeline import app

    from . import Timeline

    logger = dispatch_action.get_logger()

    action = app.backend.get_action(action_uid)

    paginator = Paginator(get_followers(action.actor), 10)

    logger.info('Dispatch action %s to %s followers' % (action, paginator.count))

    for num_page in paginator.page_range:
        page = paginator.page(num_page)

        for obj, timestamp in page.object_list:
            if action.actor == obj:
                continue

            timeline = Timeline(obj)
            timeline.save(action, dispatch=dispatch)


def populate_actions(from_uid, to_uid, method, logger=None):
    from sequere import app

    from . import Timeline

    from_instance = app.backend.get_from_uid(from_uid)

    to_instance = app.backend.get_from_uid(to_uid)

    paginator = Paginator(Timeline(from_instance).get_public(), 10)

    timeline = Timeline(to_instance)

    if logger:
        logger.info('Populate (%s) %s with %s items from %s' % (method,
                                                                to_instance,
                                                                paginator.count,
                                                                from_instance))

    for num_page in paginator.page_range:
        page = paginator.page(num_page)

        for action in page.object_list:
            getattr(timeline, method)(action, dispatch=False)


@task
def import_actions(from_uid, to_uid):
    populate_actions(from_uid, to_uid, 'save',
                     logger=import_actions.get_logger())


@task
def remove_actions(from_uid, to_uid):
    populate_actions(from_uid, to_uid, 'delete',
                     logger=remove_actions.get_logger())
