from django.db import models


class Function(models.Model):
    """Function Model
    """

    id = models.AutoField(primary_key=True)
    name = models.TextField()
    return_type = models.TextField()
    arguments = models.JSONField()
    file = models.TextField()
    line = models.IntegerField()

    static = models.BooleanField(default=False)
    const = models.BooleanField(default=False)
    is_prototype = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'function'

    def __str__(self):
        return f"{self.name}"

class FunctionRelation(models.Model):
    """Function Relation Model
    """
    id = models.AutoField(primary_key=True)

    call_from = models.ForeignKey(
        Function,
        on_delete=models.CASCADE,
        related_name='call_from')
    
    call_to = models.ForeignKey(
        Function,
        on_delete=models.CASCADE,
        related_name='call_to')

    file = models.TextField()
    line = models.IntegerField()

    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'function_relation'

    def __str__(self):
        return f"{self.call_from} -> {self.call_to}"
