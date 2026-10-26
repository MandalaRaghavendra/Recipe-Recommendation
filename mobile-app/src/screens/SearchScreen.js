import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
  Alert,
  RefreshControl
} from "react-native";
import { Colors } from "../theme/colors";
import RecipeCard from "../components/RecipeCard";
import {
  recommendRecipes,
  matchPantryRecipes,
  fetchFilteredRecipes,
  recordRecipeView,
  fetchRecipes
} from "../services/api";

const QUICK_CHIPS = ["chicken", "rice", "tomato", "onion", "paneer", "potato", "eggs", "spinach", "dal", "garlic"];

const CUISINE_OPTIONS = [
  "All", "Andhra", "Telangana", "South Indian", "North Indian", "Punjabi",
  "Gujarati", "Bengali", "Maharashtrian", "Kerala", "Karnataka", "Tamil Nadu"
];

const MEAL_TYPE_OPTIONS = ["All", "Breakfast", "Lunch", "Dinner", "Snack", "Dessert"];

const DIET_OPTIONS = ["All", "Vegetarian", "Non-Vegetarian", "Vegan"];

const NUTRITION_OPTIONS = [
  { id: "High Protein", label: "💪 High Protein (>20g)", query: "high protein" },
  { id: "Low Calorie", label: "🔥 Low Calorie (<350 kcal)", query: "low calorie" },
  { id: "High Fiber", label: "🌾 High Fiber", query: "high fiber" },
  { id: "Muscle Gain", label: "🥩 Muscle Gain", query: "muscle gain" },
  { id: "Weight Loss", label: "⚖️ Weight Loss", query: "weight loss" },
  { id: "Balanced", label: "🥗 Balanced Diet", query: "balanced" },
  { id: "under_400", label: "⚡ Under 400 kcal", query: "under 400 cal" },
  { id: "low_carb", label: "🥑 Low Carb / Keto", query: "keto" }
];

export default function SearchScreen({ onSelectRecipe, userId = null }) {
  const [mode, setMode] = useState("search"); // 'search' | 'nutrition' | 'pantry' | 'cuisine'
  const [ingredients, setIngredients] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [searched, setSearched] = useState(false);

  // Facet filter states
  const [selectedCuisine, setSelectedCuisine] = useState("All");
  const [selectedMealType, setSelectedMealType] = useState("All");
  const [selectedDiet, setSelectedDiet] = useState("All");
  const [selectedNutrition, setSelectedNutrition] = useState("All");

  useEffect(() => {
    // Initial popular recipes load
    loadInitialRecipes();
  }, []);

  const loadInitialRecipes = async () => {
    setLoading(true);
    const data = await fetchRecipes("all", "");
    setResults(data || []);
    setLoading(false);
  };

  const handleSearch = async (overrideQuery = null, overrideTag = null) => {
    const activeQuery = overrideQuery !== null ? overrideQuery : ingredients;
    const activeTag = overrideTag !== null ? overrideTag : selectedNutrition;

    setLoading(true);
    setSearched(true);
    let data = [];

    if (mode === "pantry") {
      if (!activeQuery.trim()) {
        Alert.alert("Enter Ingredients", "Please type ingredients (e.g., chicken, rice) or tap quick ingredient chips below.");
        setLoading(false);
        return;
      }
      data = await matchPantryRecipes(activeQuery, userId, 16);
    } else if (mode === "search") {
      if (!activeQuery.trim()) {
        const res = await fetchRecipes("all", "");
        data = res || [];
      } else {
        const res = await fetchFilteredRecipes({
          query: activeQuery.trim(),
          cuisine: selectedCuisine,
          meal_type: selectedMealType
        });
        data = res.recipes || [];
      }
    } else if (mode === "nutrition") {
      const res = await fetchFilteredRecipes({
        nutrition_tag: activeTag !== "All" ? activeTag : undefined,
        query: activeQuery.trim(),
        diet: selectedDiet !== "All" ? selectedDiet : undefined
      });
      data = res.recipes || [];
    } else if (mode === "cuisine") {
      const res = await fetchFilteredRecipes({
        cuisine: selectedCuisine,
        meal_type: selectedMealType,
        diet: selectedDiet,
        nutrition_tag: selectedNutrition,
        query: activeQuery.trim()
      });
      data = res.recipes || [];
    }

    setResults(data);
    setLoading(false);
    setRefreshing(false);
  };

  const handleNutritionChipPress = (item) => {
    setSelectedNutrition(item.id);
    setIngredients(item.query);
    handleSearch(item.query, item.id);
  };

  const handleFacetChange = async (type, val) => {
    let newCuisine = selectedCuisine;
    let newMealType = selectedMealType;
    let newDiet = selectedDiet;
    let newNutrition = selectedNutrition;

    if (type === "cuisine") { setSelectedCuisine(val); newCuisine = val; }
    if (type === "meal_type") { setSelectedMealType(val); newMealType = val; }
    if (type === "diet") { setSelectedDiet(val); newDiet = val; }
    if (type === "nutrition") { setSelectedNutrition(val); newNutrition = val; }

    setLoading(true);
    setSearched(true);
    const res = await fetchFilteredRecipes({
      cuisine: newCuisine,
      meal_type: newMealType,
      diet: newDiet,
      nutrition_tag: newNutrition,
      query: ingredients.trim()
    });
    setResults(res.recipes || []);
    setLoading(false);
  };

  const addChip = (item) => {
    const current = ingredients.trim();
    let updated = "";
    if (!current) {
      updated = item;
    } else {
      const parts = current.split(",").map((p) => p.trim().toLowerCase());
      if (!parts.includes(item.toLowerCase())) {
        updated = `${current}, ${item}`;
      } else {
        updated = current;
      }
    }
    setIngredients(updated);
    if (updated) {
      handleSearch(updated);
    }
  };

  const handleRecipePress = (recipe) => {
    if (recipe && recipe.recipe_id) {
      recordRecipeView(recipe.recipe_id, userId);
    }
    if (onSelectRecipe) {
      onSelectRecipe(recipe);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    handleSearch();
  };

  return (
    <View style={styles.container}>
      {/* Top Header & Navigation Modes */}
      <View style={styles.header}>
        <View style={styles.tabRow}>
          <TouchableOpacity
            style={[styles.tabBtn, mode === "search" && styles.tabBtnActive]}
            onPress={() => { setMode("search"); }}
          >
            <Text style={[styles.tabText, mode === "search" && styles.tabTextActive]}>
              🔍 AI Search
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.tabBtn, mode === "nutrition" && styles.tabBtnActive]}
            onPress={() => { setMode("nutrition"); handleSearch("", "High Protein"); }}
          >
            <Text style={[styles.tabText, mode === "nutrition" && styles.tabTextActive]}>
              🥗 Nutrition
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.tabBtn, mode === "pantry" && styles.tabBtnActive]}
            onPress={() => { setMode("pantry"); }}
          >
            <Text style={[styles.tabText, mode === "pantry" && styles.tabTextActive]}>
              🥘 Pantry
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.tabBtn, mode === "cuisine" && styles.tabBtnActive]}
            onPress={() => { setMode("cuisine"); handleFacetChange("cuisine", selectedCuisine); }}
          >
            <Text style={[styles.tabText, mode === "cuisine" && styles.tabTextActive]}>
              🏛️ Cuisines
            </Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.subTitle}>
          {mode === "search"
            ? "Search dishes, ingredients, or macro targets using AI"
            : mode === "nutrition"
            ? "Filter verified recipes by calories, protein & macro targets"
            : mode === "pantry"
            ? "Enter ingredients in your kitchen to discover cookable meals"
            : "Explore authentic regional cuisines from across India"}
        </Text>
      </View>

      {/* Input / Filter Section */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder={
            mode === "pantry"
              ? "e.g. chicken, rice, tomato, onion"
              : mode === "nutrition"
              ? "Search by macro target (e.g. high protein, under 400 cal)"
              : mode === "search"
              ? "e.g. biryani, paneer, dal, fish curry"
              : "Search within regional cuisines..."
          }
          placeholderTextColor="#94A3B8"
          value={ingredients}
          onChangeText={setIngredients}
          onSubmitEditing={() => handleSearch()}
          returnKeyType="search"
        />

        {/* Quick Chips for Pantry Mode */}
        {mode === "pantry" && (
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.chipsScroll}>
            {QUICK_CHIPS.map((chip) => (
              <TouchableOpacity key={chip} style={styles.chip} onPress={() => addChip(chip)}>
                <Text style={styles.chipText}>+{chip}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        )}

        {/* Nutrition Goal Quick Chips */}
        {mode === "nutrition" && (
          <View style={styles.facetWrap}>
            <Text style={styles.facetLabel}>TARGET MACRO & NUTRITION GOALS</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.facetRow}>
              {NUTRITION_OPTIONS.map((item) => (
                <TouchableOpacity
                  key={item.id}
                  style={[styles.facetChip, selectedNutrition === item.id && styles.facetChipActiveWarning]}
                  onPress={() => handleNutritionChipPress(item)}
                >
                  <Text style={[styles.facetChipText, selectedNutrition === item.id && styles.facetChipTextActive]}>
                    {item.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>

            <Text style={styles.facetLabel}>DIETARY PREFERENCE</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.facetRow}>
              {DIET_OPTIONS.map((d) => (
                <TouchableOpacity
                  key={`diet-${d}`}
                  style={[styles.facetChip, selectedDiet === d && styles.facetChipActivePrimary]}
                  onPress={() => { setSelectedDiet(d); handleFacetChange("diet", d); }}
                >
                  <Text style={[styles.facetChipText, selectedDiet === d && styles.facetChipTextActive]}>
                    {d}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        )}

        {/* Cuisines Mode Facets */}
        {mode === "cuisine" && (
          <View style={styles.facetWrap}>
            <Text style={styles.facetLabel}>REGIONAL INDIAN CUISINES</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.facetRow}>
              {CUISINE_OPTIONS.map((c) => (
                <TouchableOpacity
                  key={`c-${c}`}
                  style={[styles.facetChip, selectedCuisine === c && styles.facetChipActive]}
                  onPress={() => handleFacetChange("cuisine", c)}
                >
                  <Text style={[styles.facetChipText, selectedCuisine === c && styles.facetChipTextActive]}>
                    {c}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>

            <Text style={styles.facetLabel}>MEAL OCCASION</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.facetRow}>
              {MEAL_TYPE_OPTIONS.map((m) => (
                <TouchableOpacity
                  key={`m-${m}`}
                  style={[styles.facetChip, selectedMealType === m && styles.facetChipActivePrimary]}
                  onPress={() => handleFacetChange("meal_type", m)}
                >
                  <Text style={[styles.facetChipText, selectedMealType === m && styles.facetChipTextActive]}>
                    {m}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        )}

        <TouchableOpacity style={styles.btn} onPress={() => handleSearch()} activeOpacity={0.8}>
          <Text style={styles.btnText}>
            {mode === "pantry"
              ? "🥘 Match My Pantry"
              : mode === "nutrition"
              ? "🥗 Search by Nutrients"
              : mode === "search"
              ? "🔍 Find Recipes"
              : "✨ Filter Cuisines"}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Results Header */}
      <View style={styles.resultHeaderRow}>
        <Text style={styles.resultHeaderTitle}>
          {results.length > 0 ? `Recipes (${results.length})` : "Recipes"}
        </Text>
        {results.length > 0 && (
          <Text style={styles.resultHeaderSub}>
            {mode === "pantry" ? "Ranked by ingredient availability" : "Verified database nutrition"}
          </Text>
        )}
      </View>

      {/* Results List */}
      {loading ? (
        <View style={styles.loadingBox}>
          <ActivityIndicator size="large" color={Colors.accent} />
          <Text style={styles.loadingText}>Searching recipe database...</Text>
        </View>
      ) : (
        <FlatList
          data={results}
          keyExtractor={(item, index) => String(item.recipe_id || index)}
          renderItem={({ item }) => (
            <RecipeCard recipe={item} onPress={() => handleRecipePress(item)} />
          )}
          initialNumToRender={6}
          maxToRenderPerBatch={8}
          windowSize={5}
          removeClippedSubviews={true}
          contentContainerStyle={styles.list}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={["#7B2C3F"]} />
          }
          ListEmptyComponent={
            searched ? (
              <View style={styles.emptyBox}>
                <Text style={styles.emptyTitle}>No Recipes Found</Text>
                <Text style={styles.emptyText}>
                  Try selecting different filters or searching for ingredients like chicken, paneer, or dal.
                </Text>
              </View>
            ) : (
              <View style={styles.emptyBox}>
                <Text style={styles.emptyTitle}>
                  {mode === "pantry"
                    ? "What's in your kitchen?"
                    : mode === "nutrition"
                    ? "Choose a nutrient target above"
                    : "Discover delicious meals"}
                </Text>
                <Text style={styles.emptyText}>
                  Explore personalized recommendations crafted from 198 authentic recipes.
                </Text>
              </View>
            )
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F4F6F9"
  },
  header: {
    padding: 12,
    backgroundColor: "#FFFFFF",
    borderBottomWidth: 1,
    borderBottomColor: "#E2E8F0"
  },
  tabRow: {
    flexDirection: "row",
    gap: 6,
    marginBottom: 8
  },
  tabBtn: {
    flex: 1,
    paddingVertical: 9,
    borderRadius: 10,
    backgroundColor: "#F1F5F9",
    alignItems: "center"
  },
  tabBtnActive: {
    backgroundColor: Colors.primary
  },
  tabText: {
    fontSize: 12,
    fontWeight: "700",
    color: "#475569"
  },
  tabTextActive: {
    color: "#FFFFFF"
  },
  subTitle: {
    fontSize: 12,
    color: "#64748B",
    textAlign: "center"
  },
  inputContainer: {
    padding: 14,
    backgroundColor: "#FFFFFF",
    marginBottom: 8
  },
  input: {
    backgroundColor: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#CBD5E1",
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 14,
    color: "#1E293B",
    marginBottom: 10
  },
  chipsScroll: {
    flexDirection: "row",
    marginBottom: 10
  },
  chip: {
    backgroundColor: "#FEF3C7",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 6
  },
  chipText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#92400E"
  },
  facetWrap: {
    marginBottom: 10
  },
  facetLabel: {
    fontSize: 11,
    fontWeight: "800",
    color: "#64748B",
    letterSpacing: 0.5,
    marginTop: 6,
    marginBottom: 6
  },
  facetRow: {
    flexDirection: "row",
    marginBottom: 4
  },
  facetChip: {
    backgroundColor: "#F1F5F9",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 6,
    borderWidth: 1,
    borderColor: "#E2E8F0"
  },
  facetChipActive: {
    backgroundColor: "#334155",
    borderColor: "#334155"
  },
  facetChipActivePrimary: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary
  },
  facetChipActiveWarning: {
    backgroundColor: "#D97706",
    borderColor: "#D97706"
  },
  facetChipText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#475569"
  },
  facetChipTextActive: {
    color: "#FFFFFF"
  },
  btn: {
    backgroundColor: Colors.accent,
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 4
  },
  btnText: {
    color: "#FFFFFF",
    fontWeight: "700",
    fontSize: 14
  },
  resultHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 8
  },
  resultHeaderTitle: {
    fontSize: 15,
    fontWeight: "800",
    color: "#1E293B"
  },
  resultHeaderSub: {
    fontSize: 12,
    color: "#64748B"
  },
  list: {
    paddingHorizontal: 14,
    paddingBottom: 24
  },
  loadingBox: {
    padding: 30,
    alignItems: "center"
  },
  loadingText: {
    marginTop: 10,
    fontSize: 13,
    color: "#64748B"
  },
  emptyBox: {
    padding: 36,
    alignItems: "center"
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#1E293B",
    marginBottom: 6
  },
  emptyText: {
    fontSize: 13,
    color: "#64748B",
    textAlign: "center",
    lineHeight: 18
  }
});
