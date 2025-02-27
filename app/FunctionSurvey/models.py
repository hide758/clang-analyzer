from django.db import models

class Project(models.Model):
    """Project Model
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length = 256,
        null=True
    )

    class Meta:
        db_table = 'project'

    def __str__(self):
        return f"{self.name}"


class Function(models.Model):
    """Function Model
    """

    id = models.AutoField(primary_key=True)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='functioin_project',
        null=True)
    
    name = models.CharField(
        max_length = 256
        )
    
    return_type = models.CharField(
        max_length = 128
        )
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

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='functioin_relation_project',
        null=True)
    
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
