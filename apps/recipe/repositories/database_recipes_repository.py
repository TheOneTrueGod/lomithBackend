"""
Database implementation of RecipesRepository using Django ORM.
"""
from typing import List, Optional, Tuple
from django.db.models import Q, Prefetch
from django.utils import timezone
from datetime import datetime
from db.mocked.recipes import Recipe, Ingredient as IngredientDict, Step as StepDict
from .recipes_repository import RecipesRepository
from apps.recipe.models import Recipe as RecipeModel, Ingredient as IngredientModel, Step as StepModel, Tag, RecipeTag, StepIngredient


class DatabaseRecipesRepository(RecipesRepository):
    """Repository implementation using Django ORM for database access."""
    
    def _model_to_dict(self, recipe_model: RecipeModel) -> Recipe:
        """
        Convert a Django Recipe model instance to Recipe TypedDict format.
        
        Args:
            recipe_model: Django Recipe model instance
            
        Returns:
            Recipe dictionary in TypedDict format
        """
        # Get all ingredients for this recipe
        ingredients = [
            {
                'id': str(ing.id),  # Convert auto-incrementing ID to string
                'name': ing.name,
                'amount': ing.amount,
                'unit': ing.unit,
            }
            for ing in recipe_model.ingredients.all()
        ]
        
        # Get all steps with their associated ingredients
        steps = []
        for step in recipe_model.steps.all().prefetch_related('ingredients'):
            # Get ingredient IDs for this step (convert to strings)
            step_ingredient_ids = [str(ing.id) for ing in step.ingredients.all()]
            steps.append({
                'id': str(step.id),  # Convert auto-incrementing ID to string
                'instructions': step.instructions,
                'ingredients': step_ingredient_ids,
            })
        
        # Get all tags for this recipe
        tags = [tag.name for tag in recipe_model.tags.all()]
        
        # Convert datetime to ISO format string
        created_at_str = recipe_model.createdAt.isoformat() if recipe_model.createdAt else ''
        updated_at_str = recipe_model.updatedAt.isoformat() if recipe_model.updatedAt else ''
        
        return {
            'id': str(recipe_model.id),  # Convert auto-incrementing ID to string
            'userId': recipe_model.userId,
            'title': recipe_model.title,
            'description': recipe_model.description,
            'prepTime': recipe_model.prepTime,
            'cookTime': recipe_model.cookTime,
            'servings': recipe_model.servings,
            'imageUrl': recipe_model.imageUrl,
            'ingredients': ingredients,
            'steps': steps,
            'tags': tags,
            'createdAt': created_at_str,
            'updatedAt': updated_at_str,
        }
    
    def get_list(
        self,
        user_id: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Recipe], int]:
        """
        Retrieve a paginated list of recipes with optional filtering.
        All filtering, searching, and pagination is handled in one query.
        """
        # Start with base queryset
        queryset = RecipeModel.objects.all()
        
        # Apply user_id filter if provided
        if user_id:
            queryset = queryset.filter(userId=user_id)
        
        # Apply search filter if provided
        if search:
            query_lower = search.lower()
            queryset = queryset.filter(
                Q(title__icontains=query_lower) |
                Q(description__icontains=query_lower) |
                Q(tags__name__icontains=query_lower)
            ).distinct()
        
        # Get total count before pagination
        total = queryset.count()
        
        # Apply pagination
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        # Prefetch related objects for efficiency
        queryset = queryset.prefetch_related(
            'ingredients',
            Prefetch('steps', queryset=StepModel.objects.prefetch_related('ingredients')),
            'tags'
        )
        
        # Get paginated results
        paginated_recipes = queryset[start_index:end_index]
        
        # Convert to dict format
        return [self._model_to_dict(recipe) for recipe in paginated_recipes], total
    
    def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """
        Retrieve a recipe by its ID.
        Handles both string and integer IDs (converts string to int if needed).
        """
        try:
            # Try to convert to int (for auto-incrementing IDs)
            try:
                recipe_id_int = int(recipe_id)
            except ValueError:
                recipe_id_int = recipe_id
            
            recipe = RecipeModel.objects.prefetch_related(
                'ingredients',
                Prefetch('steps', queryset=StepModel.objects.prefetch_related('ingredients')),
                'tags'
            ).get(id=recipe_id_int)
            return self._model_to_dict(recipe)
        except RecipeModel.DoesNotExist:
            return None
    
    def create(self, recipe: Recipe) -> Recipe:
        """
        Create a new recipe.
        Note: id is auto-generated by the database, so it's not required in the recipe dict.
        """
        # Parse datetime strings (handle ISO format with 'Z' suffix)
        if recipe.get('createdAt'):
            created_at_str = recipe['createdAt'].replace('Z', '+00:00')
            created_at = datetime.fromisoformat(created_at_str)
            if timezone.is_naive(created_at):
                created_at = timezone.make_aware(created_at)
        else:
            created_at = timezone.now()
        
        if recipe.get('updatedAt'):
            updated_at_str = recipe['updatedAt'].replace('Z', '+00:00')
            updated_at = datetime.fromisoformat(updated_at_str)
            if timezone.is_naive(updated_at):
                updated_at = timezone.make_aware(updated_at)
        else:
            updated_at = timezone.now()
        
        # Create Recipe instance (id is auto-generated)
        recipe_model = RecipeModel.objects.create(
            userId=recipe['userId'],
            title=recipe['title'],
            description=recipe['description'],
            prepTime=recipe['prepTime'],
            cookTime=recipe['cookTime'],
            servings=recipe['servings'],
            imageUrl=recipe.get('imageUrl'),  # Optional field
            createdAt=created_at,
            updatedAt=updated_at,
        )
        
        # Create ingredients (id is auto-generated in database, but we track request IDs for linking)
        created_ingredients = []
        ingredient_id_map = {}  # Maps request ingredient ID to database ingredient object
        
        for idx, ing_data in enumerate(recipe.get('ingredients', [])):
            ingredient = IngredientModel.objects.create(
                recipe=recipe_model,
                name=ing_data['name'],
                amount=ing_data['amount'],
                unit=ing_data.get('unit', ''),
            )
            created_ingredients.append(ingredient)
            
            # Map request ingredient ID to database ingredient
            # If request has an ID, use it; otherwise generate one based on index
            request_id = ing_data.get('id', str(idx))
            ingredient_id_map[request_id] = ingredient
            # Also map by index for convenience (in case steps reference by index)
            ingredient_id_map[str(idx)] = ingredient
        
        # Create steps and link ingredients (id is auto-generated)
        
        for idx, step_data in enumerate(recipe.get('steps', []), start=1):
            step_model = StepModel.objects.create(
                recipe=recipe_model,
                instructions=step_data['instructions'],
                order=idx,  # Use enumerate index as order
            )
            
            # Link ingredients to step
            # step_data['ingredients'] contains ingredient IDs (strings) from the request
            # Map them to the actual ingredient objects
            ingredient_ids = step_data.get('ingredients', [])
            step_ingredients = []
            for ing_id in ingredient_ids:
                if ing_id in ingredient_id_map:
                    step_ingredients.append(ingredient_id_map[ing_id])
            
            step_model.ingredients.set(step_ingredients)
        
        # Create or get tags and link to recipe
        for tag_name in recipe.get('tags', []):
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            RecipeTag.objects.get_or_create(recipe=recipe_model, tag=tag)
        
        # Return the created recipe (id is now available from the model)
        return self.get_by_id(str(recipe_model.id))
    
    def update(self, recipe_id: str, recipe_data: Recipe) -> Optional[Recipe]:
        """
        Update an existing recipe.
        Handles both string and integer IDs (converts string to int if needed).
        """
        try:
            # Try to convert to int (for auto-incrementing IDs)
            try:
                recipe_id_int = int(recipe_id)
            except ValueError:
                recipe_id_int = recipe_id
            
            recipe_model = RecipeModel.objects.get(id=recipe_id_int)
        except RecipeModel.DoesNotExist:
            return None
        
        # Update basic fields
        if 'userId' in recipe_data:
            recipe_model.userId = recipe_data['userId']
        if 'title' in recipe_data:
            recipe_model.title = recipe_data['title']
        if 'description' in recipe_data:
            recipe_model.description = recipe_data['description']
        if 'prepTime' in recipe_data:
            recipe_model.prepTime = recipe_data['prepTime']
        if 'cookTime' in recipe_data:
            recipe_model.cookTime = recipe_data['cookTime']
        if 'servings' in recipe_data:
            recipe_model.servings = recipe_data['servings']
        if 'imageUrl' in recipe_data:
            recipe_model.imageUrl = recipe_data['imageUrl']
        if 'updatedAt' in recipe_data:
            updated_at_str = recipe_data['updatedAt'].replace('Z', '+00:00')
            updated_at = datetime.fromisoformat(updated_at_str)
            if timezone.is_naive(updated_at):
                updated_at = timezone.make_aware(updated_at)
            recipe_model.updatedAt = updated_at
        
        recipe_model.save()
        
        # Update ingredients if provided
        if 'ingredients' in recipe_data:
            # Delete existing ingredients
            IngredientModel.objects.filter(recipe=recipe_model).delete()
            # Create new ingredients (id is auto-generated)
            created_ingredients = []
            ingredient_id_map = {}
            for idx, ing_data in enumerate(recipe_data['ingredients']):
                ingredient = IngredientModel.objects.create(
                    recipe=recipe_model,
                    name=ing_data['name'],
                    amount=ing_data['amount'],
                    unit=ing_data.get('unit', ''),
                )
                created_ingredients.append(ingredient)
                # Map request ingredient ID to database ingredient
                request_id = ing_data.get('id', str(idx))
                ingredient_id_map[request_id] = ingredient
                ingredient_id_map[str(idx)] = ingredient
        
        # Update steps if provided
        if 'steps' in recipe_data:
            # Delete existing steps
            StepModel.objects.filter(recipe=recipe_model).delete()
            # Create new steps (id is auto-generated)
            for idx, step_data in enumerate(recipe_data['steps'], start=1):
                step_model = StepModel.objects.create(
                    recipe=recipe_model,
                    instructions=step_data['instructions'],
                    order=idx,
                )
                # Link ingredients to step using the ingredient_id_map
                ingredient_ids = step_data.get('ingredients', [])
                step_ingredients = []
                for ing_id in ingredient_ids:
                    if ing_id in ingredient_id_map:
                        step_ingredients.append(ingredient_id_map[ing_id])
                step_model.ingredients.set(step_ingredients)
        
        # Update tags if provided
        if 'tags' in recipe_data:
            # Clear existing tags
            RecipeTag.objects.filter(recipe=recipe_model).delete()
            # Create or get tags and link to recipe
            for tag_name in recipe_data['tags']:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                RecipeTag.objects.get_or_create(recipe=recipe_model, tag=tag)
        
        # Return the updated recipe
        return self.get_by_id(recipe_id)
    
    def delete(self, recipe_id: str) -> bool:
        """
        Delete a recipe by its ID.
        Handles both string and integer IDs (converts string to int if needed).
        """
        try:
            # Try to convert to int (for auto-incrementing IDs)
            try:
                recipe_id_int = int(recipe_id)
            except ValueError:
                recipe_id_int = recipe_id
            
            recipe = RecipeModel.objects.get(id=recipe_id_int)
            recipe.delete()
            return True
        except RecipeModel.DoesNotExist:
            return False

