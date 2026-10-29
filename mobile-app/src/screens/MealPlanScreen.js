import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  FlatList,
  Image,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
  Alert,
  Modal,
  RefreshControl
} from "react-native";
import { Colors } from "../theme/colors";
import {
  generateDefaultLocalMealPlan,
  fetchCurrentMealPlan,
  generateMealPlan,
  replaceMealInPlan,
  fetchMealAlternatives,
  markRecipeEaten,
  resolveRecipeImageUrl
} from "../services/api";

const SLOT_CONFIG = [
  { key: "breakfast", label: "Breakfast", icon: "🍳", color: "#D97706" },
  { key: "lunch", label: "Lunch", icon: "🥘", color: "#2563EB" },
  { key: "snack", label: "Snack", icon: "🥪", color: "#059669" },
  { key: "dinner", label: "Dinner", icon: "🍲", color: "#7C3AED" }
];

export default function MealPlanScreen({ onSelectRecipe, userId = null, isActive = false }) {
  const [mealPlan, setMealPlan] = useState(() => generateDefaultLocalMealPlan());
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [activeDayIndex, setActiveDayIndex] = useState(1);

  // Swap Modal State
  const [swapModalVisible, setSwapModalVisible] = useState(false);
  const [swapSlot, setSwapSlot] = useState("lunch");
  const [alternatives, setAlternatives] = useState([]);
  const [loadingAlts, setLoadingAlts] = useState(false);

  useEffect(() => {
    if (isActive || !mealPlan) {
      loadPlan();
    }
  }, [userId, isActive]);

  const loadPlan = async (isManualRefresh = false) => {
    if (isManualRefresh) setRefreshing(true);
    try {
      const res = await fetchCurrentMealPlan(userId);
      if (res && res.success && res.meal_plan) {
        setMealPlan(res.meal_plan);
      }
    } catch (e) {
      // Keep existing instant meal plan
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    loadPlan(true);
  };

  const handleRegenerate = async () => {
    setRegenerating(true);
    const res = await generateMealPlan(userId);
    setRegenerating(false);
    if (res.success && res.meal_plan) {
      setMealPlan(res.meal_plan);
      setActiveDayIndex(1);
      Alert.alert("Plan Generated", "✅ Fresh 7-Day AI Meal Plan generated successfully!");
    } else {
      Alert.alert("Error", "Failed to generate plan. Please try again.");
    }
  };

  const handleOpenSwapModal = async (slotKey, currentRecipeId) => {
    setSwapSlot(slotKey);
    setSwapModalVisible(true);
    setLoadingAlts(true);
    const res = await fetchMealAlternatives(slotKey, currentRecipeId, userId);
    if (res.success && res.alternatives) {
      setAlternatives(res.alternatives);
    } else {
      setAlternatives([]);
    }
    setLoadingAlts(false);
  };

  const handleExecuteSwap = async (newRecipeId) => {
    const res = await replaceMealInPlan(userId, activeDayIndex, swapSlot, newRecipeId);
    if (res.success && res.meal_plan) {
      setMealPlan(res.meal_plan);
      setSwapModalVisible(false);
      Alert.alert("Meal Swapped", "✅ Meal updated successfully in your active plan!");
    } else {
      Alert.alert("Error", res.message || "Failed to swap meal.");
    }
  };

  const handleLogMeal = async (recipe) => {
    try {
      await markRecipeEaten(userId, recipe.recipe_id, 1.0);
      Alert.alert("Logged to History", `✅ "${recipe.recipe_name}" marked as eaten!`);
    } catch (e) {
      Alert.alert("Logged", `Logged "${recipe.recipe_name}"!`);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={Colors.primary} />
        <Text style={styles.loadingText}>Loading your 7-Day AI Meal Plan...</Text>
      </View>
    );
  }

  const activeDay = (mealPlan?.days || []).find((d) => d.day_index === activeDayIndex) || mealPlan?.days?.[0];

  return (
    <View style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={["#7B2C3F"]} />
        }
      >
        {/* Plan Header Banner */}
        <View style={styles.headerCard}>
          <View style={styles.headerTopRow}>
            <View>
              <Text style={styles.planTitle}>{mealPlan?.plan_name || "7-Day AI Meal Plan"}</Text>
              <View style={styles.badgeRow}>
                <View style={styles.goalBadge}>
                  <Text style={styles.goalBadgeText}>
                    {mealPlan?.diet_goal ? mealPlan.diet_goal.replace("_", " ").toUpperCase() : "WEIGHT LOSS"}
                  </Text>
                </View>
                <View style={[styles.goalBadge, { backgroundColor: "rgba(255,255,255,0.2)" }]}>
                  <Text style={[styles.goalBadgeText, { color: "#FFFFFF" }]}>
                    {mealPlan?.food_pref ? mealPlan.food_pref.toUpperCase() : "BOTH"}
                  </Text>
                </View>
              </View>
            </View>

            <TouchableOpacity
              style={styles.btnRegenerate}
              onPress={handleRegenerate}
              disabled={regenerating}
            >
              {regenerating ? (
                <ActivityIndicator size="small" color="#FFFFFF" />
              ) : (
                <Text style={styles.btnRegenerateText}>🔄 New Plan</Text>
              )}
            </TouchableOpacity>
          </View>

          {/* Macro Targets Strip */}
          <View style={styles.macroStrip}>
            <View style={styles.macroCol}>
              <Text style={styles.macroVal}>{mealPlan?.target_calories || 1800}</Text>
              <Text style={styles.macroLbl}>kcal Target</Text>
            </View>
            <View style={styles.macroCol}>
              <Text style={styles.macroVal}>{mealPlan?.target_protein || 100}g</Text>
              <Text style={styles.macroLbl}>Protein</Text>
            </View>
            <View style={styles.macroCol}>
              <Text style={styles.macroVal}>{mealPlan?.target_carbs || 200}g</Text>
              <Text style={styles.macroLbl}>Carbs</Text>
            </View>
            <View style={styles.macroCol}>
              <Text style={styles.macroVal}>{mealPlan?.target_fat || 50}g</Text>
              <Text style={styles.macroLbl}>Fat</Text>
            </View>
          </View>
        </View>

        {/* 7-Day Horizontal Tabs */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.daysTabScroll}
        >
          {(mealPlan?.days || []).map((d) => {
            const isActive = d.day_index === activeDayIndex;
            return (
              <TouchableOpacity
                key={`day-${d.day_index}`}
                style={[styles.dayTab, isActive && styles.dayTabActive]}
                onPress={() => setActiveDayIndex(d.day_index)}
              >
                <Text style={[styles.dayTabTitle, isActive && styles.dayTabTitleActive]}>
                  Day {d.day_index}
                </Text>
                <Text style={[styles.dayTabSub, isActive && styles.dayTabSubActive]}>
                  {d.day_name.substring(0, 3)}
                </Text>
                <View style={[styles.diffPill, isActive && styles.diffPillActive]}>
                  <Text style={[styles.diffPillText, isActive && styles.diffPillTextActive]}>
                    {d.difference_str}
                  </Text>
                </View>
              </TouchableOpacity>
            );
          })}
        </ScrollView>

        {/* Active Day Summary Box */}
        {activeDay && (
          <View style={styles.daySummaryBox}>
            <View style={styles.daySummaryHeader}>
              <Text style={styles.daySummaryTitle}>Day {activeDay.day_index} ({activeDay.day_name})</Text>
              <Text style={styles.daySummaryDiff}>{activeDay.difference_str} vs Target</Text>
            </View>

            <View style={styles.summaryStatsRow}>
              <View style={styles.statPill}>
                <Text style={styles.statVal}>{activeDay.total_calories} kcal</Text>
                <Text style={styles.statLbl}>Calories</Text>
              </View>
              <View style={styles.statPill}>
                <Text style={styles.statVal}>{activeDay.total_protein}g</Text>
                <Text style={styles.statLbl}>Protein</Text>
              </View>
              <View style={styles.statPill}>
                <Text style={styles.statVal}>{activeDay.total_carbs}g</Text>
                <Text style={styles.statLbl}>Carbs</Text>
              </View>
              <View style={styles.statPill}>
                <Text style={styles.statVal}>{activeDay.total_fat}g</Text>
                <Text style={styles.statLbl}>Fat</Text>
              </View>
            </View>
          </View>
        )}

        {/* 4 Meal Slots */}
        {activeDay && (
          <View style={styles.mealsContainer}>
            {SLOT_CONFIG.map((slot) => {
              const meal = activeDay.meals?.[slot.key];
              if (!meal) return null;
              const isVeg = (meal.veg_nonveg || "Veg").toLowerCase() === "veg";

              return (
                <View key={slot.key} style={styles.mealCard}>
                  {/* Slot Header */}
                  <View style={styles.slotHeader}>
                    <Text style={[styles.slotTitle, { color: slot.color }]}>
                      {slot.icon} {slot.label.toUpperCase()}
                    </Text>
                    <View style={[styles.vegBadge, { backgroundColor: isVeg ? "#E8F5E9" : "#FFEBEE" }]}>
                      <Text style={[styles.vegBadgeText, { color: isVeg ? Colors.veg : Colors.nonVeg }]}>
                        {isVeg ? "🌱 Veg" : "🍗 Non-Veg"}
                      </Text>
                    </View>
                  </View>

                  {/* Meal Image */}
                  <Image
                    source={{ uri: resolveRecipeImageUrl(meal.image_link) }}
                    style={styles.mealImage}
                    resizeMode="cover"
                  />

                  {/* Meal Body */}
                  <View style={styles.mealBody}>
                    <Text style={styles.recipeName}>{meal.recipe_name}</Text>

                    {/* Macro Badges */}
                    <View style={styles.macroBadgesRow}>
                      <View style={[styles.mBadge, { backgroundColor: "#FEF3C7" }]}>
                        <Text style={[styles.mBadgeText, { color: "#92400E" }]}>🔥 {meal.calories} kcal</Text>
                      </View>
                      <View style={[styles.mBadge, { backgroundColor: "#E0E7FF" }]}>
                        <Text style={[styles.mBadgeText, { color: "#3730A3" }]}>💪 {meal.protein}g</Text>
                      </View>
                      <View style={[styles.mBadge, { backgroundColor: "#F1F5F9" }]}>
                        <Text style={[styles.mBadgeText, { color: "#475569" }]}>⏱️ {meal.prep_time}</Text>
                      </View>
                    </View>

                    {/* AI Reason */}
                    {meal.reason ? (
                      <View style={styles.reasonBox}>
                        <Text style={styles.reasonText} numberOfLines={2}>💡 {meal.reason}</Text>
                      </View>
                    ) : null}

                    {/* Actions */}
                    <View style={styles.actionRow}>
                      <TouchableOpacity
                        style={styles.btnActionSecondary}
                        onPress={() => onSelectRecipe && onSelectRecipe(meal)}
                      >
                        <Text style={styles.btnActionSecondaryText}>📖 View</Text>
                      </TouchableOpacity>

                      <TouchableOpacity
                        style={styles.btnActionSwap}
                        onPress={() => handleOpenSwapModal(slot.key, meal.recipe_id)}
                      >
                        <Text style={styles.btnActionSwapText}>🔄 Swap</Text>
                      </TouchableOpacity>

                      <TouchableOpacity
                        style={styles.btnActionPrimary}
                        onPress={() => handleLogMeal(meal)}
                      >
                        <Text style={styles.btnActionPrimaryText}>✅ Log</Text>
                      </TouchableOpacity>
                    </View>
                  </View>
                </View>
              );
            })}
          </View>
        )}

        {/* Empty Plan Card if No Active Plan */}
        {!activeDay && (
          <View style={styles.emptyPlanCard}>
            <Text style={styles.emptyPlanIcon}>📅</Text>
            <Text style={styles.emptyPlanTitle}>No Active Meal Plan</Text>
            <Text style={styles.emptyPlanText}>
              Generate a 7-day personalized AI meal plan tailored to your nutritional targets ({mealPlan?.target_calories || 1800} kcal, {mealPlan?.target_protein || 100}g protein).
            </Text>
            <TouchableOpacity style={styles.btnGenerateEmpty} onPress={handleRegenerate} disabled={regenerating}>
              {regenerating ? (
                <ActivityIndicator size="small" color="#FFFFFF" />
              ) : (
                <Text style={styles.btnGenerateEmptyText}>✨ Generate 7-Day AI Meal Plan</Text>
              )}
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>

      {/* Meal Swap Modal */}
      <Modal
        visible={swapModalVisible}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setSwapModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Swap {swapSlot.toUpperCase()} (Day {activeDayIndex})</Text>
              <TouchableOpacity onPress={() => setSwapModalVisible(false)}>
                <Text style={styles.modalCloseBtn}>✕</Text>
              </TouchableOpacity>
            </View>

            {loadingAlts ? (
              <View style={{ padding: 30, alignItems: "center" }}>
                <ActivityIndicator size="large" color={Colors.primary} />
                <Text style={{ marginTop: 10, color: Colors.textMuted }}>Finding matching alternative recipes...</Text>
              </View>
            ) : (
              <FlatList
                data={alternatives}
                keyExtractor={(item) => String(item.recipe_id)}
                renderItem={({ item }) => (
                  <TouchableOpacity
                    style={styles.altItem}
                    onPress={() => handleExecuteSwap(item.recipe_id)}
                  >
                    <Image
                      source={{ uri: resolveRecipeImageUrl(item.image_link) }}
                      style={styles.altImg}
                    />
                    <View style={styles.altInfo}>
                      <Text style={styles.altName} numberOfLines={1}>{item.recipe_name}</Text>
                      <Text style={styles.altMeta}>🔥 {item.calories} kcal • 💪 {item.protein}g Protein</Text>
                    </View>
                    <View style={styles.altSelectBtn}>
                      <Text style={styles.altSelectBtnText}>Select</Text>
                    </View>
                  </TouchableOpacity>
                )}
                contentContainerStyle={{ padding: 12 }}
                ListEmptyComponent={
                  <Text style={{ textAlign: "center", padding: 20, color: Colors.textMuted }}>
                    No alternative recipes found matching dietary rules.
                  </Text>
                }
              />
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F4F6F9"
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: "#F4F6F9",
    alignItems: "center",
    justifyContent: "center"
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: Colors.textMuted,
    fontWeight: "600"
  },
  scrollContent: {
    padding: 14,
    paddingBottom: 40
  },
  headerCard: {
    backgroundColor: "#7B2C3F",
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.12,
    shadowRadius: 8,
    elevation: 4
  },
  headerTopRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 12
  },
  planTitle: {
    fontSize: 17,
    fontWeight: "800",
    color: "#FFFFFF",
    marginBottom: 4
  },
  badgeRow: {
    flexDirection: "row",
    gap: 6
  },
  goalBadge: {
    backgroundColor: "#FF9E1F",
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6
  },
  goalBadgeText: {
    color: "#FFFFFF",
    fontSize: 10,
    fontWeight: "700"
  },
  btnRegenerate: {
    backgroundColor: "#FF9E1F",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20
  },
  btnRegenerateText: {
    color: "#FFFFFF",
    fontSize: 11,
    fontWeight: "700"
  },
  macroStrip: {
    flexDirection: "row",
    backgroundColor: "rgba(255,255,255,0.12)",
    borderRadius: 12,
    paddingVertical: 8,
    paddingHorizontal: 12,
    justifyContent: "space-between"
  },
  macroCol: {
    alignItems: "center"
  },
  macroVal: {
    color: "#FFD180",
    fontWeight: "700",
    fontSize: 13
  },
  macroLbl: {
    color: "rgba(255,255,255,0.75)",
    fontSize: 10,
    fontWeight: "600",
    textTransform: "uppercase"
  },
  daysTabScroll: {
    paddingBottom: 12,
    gap: 8
  },
  dayTab: {
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#E2E8F0",
    borderRadius: 12,
    paddingVertical: 10,
    paddingHorizontal: 14,
    alignItems: "center",
    minWidth: 86
  },
  dayTabActive: {
    backgroundColor: "#7B2C3F",
    borderColor: "#7B2C3F"
  },
  dayTabTitle: {
    fontSize: 13,
    fontWeight: "700",
    color: "#1E293B"
  },
  dayTabTitleActive: {
    color: "#FFFFFF"
  },
  dayTabSub: {
    fontSize: 11,
    color: "#64748B",
    marginBottom: 4
  },
  dayTabSubActive: {
    color: "rgba(255,255,255,0.8)"
  },
  diffPill: {
    backgroundColor: "#DCFCE7",
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8
  },
  diffPillActive: {
    backgroundColor: "rgba(255,255,255,0.25)"
  },
  diffPillText: {
    color: "#166534",
    fontSize: 9,
    fontWeight: "700"
  },
  diffPillTextActive: {
    color: "#FFD180"
  },
  daySummaryBox: {
    backgroundColor: "#FFFFFF",
    borderRadius: 14,
    padding: 12,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    marginBottom: 14
  },
  daySummaryHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8
  },
  daySummaryTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: "#0F172A"
  },
  daySummaryDiff: {
    fontSize: 11,
    fontWeight: "600",
    color: "#10B981"
  },
  summaryStatsRow: {
    flexDirection: "row",
    gap: 6,
    justifyContent: "space-between"
  },
  statPill: {
    flex: 1,
    backgroundColor: "#F8FAFC",
    borderRadius: 8,
    paddingVertical: 6,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#E2E8F0"
  },
  statVal: {
    fontSize: 12,
    fontWeight: "700",
    color: "#7B2C3F"
  },
  statLbl: {
    fontSize: 9,
    color: "#64748B",
    textTransform: "uppercase"
  },
  mealsContainer: {
    gap: 12
  },
  mealCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 14,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    overflow: "hidden"
  },
  slotHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: "#F8FAFC",
    borderBottomWidth: 1,
    borderBottomColor: "#E2E8F0"
  },
  slotTitle: {
    fontSize: 11,
    fontWeight: "800",
    letterSpacing: 0.5
  },
  vegBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4
  },
  vegBadgeText: {
    fontSize: 10,
    fontWeight: "700"
  },
  mealImage: {
    width: "100%",
    height: 120
  },
  mealBody: {
    padding: 12
  },
  recipeName: {
    fontSize: 14,
    fontWeight: "700",
    color: "#0F172A",
    marginBottom: 6
  },
  macroBadgesRow: {
    flexDirection: "row",
    gap: 6,
    marginBottom: 8
  },
  mBadge: {
    paddingHorizontal: 6,
    paddingVertical: 3,
    borderRadius: 6
  },
  mBadgeText: {
    fontSize: 10,
    fontWeight: "700"
  },
  reasonBox: {
    backgroundColor: "#FFFBEB",
    borderLeftWidth: 3,
    borderLeftColor: "#F59E0B",
    padding: 6,
    borderRadius: 4,
    marginBottom: 10
  },
  reasonText: {
    fontSize: 11,
    color: "#78350F",
    lineHeight: 14
  },
  actionRow: {
    flexDirection: "row",
    gap: 6
  },
  btnActionSecondary: {
    flex: 1,
    backgroundColor: "#F1F5F9",
    paddingVertical: 6,
    borderRadius: 6,
    alignItems: "center"
  },
  btnActionSecondaryText: {
    fontSize: 11,
    fontWeight: "600",
    color: "#334155"
  },
  btnActionSwap: {
    flex: 1,
    backgroundColor: "#E0E7FF",
    paddingVertical: 6,
    borderRadius: 6,
    alignItems: "center"
  },
  btnActionSwapText: {
    fontSize: 11,
    fontWeight: "700",
    color: "#3730A3"
  },
  btnActionPrimary: {
    flex: 1,
    backgroundColor: Colors.accent,
    paddingVertical: 6,
    borderRadius: 6,
    alignItems: "center"
  },
  btnActionPrimaryText: {
    fontSize: 11,
    fontWeight: "700",
    color: "#FFFFFF"
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.5)",
    justifyContent: "flex-end"
  },
  modalContent: {
    backgroundColor: "#FFFFFF",
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: "75%",
    paddingBottom: 20
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#E2E8F0"
  },
  modalTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: "#0F172A"
  },
  modalCloseBtn: {
    fontSize: 18,
    fontWeight: "700",
    color: "#64748B",
    padding: 4
  },
  altItem: {
    flexDirection: "row",
    alignItems: "center",
    padding: 8,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    borderRadius: 10,
    marginBottom: 8
  },
  altImg: {
    width: 50,
    height: 50,
    borderRadius: 8,
    marginRight: 10
  },
  altInfo: {
    flex: 1
  },
  altName: {
    fontSize: 13,
    fontWeight: "700",
    color: "#0F172A"
  },
  altMeta: {
    fontSize: 11,
    color: "#64748B",
    marginTop: 2
  },
  altSelectBtn: {
    backgroundColor: "#7B2C3F",
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 6
  },
  altSelectBtnText: {
    color: "#FFFFFF",
    fontSize: 11,
    fontWeight: "700"
  },
  emptyPlanCard: {
    backgroundColor: "#FFFFFF",
    marginHorizontal: 16,
    marginVertical: 24,
    borderRadius: 16,
    padding: 28,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#E2E8F0",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2
  },
  emptyPlanIcon: {
    fontSize: 42,
    marginBottom: 12
  },
  emptyPlanTitle: {
    fontSize: 18,
    fontWeight: "800",
    color: "#0F172A",
    marginBottom: 8
  },
  emptyPlanText: {
    fontSize: 13,
    color: "#64748B",
    textAlign: "center",
    lineHeight: 19,
    marginBottom: 18
  },
  btnGenerateEmpty: {
    backgroundColor: "#7B2C3F",
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 12
  },
  btnGenerateEmptyText: {
    color: "#FFFFFF",
    fontSize: 14,
    fontWeight: "700"
  }
});
