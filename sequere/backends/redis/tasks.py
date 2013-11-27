from celery.task import task

from sequere.utils import load_class


@task
def follow(backend_class,
           from_instance_class, from_instance_pk,
           to_instance_class, to_instance_pk):

    backend = load_class(backend_class)()

    return backend.follow(from_instance_class.objects.get(pk=from_instance_pk),
                          to_instance_class.objects.get(pk=to_instance_pk))


@task
def unfollow(backend_class,
             from_instance_class, from_instance_pk,
             to_instance_class, to_instance_pk):

    backend = load_class(backend_class)()

    return backend.unfollow(from_instance_class.objects.get(pk=from_instance_pk),
                            to_instance_class.objects.get(pk=to_instance_pk))
