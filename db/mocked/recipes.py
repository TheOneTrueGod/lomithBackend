from typing import TypedDict, List


class Ingredient(TypedDict):
    id: str
    name: str
    amount: str
    unit: str


class Step(TypedDict):
    id: str
    instructions: str
    ingredients: List[str]


class Recipe(TypedDict):
    id: str
    userId: str
    title: str
    description: str
    prepTime: int
    cookTime: int
    servings: int
    imageUrl: str
    ingredients: List[Ingredient]
    steps: List[Step]
    tags: List[str]
    createdAt: str
    updatedAt: str


mock_recipes: List[Recipe] = [
    {
        "id": "1",
        "userId": "1",
        "title": "Classic Spaghetti Carbonara",
        "description": "A traditional Italian pasta dish with eggs, cheese, pancetta, and black pepper.",
        "prepTime": 15,
        "cookTime": 20,
        "servings": 4,
        "imageUrl": "https://images.pexels.com/photos/4198023/pexels-photo-4198023.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
        "ingredients": [
            {"id": "1-1", "name": "Spaghetti", "amount": "400", "unit": "g"},
            {"id": "1-2", "name": "Pancetta", "amount": "150", "unit": "g"},
            {"id": "1-3", "name": "Egg Yolks", "amount": "6", "unit": ""},
            {"id": "1-4", "name": "Parmesan", "amount": "50", "unit": "g"},
            {"id": "1-5", "name": "Black Pepper", "amount": "1", "unit": "tsp"},
            {"id": "1-6", "name": "Salt", "amount": "", "unit": "to taste"},
        ],
        "steps": [
            {
                "id": "1-1",
                "instructions": "Bring a large pot of salted water to boil. Add the spaghetti and cook until al dente.",
                "ingredients": ["1-1", "1-6"],
            },
            {
                "id": "1-2",
                "instructions": "While pasta is cooking, heat a large skillet over medium heat. Add the pancetta and cook until crispy.",
                "ingredients": ["1-2"],
            },
            {
                "id": "1-3",
                "instructions": "In a bowl, whisk together the egg yolks, grated parmesan, and black pepper.",
                "ingredients": ["1-3", "1-4", "1-5"],
            },
            {
                "id": "1-4",
                "instructions": "Drain the pasta, reserving 1/2 cup of pasta water. Add pasta to the skillet with the pancetta and toss to combine.",
                "ingredients": ["1-1", "1-2"],
            },
            {
                "id": "1-5",
                "instructions": "Remove skillet from heat, add the egg mixture and quickly toss to coat the pasta, creating a creamy sauce. If needed, add a splash of reserved pasta water to loosen the sauce.",
                "ingredients": ["1-3", "1-4", "1-5"],
            },
            {
                "id": "1-6",
                "instructions": "Serve immediately with extra grated parmesan and freshly ground black pepper.",
                "ingredients": ["1-4", "1-5"],
            },
        ],
        "tags": ["Italian", "Pasta", "Quick", "Dinner"],
        "createdAt": "2023-09-15T10:30:00Z",
        "updatedAt": "2023-09-15T10:30:00Z",
    },
    {
        "id": "2",
        "userId": "1",
        "title": "Avocado Toast with Poached Eggs",
        "description": "A simple, nutritious breakfast that combines creamy avocado with perfectly poached eggs.",
        "prepTime": 10,
        "cookTime": 5,
        "servings": 2,
        "imageUrl": "https://images.pexels.com/photos/704569/pexels-photo-704569.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
        "ingredients": [
            {"id": "2-1", "name": "Bread", "amount": "2", "unit": "slices"},
            {"id": "2-2", "name": "Avocado", "amount": "1", "unit": "large"},
            {"id": "2-3", "name": "Eggs", "amount": "2", "unit": ""},
            {"id": "2-4", "name": "Vinegar", "amount": "1", "unit": "tbsp"},
            {"id": "2-5", "name": "Lemon Juice", "amount": "1", "unit": "tsp"},
            {"id": "2-6", "name": "Salt", "amount": "", "unit": "to taste"},
            {"id": "2-7", "name": "Pepper", "amount": "", "unit": "to taste"},
            {"id": "2-8", "name": "Red Pepper Flakes", "amount": "1/4", "unit": "tsp"},
        ],
        "steps": [
            {
                "id": "2-1",
                "instructions": "Fill a saucepan with water, add vinegar, and bring to a simmer.",
                "ingredients": ["2-4"],
            },
            {
                "id": "2-2",
                "instructions": "Crack each egg into a small bowl. Create a gentle whirlpool in the water and carefully slide in the eggs. Cook for 3-4 minutes for a runny yolk.",
                "ingredients": ["2-3"],
            },
            {
                "id": "2-3",
                "instructions": "While eggs are cooking, toast the bread slices until golden brown.",
                "ingredients": ["2-1"],
            },
            {
                "id": "2-4",
                "instructions": "Cut the avocado in half, remove the pit, and scoop the flesh into a bowl. Add lemon juice, salt, and pepper. Mash with a fork until desired consistency.",
                "ingredients": ["2-2", "2-5", "2-6", "2-7"],
            },
            {
                "id": "2-5",
                "instructions": "Spread the mashed avocado evenly on the toast slices.",
                "ingredients": ["2-1", "2-2"],
            },
            {
                "id": "2-6",
                "instructions": "Using a slotted spoon, remove the poached eggs from water and place on top of the avocado toast. Sprinkle with red pepper flakes and serve immediately.",
                "ingredients": ["2-3", "2-8"],
            },
        ],
        "tags": ["Breakfast", "Vegetarian", "Healthy", "Quick"],
        "createdAt": "2023-10-02T08:15:00Z",
        "updatedAt": "2023-10-02T08:15:00Z",
    },
    {
        "id": "3",
        "userId": "1",
        "title": "Classic Chocolate Chip Cookies",
        "description": "Soft and chewy cookies with melted chocolate chips - a family favorite!",
        "prepTime": 15,
        "cookTime": 12,
        "servings": 24,
        "imageUrl": "https://images.pexels.com/photos/230325/pexels-photo-230325.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
        "ingredients": [
            {
                "id": "3-1",
                "name": "All-Purpose Flour",
                "amount": "2 1/4",
                "unit": "cups",
            },
            {"id": "3-2", "name": "Baking Soda", "amount": "1", "unit": "tsp"},
            {"id": "3-3", "name": "Salt", "amount": "1", "unit": "tsp"},
            {"id": "3-4", "name": "Unsalted Butter", "amount": "1", "unit": "cup"},
            {"id": "3-5", "name": "Brown Sugar", "amount": "3/4", "unit": "cup"},
            {"id": "3-6", "name": "Granulated Sugar", "amount": "3/4", "unit": "cup"},
            {"id": "3-7", "name": "Vanilla Extract", "amount": "1", "unit": "tsp"},
            {"id": "3-8", "name": "Eggs", "amount": "2", "unit": "large"},
            {"id": "3-9", "name": "Chocolate Chips", "amount": "2", "unit": "cups"},
        ],
        "steps": [
            {
                "id": "3-1",
                "instructions": "Preheat oven to 375°F (190°C). Line baking sheets with parchment paper.",
                "ingredients": [],
            },
            {
                "id": "3-2",
                "instructions": "In a small bowl, whisk together flour, baking soda, and salt.",
                "ingredients": ["3-1", "3-2", "3-3"],
            },
            {
                "id": "3-3",
                "instructions": "In a large bowl, beat butter, brown sugar, and granulated sugar until creamy.",
                "ingredients": ["3-4", "3-5", "3-6"],
            },
            {
                "id": "3-4",
                "instructions": "Add vanilla extract and eggs to the butter mixture, one at a time, beating well after each addition.",
                "ingredients": ["3-7", "3-8"],
            },
            {
                "id": "3-5",
                "instructions": "Gradually stir in the flour mixture until just combined. Do not overmix.",
                "ingredients": ["3-1", "3-2", "3-3"],
            },
            {
                "id": "3-6",
                "instructions": "Fold in the chocolate chips.",
                "ingredients": ["3-9"],
            },
            {
                "id": "3-7",
                "instructions": "Drop rounded tablespoons of dough onto the prepared baking sheets, spacing them about 2 inches apart.",
                "ingredients": [],
            },
            {
                "id": "3-8",
                "instructions": "Bake for 9-12 minutes or until edges are golden brown but centers are still soft. Cool on baking sheets for 2 minutes before transferring to wire racks to cool completely.",
                "ingredients": [],
            },
        ],
        "tags": ["Dessert", "Baking", "Cookies", "Chocolate"],
        "createdAt": "2023-08-25T15:45:00Z",
        "updatedAt": "2023-08-25T15:45:00Z",
    },
]
