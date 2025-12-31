from django.db import models
from django.utils import timezone


class Recipe(models.Model):
    """Recipe model representing a cooking recipe."""
    id = models.CharField(max_length=255, primary_key=True)
    userId = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    prepTime = models.IntegerField()  # in minutes
    cookTime = models.IntegerField()  # in minutes
    servings = models.IntegerField()
    imageUrl = models.URLField(max_length=500)
    createdAt = models.DateTimeField(default=timezone.now)
    updatedAt = models.DateTimeField(auto_now=True)
    
    # Many-to-many relationship with tags
    tags = models.ManyToManyField('Tag', through='RecipeTag', related_name='recipes')
    
    class Meta:
        db_table = 'recipe'
        ordering = ['-createdAt']
    
    def __str__(self):
        return self.title


class Ingredient(models.Model):
    """Ingredient model representing an ingredient in a recipe."""
    id = models.CharField(max_length=255, primary_key=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=255)
    amount = models.CharField(max_length=100)
    unit = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'ingredient'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.name} ({self.amount} {self.unit})".strip()


class Step(models.Model):
    """Step model representing a cooking step in a recipe."""
    id = models.CharField(max_length=255, primary_key=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')
    instructions = models.TextField()
    order = models.IntegerField()  # Order of the step in the recipe
    
    # Many-to-many relationship with ingredients used in this step
    ingredients = models.ManyToManyField(Ingredient, through='StepIngredient', related_name='steps')
    
    class Meta:
        db_table = 'step'
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"Step {self.order}: {self.instructions[:50]}..."


class StepIngredient(models.Model):
    """Intermediate model linking steps to ingredients."""
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'step_ingredient'
        unique_together = [['step', 'ingredient']]
    
    def __str__(self):
        return f"{self.step.id} -> {self.ingredient.name}"


class Tag(models.Model):
    """Tag model for categorizing recipes."""
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        db_table = 'tag'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """Intermediate model linking recipes to tags."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'recipe_tag'
        unique_together = [['recipe', 'tag']]
    
    def __str__(self):
        return f"{self.recipe.title} - {self.tag.name}"

