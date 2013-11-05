from celery.task import task


@task
def follow(backend_class,
           from_instance_class, from_instance_pk,
           to_instance_class, to_instance_pk):

    return backend_class().follow(from_instance_class.objects.get(pk=from_instance_pk),
                                  to_instance_class.objects.get(pk=to_instance_pk))


@task
def unfollow(backend_class,
             from_instance_class, from_instance_pk,
             to_instance_class, to_instance_pk):

    return backend_class().unfollow(from_instance_class.objects.get(pk=from_instance_pk),
                                    to_instance_class.objects.get(pk=to_instance_pk))
