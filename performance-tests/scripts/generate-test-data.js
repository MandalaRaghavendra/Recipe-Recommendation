// generate-test-data.js - Builds rich mock data feeds for k6 load scenarios
const fs = require('fs');
const path = require('path');

const dataDir = path.join(__dirname, '..', 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

// 1. Users Feed (100 distinct users)
const users = [];
users.push({ id: 1, email: 'raghavendra@gmail.com', password: 'password123', name: 'Demo Chef' });
for (let i = 2; i <= 100; i++) {
  users.push({
    id: i,
    email: `loaduser_${i}@tastio-perf.local`,
    password: `PerfPass_${i}!@#`,
    name: `Virtual User ${i}`
  });
}
fs.writeFileSync(path.join(dataDir, 'users.json'), JSON.stringify(users, null, 2));

// 2. Search & Discovery Queries Feed
const queries = {
  text_searches: [
    'biryani', 'chicken', 'paneer', 'dosa', 'salad', 'smoothie', 'curry',
    'rice', 'pasta', 'dal', 'egg', 'fish', 'soup', 'sandwich', 'cake',
    'oats', 'idli', 'tikka', 'masala', 'noodles', 'pizza', 'roti'
  ],
  cuisines: ['Indian', 'Italian', 'Mexican', 'Asian', 'American', 'Mediterranean', 'Chinese', 'Continental'],
  meal_types: ['Breakfast', 'Lunch', 'Dinner', 'Snack'],
  diets: ['Vegetarian', 'Non-Vegetarian', 'Vegan', 'High-Protein', 'Low-Carb', 'Keto'],
  recipe_ids: Array.from({ length: 230 }, (_, i) => i + 1)
};
fs.writeFileSync(path.join(dataDir, 'queries.json'), JSON.stringify(queries, null, 2));

// 3. Pantry Ingredients Feed
const ingredients = [
  ['chicken', 'rice', 'onion', 'tomato', 'ginger', 'garlic'],
  ['paneer', 'butter', 'tomato', 'cream', 'garam masala'],
  ['egg', 'bread', 'butter', 'pepper', 'salt'],
  ['rice', 'urad dal', 'fenugreek', 'salt', 'oil'],
  ['chicken', 'curry leaves', 'mustard seeds', 'chilli', 'coconut milk'],
  ['pasta', 'olive oil', 'garlic', 'parmesan', 'basil'],
  ['oats', 'milk', 'banana', 'honey', 'chia seeds'],
  ['chickpeas', 'tahini', 'lemon', 'garlic', 'olive oil'],
  ['potato', 'cauliflower', 'turmeric', 'cumin', 'coriander'],
  ['salmon', 'lemon', 'dill', 'butter', 'asparagus']
];
fs.writeFileSync(path.join(dataDir, 'ingredients.json'), JSON.stringify(ingredients, null, 2));

// 4. Meal Plan Payloads Feed
const mealPlans = [
  { target_calories: 1800, diet_type: 'weight_loss', user_id: 1, split: 'high_protein' },
  { target_calories: 2200, diet_type: 'muscle_gain', user_id: 1, split: 'balanced' },
  { target_calories: 2000, diet_type: 'maintenance', user_id: 1, split: 'both' },
  { target_calories: 1600, diet_type: 'weight_loss', user_id: 1, split: 'vegetarian' },
  { target_calories: 2400, diet_type: 'muscle_gain', user_id: 1, split: 'non_vegetarian' }
];
fs.writeFileSync(path.join(dataDir, 'meal_plans.json'), JSON.stringify(mealPlans, null, 2));

// 5. Coach Queries Feed
const coachQueries = [
  { prompt: 'What is a healthy substitute for heavy cream in butter chicken?', user_id: 1 },
  { prompt: 'How much protein should I eat daily for muscle gain at 70kg?', user_id: 1 },
  { prompt: 'Give me 3 high protein breakfast ideas ready in under 15 minutes', user_id: 1 },
  { prompt: 'Can you analyze my weekly macros vs target calories?', user_id: 1 },
  { prompt: 'Is white rice healthy for weight loss if portions are controlled?', user_id: 1 }
];
fs.writeFileSync(path.join(dataDir, 'coach_queries.json'), JSON.stringify(coachQueries, null, 2));

// 6. Food Scanner Sample Chips Feed
const scannerSamples = [
  { dish_name: 'Hyderabadi Chicken Biryani', category: 'Rice / Non-Veg', confidence: 0.96 },
  { dish_name: 'Masala Dosa with Sambar', category: 'South Indian Breakfast', confidence: 0.94 },
  { dish_name: 'Paneer Butter Masala', category: 'North Indian Curry', confidence: 0.92 },
  { dish_name: 'Greek Salad with Feta', category: 'Salads & Greens', confidence: 0.95 },
  { dish_name: 'Banana Protein Smoothie', category: 'Beverage / Fitness', confidence: 0.97 }
];
fs.writeFileSync(path.join(dataDir, 'scanner_samples.json'), JSON.stringify(scannerSamples, null, 2));

console.log('[DataGen] Successfully generated 6 test data feeds in performance-tests/data/');

