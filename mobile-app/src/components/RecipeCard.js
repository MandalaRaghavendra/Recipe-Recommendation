import React, { useState } from "react";
import { View, Text, Image, TouchableOpacity, StyleSheet } from "react-native";
import { Colors } from "../theme/colors";
import { resolveRecipeImageUrl } from "../services/api";

const AUTHENTIC_FOOD_FALLBACK = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&auto=format&fit=crop&q=80";

export default function RecipeCard({ recipe, onPress }) {
  const [imgError, setImgError] = useState(false);

  if (!recipe) return null;

  const isVeg = (recipe.veg_nonveg || "").toLowerCase() === "veg";
  const calories = recipe.nutritions?.calories || 300;
  const healthScore = recipe.health_score || 85;
  const totalTimeMins = (recipe.prep_time_mins || 15) + (recipe.cook_time_mins || 20);
  const imageUri = imgError ? AUTHENTIC_FOOD_FALLBACK : resolveRecipeImageUrl(recipe.image_link);

  return (
    <TouchableOpacity activeOpacity={0.85} style={styles.card} onPress={() => onPress && onPress(recipe)}>
      <Image
        source={{ uri: imageUri }}
        style={styles.image}
        resizeMode="cover"
        onError={() => setImgError(true)}
      />
      <View style={styles.content}>
        <View style={styles.topRow}>
          <View style={{ flexDirection: "row", gap: 6, alignItems: "center" }}>
            <View style={[styles.badge, { backgroundColor: isVeg ? "#E8F5E9" : "#FFEBEE" }]}>
              <Text style={[styles.badgeText, { color: isVeg ? Colors.veg : Colors.nonVeg }]}>
                {isVeg ? "🌱 Veg" : "🍗 Non-Veg"}
              </Text>
            </View>
            {Boolean(recipe.match_score_pct) ? (
              <View style={[styles.badge, { backgroundColor: "#DCFCE7" }]}>
                <Text style={[styles.badgeText, { color: "#166534" }]}>✨ {recipe.match_score_pct}% Match</Text>
              </View>
            ) : null}
          </View>
          <View style={styles.healthBadge}>
            <Text style={styles.healthText}>⭐ {healthScore}/100</Text>
          </View>
        </View>

        <Text style={styles.title} numberOfLines={2}>{recipe.recipe_name}</Text>

        {Boolean(recipe.recommendation_reason) ? (
          <View style={styles.aiReasonBox}>
            <Text style={styles.aiReasonText} numberOfLines={2}>💡 {recipe.recommendation_reason}</Text>
          </View>
        ) : null}

        <View style={styles.metaRow}>
          <Text style={styles.metaText}>🔥 {Math.round(calories)} kcal</Text>
          <Text style={styles.metaText}>⏱️ {totalTimeMins} mins</Text>
          <Text style={styles.metaText}>🥩 {Math.round(recipe.nutritions?.protein_g || 15)}g Protein</Text>
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.cardBg,
    borderRadius: 16,
    marginBottom: 16,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: Colors.border,
    elevation: 2,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 6
  },
  image: {
    width: "100%",
    height: 160
  },
  content: {
    padding: 14
  },
  topRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8
  },
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6
  },
  badgeText: {
    fontSize: 12,
    fontWeight: "700"
  },
  healthBadge: {
    backgroundColor: "#FEF3C7",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6
  },
  healthText: {
    color: "#92400E",
    fontSize: 12,
    fontWeight: "700"
  },
  title: {
    fontSize: 16,
    fontWeight: "700",
    color: Colors.textDark,
    marginBottom: 6
  },
  aiReasonBox: {
    backgroundColor: "#F8FAFC",
    paddingHorizontal: 8,
    paddingVertical: 5,
    borderRadius: 8,
    marginBottom: 8,
    borderLeftWidth: 3,
    borderLeftColor: Colors.accent
  },
  aiReasonText: {
    fontSize: 11,
    color: Colors.textDark,
    fontWeight: "500",
    lineHeight: 15
  },
  metaRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: "#F1F5F9"
  },
  metaText: {
    fontSize: 12,
    color: Colors.textMuted,
    fontWeight: "500"
  }
});
