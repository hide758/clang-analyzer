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
    end_line = models.IntegerField(null=True)

    static = models.BooleanField(default=False)
    const = models.BooleanField(default=False)
    is_prototype = models.BooleanField(default=True)

    include_for     = models.BooleanField(default=False, null=True)
    include_if      = models.BooleanField(default=False, null=True)
    include_switch  = models.BooleanField(default=False, null=True)
    include_while   = models.BooleanField(default=False, null=True)
    include_do      = models.BooleanField(default=False, null=True)

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
        related_name='call_from',
        null=True)
    
    call_to = models.ForeignKey(
        Function,
        on_delete=models.CASCADE,
        related_name='call_to',
        null=True)

    file = models.TextField()
    line = models.IntegerField()

    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'function_relation'

    def __str__(self):
        return f"{self.call_from} -> {self.call_to}"


class Variable(models.Model):
    """Variable Model
    """

    id = models.AutoField(primary_key=True)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='variable_project',
        null=True)
    
    scope = models.ForeignKey(
        Function,
        on_delete=models.CASCADE,
        related_name='variable_function',
        null=True)

    type = models.CharField(
        max_length = 128
        )

    name = models.CharField(
        max_length = 256
        )
    
    file = models.TextField()
    line = models.IntegerField()

    static = models.BooleanField(default=False)
    const = models.BooleanField(default=False)
    is_pointer = models.BooleanField(default=True)
    is_prototype = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'variable'

    def __str__(self):
        return f"{self.scope}::{self.name}"
