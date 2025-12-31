"""
Management command to seed the database with recipes from mock data.
"""
from django.core.management.base import BaseCommand
from db.mocked.recipes import mock_recipes
from apps.recipe.repositories.database_recipes_repository import DatabaseRecipesRepository


class Command(BaseCommand):
    help = 'Seed the database with recipes from mock data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-seeding even if recipes already exist',
        )

    def handle(self, *args, **options):
        repository = DatabaseRecipesRepository()
        force = options['force']
        
        self.stdout.write('Starting to seed recipes...')
        
        created_count = 0
        skipped_count = 0
        
        for recipe_data in mock_recipes:
            recipe_id = recipe_data['id']
            
            # Check if recipe already exists
            existing_recipe = repository.get_by_id(recipe_id)
            
            if existing_recipe and not force:
                self.stdout.write(
                    self.style.WARNING(f'Recipe "{recipe_data["title"]}" (ID: {recipe_id}) already exists. Skipping.')
                )
                skipped_count += 1
                continue
            
            # Create the recipe
            try:
                repository.create(recipe_data)
                self.stdout.write(
                    self.style.SUCCESS(f'Created recipe: "{recipe_data["title"]}" (ID: {recipe_id})')
                )
                created_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating recipe "{recipe_data["title"]}": {str(e)}')
                )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Seeding complete!'))
        self.stdout.write(f'  Created: {created_count} recipes')
        if skipped_count > 0:
            self.stdout.write(f'  Skipped: {skipped_count} recipes (already exist)')
            self.stdout.write(self.style.WARNING('  Use --force to re-seed existing recipes'))

