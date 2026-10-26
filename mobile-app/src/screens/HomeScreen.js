import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  TextInput,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
  RefreshControl
} from "react-native";
import { Colors } from "../theme/colors";
import RecipeCard from "../components/RecipeCard";
import {
  fetchRecipes,
  fetchFilteredRecipes,
  fetchFavorites
} from "../services/api";

const CUISINES = [
  "All", "Andhra", "Telangana", "South Indian", "North Indian", "Punjabi",
  "Gujarati", "Bengali", "Maharashtrian", "Kerala", "Karnataka", "Tamil Nadu"
];

const MEAL_TYPES = ["All", "Breakfast", "Lunch", "Dinner", "Snack", "Dessert"];

const DIET_FILTERS = [
  { id: "all", label: "🌟 All" },
  { id: "Vegetarian", label: "🌱 Veg" },
  { id: "Non-Vegetarian", label: "🍗 Non-Veg" },
  { id: "High Protein", label: "💪 High Protein" },
  { id: "Low Calorie", label: "🔥 Low Cal" },
  { id: "High Fiber", label: "🌾 High Fiber" },
  { id: "Muscle Gain", label: "🥩 Muscle Gain" },
  { id: "Weight Loss", label: "⚖️ Weight Loss" },
  { id: "favorites", label: "⭐ Favorites" }
];

export default function HomeScreen({ onSelectRecipe, currentUser = null, onOpenAuth = null }) {
  const [selectedCuisine, setSelectedCuisine] = useState("All");
  const [selectedMealType, setSelectedMealType] = useState("All");
  const [selectedDiet, setSelectedDiet] = useState("all");
  const [search, setSearch] = useState("");
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const userId = currentUser?.objectId || currentUser?.id || null;

  useEffect(() => {
    const timer = setTimeout(() => {
      loadRecipes();
    }, 350);
    return () => clearTimeout(timer);
  }, [search, selectedCuisine, selectedMealType, selectedDiet]);

  const loadRecipes = async (queryOverride = null) => {
    setLoading(true);
    const activeSearch = queryOverride !== null ? queryOverride : search;
    try {
      if (selectedDiet === "favorites") {
        const favRes = await fetchFavorites(userId);
        setRecipes(favRes.recipes || []);
      } else {
        const isDiet = selectedDiet === "Vegetarian" || selectedDiet === "Non-Vegetarian";
        const isNutr = ["High Protein", "Low Calorie", "High Fiber", "Muscle Gain", "Weight Loss"].includes(selectedDiet);
        const res = await fetchFilteredRecipes({
          cuisine: selectedCuisine,
          meal_type: selectedMealType,
          diet: isDiet ? selectedDiet : "all",
          nutrition_tag: isNutr ? selectedDiet : "all",
          query: activeSearch.trim()
        });
        setRecipes(res.recipes || []);
      }
    } catch (e) {
      const data = await fetchRecipes("all", activeSearch);
      setRecipes(data || []);
    }
    setLoading(false);
    setRefreshing(false);
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadRecipes();
  };

  const handleSearchSubmit = () => {
    loadRecipes();
  };

  const resetAllFilters = () => {
    setSelectedCuisine("All");
    setSelectedMealType("All");
    setSelectedDiet("all");
    setSearch("");
    loadRecipes("");
  };


  return (
    <View style={styles.container}>
      {/* Top Header & Account Switcher */}
      <View style={styles.header}>
        <View style={styles.brandRow}>
          <View>
            <Text style={styles.brandTitle}>🍲 Tastio</Text>
            <Text style={styles.subTitle}>AI Recipe Recommendation & Nutrition Monorepo</Text>
          </View>
          <TouchableOpacity
            style={styles.authBadge}
            onPress={onOpenAuth}
            activeOpacity={0.7}
          >
            <Text style={styles.authBadgeText}>
              {currentUser ? `👤 ${currentUser.name || "User"}` : "🔑 Sign In"}
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      <FlatList
        ListHeaderComponent={
          <>
            {/* Search Input Bar */}
            <View style={styles.searchSection}>
              <View style={styles.searchBox}>
                <TouchableOpacity onPress={() => loadRecipes()} activeOpacity={0.7} style={{ paddingRight: 6 }}>
                  <Text style={styles.searchIcon}>🔍</Text>
                </TouchableOpacity>
                <TextInput
                  style={styles.searchInput}
                  placeholder="Search recipes, chicken, biryani, paneer..."
                  placeholderTextColor="#94A3B8"
                  value={search}
                  onChangeText={setSearch}
                  onSubmitEditing={handleSearchSubmit}
                  returnKeyType="search"
                />
                {search.length > 0 && (
                  <TouchableOpacity onPress={() => { setSearch(""); loadRecipes(""); }}>
                    <Text style={styles.clearSearch}>✕</Text>
                  </TouchableOpacity>
                )}
              </View>
            </View>

            {/* Multi-facet Filter Toolbar */}
            <View style={styles.filterSection}>
              <View style={styles.filterHeaderRow}>
                <Text style={styles.filterSectionTitle}>🎛️ Explore by Cuisine & Diet</Text>
                <TouchableOpacity onPress={resetAllFilters}>
                  <Text style={styles.resetFilterText}>↺ Reset</Text>
                </TouchableOpacity>
              </View>

              {/* 1. Diet & Macro Pills */}
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterRow}>
                {DIET_FILTERS.map((d) => (
                  <TouchableOpacity
                    key={d.id}
                    style={[styles.filterChip, selectedDiet === d.id && styles.filterChipActivePrimary]}
                    onPress={() => setSelectedDiet(d.id)}
                  >
                    <Text style={[styles.filterChipText, selectedDiet === d.id && styles.filterChipTextActive]}>
                      {d.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>

              {/* 2. Indian Regional Cuisines Row */}
              <Text style={styles.filterSubLabel}>REGIONAL INDIAN CUISINES</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterRow}>
                {CUISINES.map((c) => (
                  <TouchableOpacity
                    key={c}
                    style={[styles.filterChip, selectedCuisine === c && styles.filterChipActive]}
                    onPress={() => setSelectedCuisine(c)}
                  >
                    <Text style={[styles.filterChipText, selectedCuisine === c && styles.filterChipTextActive]}>
                      {c}
                    </Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>

              {/* 3. Meal Types Row */}
              <Text style={styles.filterSubLabel}>MEAL OCCASION</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterRow}>
                {MEAL_TYPES.map((m) => (
                  <TouchableOpacity
                    key={m}
                    style={[styles.filterChip, selectedMealType === m && styles.filterChipActiveAccent]}
                    onPress={() => setSelectedMealType(m)}
                  >
                    <Text style={[styles.filterChipText, selectedMealType === m && styles.filterChipTextActive]}>
                      {m}
                    </Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            </View>
          </>
        }
        data={recipes}
        keyExtractor={(item, index) => String(item.recipe_id || index)}
        renderItem={({ item }) => <RecipeCard recipe={item} onPress={onSelectRecipe} />}
        initialNumToRender={6}
        maxToRenderPerBatch={8}
        windowSize={5}
        removeClippedSubviews={true}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={["#7B2C3F"]} />
        }
        ListEmptyComponent={
          loading ? (
            <View style={styles.loadingBox}>
              <ActivityIndicator size="large" color="#7B2C3F" />
              <Text style={styles.loadingText}>Fetching personalized recipes...</Text>
            </View>
          ) : (
            <View style={styles.emptyBox}>
              <Text style={styles.emptyTitle}>No Recipes Found</Text>
              <Text style={styles.emptyText}>Try changing cuisine filters or your search query.</Text>
            </View>
          )
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F8FAFC"
  },
  header: {
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 10,
    backgroundColor: "#FFFFFF",
    borderBottomWidth: 1,
    borderBottomColor: "#E2E8F0"
  },
  brandRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center"
  },
  brandTitle: {
    fontSize: 22,
    fontWeight: "900",
    color: "#7B2C3F"
  },
  subTitle: {
    fontSize: 11,
    color: "#64748B",
    marginTop: 1
  },
  authBadge: {
    backgroundColor: "#FEF3C7",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#FDE68A"
  },
  authBadgeText: {
    fontSize: 12,
    fontWeight: "700",
    color: "#92400E"
  },
  searchSection: {
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 6
  },
  searchBox: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#FFFFFF",
    borderRadius: 14,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: "#CBD5E1",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1
  },
  searchIcon: {
    fontSize: 16,
    marginRight: 8
  },
  searchInput: {
    flex: 1,
    fontSize: 14,
    color: "#0F172A",
    padding: 0
  },
  clearSearch: {
    fontSize: 14,
    color: "#94A3B8",
    paddingHorizontal: 6
  },
  filterSection: {
    backgroundColor: "#FFFFFF",
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#E2E8F0",
    marginBottom: 10
  },
  filterHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8
  },
  filterSectionTitle: {
    fontSize: 13,
    fontWeight: "800",
    color: "#0F172A"
  },
  resetFilterText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#64748B"
  },
  filterSubLabel: {
    fontSize: 9,
    fontWeight: "800",
    color: "#94A3B8",
    letterSpacing: 0.5,
    marginTop: 8,
    marginBottom: 4
  },
  filterRow: {
    marginBottom: 4
  },
  filterChip: {
    backgroundColor: "#F1F5F9",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 14,
    marginRight: 6
  },
  filterChipActive: {
    backgroundColor: "#7B2C3F"
  },
  filterChipActivePrimary: {
    backgroundColor: "#D97706"
  },
  filterChipActiveAccent: {
    backgroundColor: "#2563EB"
  },
  filterChipText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#475569"
  },
  filterChipTextActive: {
    color: "#FFFFFF",
    fontWeight: "700"
  },
  listContent: {
    paddingBottom: 24
  },
  loadingBox: {
    padding: 40,
    alignItems: "center"
  },
  loadingText: {
    marginTop: 10,
    color: "#64748B",
    fontSize: 13
  },
  emptyBox: {
    padding: 40,
    alignItems: "center"
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#0F172A",
    marginBottom: 4
  },
  emptyText: {
    fontSize: 13,
    color: "#64748B",
    textAlign: "center"
  }
});
