from django_random_queryset import RandomManager


class RandomManagerMixin:
    """Allows selection of a random item from a queryset."""

    objects = RandomManager()


class LockableModelMixin:
    def lock_me(self):
        # todo: is there a better way to do this?
        self.__class__.objects.select_for_update().get(id=self.id)
        self.refresh_from_db()
