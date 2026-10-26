import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  ScrollView,
  Image,
  TouchableOpacity,
  Modal,
  StyleSheet,
  Alert,
  TextInput,
  ActivityIndicator
} from "react-native";
import { Colors } from "../theme/colors";
import StarRating from "../components/StarRating";
import {
  markRecipeEaten,
  submitReview,
  toggleFavorite,
  fetchFavorites,
  addRecipeIngredientsToGrocery,
  resolveRecipeImageUrl
} from "../services/api";

const AUTHENTIC_FOOD_FALLBACK = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&auto=format&fit=crop&q=80";

const SERVING_OPTIONS = [0.5, 1.0, 1.5, 2.0, 3.0];

export default function RecipeDetailModal({ visible, recipe, onClose, userId = null }) {
  const [servingSize, setServingSize] = useState(1.0);
  const [isFav, setIsFav] = useState(false);
  const [togglingFav, setTogglingFav] = useState(false);
  const [addingGrocery, setAddingGrocery] = useState(false);
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [showReviewInput, setShowReviewInput] = useState(false);
  const [eaten, setEaten] = useState(false);
  const [loggingEaten, setLoggingEaten] = useState(false);
  const [imgError, setImgError] = useState(false);

  useEffect(() => {
    if (visible && recipe) {
      setServingSize(1.0);
      setEaten(false);
      setShowReviewInput(false);
      setImgError(false);
      checkFavoriteStatus();
    }
  }, [visible, recipe]);

  const checkFavoriteStatus = async () => {
    if (!userId || !recipe?.recipe_id) return;
    try {
      const res = await fetchFavorites(userId);
      if (res.success && Array.isArray(res.favorites)) {
        setIsFav(res.favorites.includes(Number(recipe.recipe_id)) || res.favorites.includes(String(recipe.recipe_id)));
      }
    } catch (e) {
      // Quiet fallback
    }
  };

  const handleToggleFavorite = async () => {
    if (!recipe?.recipe_id) return;
    setTogglingFav(true);
    try {
      const res = await toggleFavorite(userId, recipe.recipe_id);
      if (res && res.success) {
        setIsFav(res.is_favorite);
        Alert.alert("Favorite", res.message || (res.is_favorite ? "Added to favorites ⭐" : "Removed from favorites"));
      }
    } catch (e) {
      Alert.alert("Notice", "Could not update favorite status.");
    }
    setTogglingFav(false);
  };

  const handleAddGrocery = async () => {
    if (!recipe) return;
    setAddingGrocery(true);
    try {
      const res = await addRecipeIngredientsToGrocery(recipe, userId);
      if (res && res.success) {
        Alert.alert("Grocery List Updated! 🛒", `Added ${res.added !== undefined ? res.added : (recipe.ingredients?.length || 0)} ingredients directly to your Smart Grocery List.`);
      } else {
        Alert.alert("Notice", res?.message || "Failed to add ingredients to grocery list.");
      }
    } catch (e) {
      Alert.alert("Notice", "Could not add ingredients to grocery list at this time.");
    } finally {
      setAddingGrocery(false);
    }
  };

  const handleMarkEaten = async () => {
    if (!recipe?.recipe_id) return;
    setLoggingEaten(true);
    const res = await markRecipeEaten(userId, recipe.recipe_id, servingSize);
    setLoggingEaten(false);
    if (res.success) {
      setEaten(true);
      setShowReviewInput(true);
      Alert.alert("Logged! 🎉", `Marked ${servingSize}x serving (${scaledCalories} kcal) as cooked & eaten! Please leave a star review.`);
    } else {
      Alert.alert("Notice", res.message || "Failed to log recipe.");
    }
  };

  const handleReviewSubmit = async () => {
    if (!recipe?.recipe_id) return;
    const res = await submitReview(userId, recipe.recipe_id, rating, comment);
    if (res.success) {
      Alert.alert("Thank you! ⭐", "Your rating and feedback have been saved.");
      setShowReviewInput(false);
    } else {
      Alert.alert("Notice", res.message || "Failed to save review.");
    }
  };

  if (!visible || !recipe) return null;

  const nutr = recipe?.nutritions || {};
  const ingredients = Array.isArray(recipe?.ingredients) ? recipe.ingredients : [];
  const steps = Array.isArray(recipe?.steps) ? recipe.steps : [];

  // Scaled nutrition based on chosen serving size
  const scaledCalories = Math.round((nutr.calories || 0) * servingSize);
  const scaledProtein = Math.round((nutr.protein_g || 0) * servingSize);
  const scaledCarbs = Math.round((nutr.carbs_g || 0) * servingSize);
  const scaledFat = Math.round((nutr.fat_g || 0) * servingSize);

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={onClose}>
      <View style={styles.modalContainer}>
        {/* Top Navbar */}
        <View style={styles.topBar}>
          <TouchableOpacity style={styles.favTopBtn} onPress={handleToggleFavorite} disabled={togglingFav}>
            <Text style={styles.favIconText}>{isFav ? "⭐ Favorited" : "☆ Add Favorite"}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.closeBtn} onPress={onClose}>
            <Text style={styles.closeText}>✕ Close</Text>
          </TouchableOpacity>
        </View>

        <ScrollView contentContainerStyle={styles.scrollContent}>
          <Image
            source={{ uri: imgError ? AUTHENTIC_FOOD_FALLBACK : resolveRecipeImageUrl(recipe.image_link) }}
            style={styles.heroImage}
            onError={() => setImgError(true)}
          />

          <View style={styles.body}>
            <Text style={styles.title}>{recipe.recipe_name}</Text>

            {/* Metadata Tags / Badges */}
            <View style={styles.badgeRow}>
              {Boolean(recipe.cuisine) ? (
                <View style={[styles.badge, styles.badgeCuisine]}>
                  <Text style={styles.badgeText}>🏛️ {recipe.cuisine}</Text>
                </View>
              ) : null}
              {Boolean(recipe.meal_type) ? (
                <View style={[styles.badge, styles.badgeMeal]}>
                  <Text style={styles.badgeText}>🍽️ {recipe.meal_type}</Text>
                </View>
              ) : null}
              {Boolean(recipe.diet) ? (
                <View style={[styles.badge, recipe.diet === "Vegetarian" ? styles.badgeVeg : styles.badgeNonVeg]}>
                  <Text style={styles.badgeText}>{recipe.diet === "Vegetarian" ? "🌱 Veg" : "🍗 Non-Veg"}</Text>
                </View>
              ) : null}
              {Boolean(recipe.cook_time_mins) ? (
                <View style={[styles.badge, styles.badgeTime]}>
                  <Text style={styles.badgeText}>⏱️ {recipe.cook_time_mins}m</Text>
                </View>
              ) : null}
              {Boolean(recipe.health_score) ? (
                <View style={[styles.badge, styles.badgeHealth]}>
                  <Text style={styles.badgeText}>❤️ Health: {recipe.health_score}/100</Text>
                </View>
              ) : null}
            </View>

            {/* Serving Size Selector */}
            <View style={styles.servingContainer}>
              <Text style={styles.servingLabel}>Serving Size:</Text>
              <View style={styles.servingPillsRow}>
                {SERVING_OPTIONS.map((opt) => (
                  <TouchableOpacity
                    key={opt}
                    style={[styles.servingPill, servingSize === opt && styles.servingPillActive]}
                    onPress={() => setServingSize(opt)}
                  >
                    <Text style={[styles.servingPillText, servingSize === opt && styles.servingPillTextActive]}>
                      {opt}x
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {/* Dynamic Nutrition Grid */}
            <View style={styles.nutritionRow}>
              <View style={styles.nutrItem}>
                <Text style={styles.nutrValue}>{scaledCalories}</Text>
                <Text style={styles.nutrLabel}>Calories</Text>
              </View>
              <View style={styles.nutrItem}>
                <Text style={styles.nutrValue}>{scaledProtein}g</Text>
                <Text style={styles.nutrLabel}>Protein</Text>
              </View>
              <View style={styles.nutrItem}>
                <Text style={styles.nutrValue}>{scaledCarbs}g</Text>
                <Text style={styles.nutrLabel}>Carbs</Text>
              </View>
              <View style={styles.nutrItem}>
                <Text style={styles.nutrValue}>{scaledFat}g</Text>
                <Text style={styles.nutrLabel}>Fat</Text>
              </View>
            </View>

            {/* Action Buttons: Log Eaten & Add to Grocery */}
            <View style={styles.actionButtonsRow}>
              <TouchableOpacity
                style={[styles.eatenBtn, eaten && styles.eatenBtnSuccess]}
                onPress={handleMarkEaten}
                disabled={eaten || loggingEaten}
              >
                {loggingEaten ? (
                  <ActivityIndicator color="#FFFFFF" size="small" />
                ) : (
                  <Text style={styles.eatenBtnText}>
                    {eaten ? "✓ Logged as Eaten" : "🍽️ Mark as Cooked / Eaten"}
                  </Text>
                )}
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.groceryBtn}
                onPress={handleAddGrocery}
                disabled={addingGrocery}
              >
                {addingGrocery ? (
                  <ActivityIndicator color="#7B2C3F" size="small" />
                ) : (
                  <Text style={styles.groceryBtnText}>🛒 Add to Grocery</Text>
                )}
              </TouchableOpacity>
            </View>

            {/* Review Section */}
            {showReviewInput && (
              <View style={styles.reviewBox}>
                <Text style={styles.reviewTitle}>Rate This Recipe</Text>
                <StarRating rating={rating} onRate={setRating} />
                <TextInput
                  style={styles.commentInput}
                  placeholder="Add a comment or tips for next time..."
                  placeholderTextColor="#94A3B8"
                  value={comment}
                  onChangeText={setComment}
                />
                <TouchableOpacity style={styles.submitReviewBtn} onPress={handleReviewSubmit}>
                  <Text style={styles.submitReviewText}>Submit Review</Text>
                </TouchableOpacity>
              </View>
            )}

            {/* Ingredients Section */}
            <Text style={styles.sectionHeader}>🛒 Ingredients ({ingredients.length})</Text>
            {ingredients.map((ing, idx) => (
              <View key={idx} style={styles.ingRow}>
                <Text style={styles.ingBullet}>•</Text>
                <Text style={styles.ingText}>{ing}</Text>
              </View>
            ))}

            {/* Preparation Steps Section */}
            <Text style={styles.sectionHeader}>👨‍🍳 Preparation Steps ({steps.length})</Text>
            {steps.map((step, idx) => (
              <View key={idx} style={styles.stepCard}>
                <View style={styles.stepBadge}>
                  <Text style={styles.stepBadgeText}>{idx + 1}</Text>
                </View>
                <Text style={styles.stepText}>{step}</Text>
              </View>
            ))}
          </View>
        </ScrollView>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  modalContainer: {
    flex: 1,
    backgroundColor: "#F8FAFC"
  },
  topBar: {
    paddingHorizontal: 16,
    paddingTop: 48,
    paddingBottom: 12,
    backgroundColor: "#FFFFFF",
    borderBottomWidth: 1,
    borderBottomColor: "#E2E8F0",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center"
  },
  favTopBtn: {
    backgroundColor: "#FEF3C7",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#FDE68A"
  },
  favIconText: {
    fontSize: 13,
    fontWeight: "700",
    color: "#B45309"
  },
  closeBtn: {
    padding: 6
  },
  closeText: {
    fontSize: 15,
    fontWeight: "bold",
    color: "#64748B"
  },
  scrollContent: {
    paddingBottom: 30
  },
  heroImage: {
    width: "100%",
    height: 230
  },
  body: {
    padding: 18
  },
  title: {
    fontSize: 22,
    fontWeight: "800",
    color: "#0F172A",
    marginBottom: 10
  },
  badgeRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
    marginBottom: 14
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12
  },
  badgeCuisine: {
    backgroundColor: "rgba(123, 44, 63, 0.1)"
  },
  badgeMeal: {
    backgroundColor: "#EFF6FF"
  },
  badgeVeg: {
    backgroundColor: "#DCFCE7"
  },
  badgeNonVeg: {
    backgroundColor: "#FEE2E2"
  },
  badgeTime: {
    backgroundColor: "#FEF3C7"
  },
  badgeHealth: {
    backgroundColor: "#E0E7FF"
  },
  badgeText: {
    fontSize: 11,
    fontWeight: "700",
    color: "#1E293B"
  },
  servingContainer: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: "#FFFFFF",
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    marginBottom: 14
  },
  servingLabel: {
    fontSize: 13,
    fontWeight: "700",
    color: "#334155"
  },
  servingPillsRow: {
    flexDirection: "row",
    gap: 6
  },
  servingPill: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 8,
    backgroundColor: "#F1F5F9"
  },
  servingPillActive: {
    backgroundColor: "#7B2C3F"
  },
  servingPillText: {
    fontSize: 12,
    fontWeight: "700",
    color: "#475569"
  },
  servingPillTextActive: {
    color: "#FFFFFF"
  },
  nutritionRow: {
    flexDirection: "row",
    backgroundColor: "#FFFFFF",
    borderRadius: 14,
    padding: 14,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    justifyContent: "space-around"
  },
  nutrItem: {
    alignItems: "center"
  },
  nutrValue: {
    fontSize: 17,
    fontWeight: "800",
    color: "#7B2C3F"
  },
  nutrLabel: {
    fontSize: 11,
    color: "#64748B",
    marginTop: 2
  },
  actionButtonsRow: {
    flexDirection: "row",
    gap: 10,
    marginBottom: 16
  },
  eatenBtn: {
    flex: 1.2,
    backgroundColor: "#FF9E1F",
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center"
  },
  eatenBtnSuccess: {
    backgroundColor: "#10B981"
  },
  eatenBtnText: {
    color: "#0F172A",
    fontSize: 14,
    fontWeight: "700"
  },
  groceryBtn: {
    flex: 1,
    backgroundColor: "#FFFFFF",
    borderWidth: 1.5,
    borderColor: "#7B2C3F",
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center"
  },
  groceryBtnText: {
    color: "#7B2C3F",
    fontSize: 13,
    fontWeight: "700"
  },
  reviewBox: {
    backgroundColor: "#FFFFFF",
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: "#E2E8F0"
  },
  reviewTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: "#0F172A",
    marginBottom: 6
  },
  commentInput: {
    backgroundColor: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#E2E8F0",
    borderRadius: 8,
    padding: 10,
    fontSize: 13,
    color: "#0F172A",
    marginVertical: 10
  },
  submitReviewBtn: {
    backgroundColor: "#7B2C3F",
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: "center"
  },
  submitReviewText: {
    color: "#FFFFFF",
    fontWeight: "700",
    fontSize: 13
  },
  sectionHeader: {
    fontSize: 16,
    fontWeight: "700",
    color: "#0F172A",
    marginTop: 14,
    marginBottom: 10
  },
  ingRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: "#F1F5F9"
  },
  ingBullet: {
    fontSize: 18,
    color: "#7B2C3F",
    marginRight: 10
  },
  ingText: {
    fontSize: 13,
    color: "#334155",
    flex: 1
  },
  stepCard: {
    flexDirection: "row",
    backgroundColor: "#FFFFFF",
    padding: 12,
    borderRadius: 10,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "#E2E8F0"
  },
  stepBadge: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: "#7B2C3F",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 10
  },
  stepBadgeText: {
    color: "#FFFFFF",
    fontWeight: "bold",
    fontSize: 12
  },
  stepText: {
    fontSize: 13,
    color: "#334155",
    lineHeight: 18,
    flex: 1
  }
});
