import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
  ScrollView,
  Image,
  RefreshControl
} from "react-native";
import { Colors } from "../theme/colors";
import RecipeCard from "../components/RecipeCard";
import { fetchHistory, fetchNutritionAnalytics } from "../services/api";

export default function HistoryScreen({ onSelectRecipe, userId = null }) {
  const [mainTab, setMainTab] = useState("analytics"); // 'analytics' | 'log'
  const [analyticsSubTab, setAnalyticsSubTab] = useState("today"); // 'today' | 'week' | 'month'
  const [history, setHistory] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, [userId]);

  const loadData = async () => {
    setLoading(true);
    const [histData, analData] = await Promise.all([
      fetchHistory(userId),
      fetchNutritionAnalytics(userId)
    ]);
    setHistory(histData || []);
    if (analData?.success && analData?.analytics) {
      setAnalytics(analData.analytics);
    }
    setLoading(false);
    setRefreshing(false);
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  const today = analytics?.today || {};
  const week = analytics?.week || {};
  const month = analytics?.month || {};

  return (
    <View style={styles.container}>
      {/* Top Header */}
      <View style={styles.header}>
        <Text style={styles.title}>📊 Nutrition & History</Text>
        <Text style={styles.subTitle}>Real-time analytics and meals cooked from the database</Text>

        {/* Main Segmented Toggle */}
        <View style={styles.segmentedContainer}>
          <TouchableOpacity
            style={[styles.segmentBtn, mainTab === "analytics" && styles.segmentBtnActive]}
            onPress={() => setMainTab("analytics")}
          >
            <Text style={[styles.segmentBtnText, mainTab === "analytics" && styles.segmentBtnTextActive]}>
              📊 Nutrition Dashboard
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.segmentBtn, mainTab === "log" && styles.segmentBtnActive]}
            onPress={() => setMainTab("log")}
          >
            <Text style={[styles.segmentBtnText, mainTab === "log" && styles.segmentBtnTextActive]}>
              📖 Eaten Log ({history.length})
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {loading ? (
        <View style={styles.loadingBox}>
          <ActivityIndicator size="large" color={Colors.primary} />
          <Text style={styles.loadingText}>Loading nutrition analytics...</Text>
        </View>
      ) : mainTab === "analytics" ? (
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={["#7B2C3F"]} />
          }
        >
          {/* Sub Tab Switcher: Today | Week | Month */}
          <View style={styles.subTabContainer}>
            <TouchableOpacity
              style={[styles.subTabBtn, analyticsSubTab === "today" && styles.subTabBtnActive]}
              onPress={() => setAnalyticsSubTab("today")}
            >
              <Text style={[styles.subTabBtnText, analyticsSubTab === "today" && styles.subTabBtnTextActive]}>
                ☀️ Today
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.subTabBtn, analyticsSubTab === "week" && styles.subTabBtnActive]}
              onPress={() => setAnalyticsSubTab("week")}
            >
              <Text style={[styles.subTabBtnText, analyticsSubTab === "week" && styles.subTabBtnTextActive]}>
                📅 Week (7D)
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.subTabBtn, analyticsSubTab === "month" && styles.subTabBtnActive]}
              onPress={() => setAnalyticsSubTab("month")}
            >
              <Text style={[styles.subTabBtnText, analyticsSubTab === "month" && styles.subTabBtnTextActive]}>
                📈 Month (30D)
              </Text>
            </TouchableOpacity>
          </View>

          {/* ======================================================== */}
          {/* 1. TODAY ANALYTICS VIEW */}
          {/* ======================================================== */}
          {analyticsSubTab === "today" && (
            <View>
              {/* Adherence Banner */}
              <View style={styles.bannerCard}>
                <View style={styles.bannerRow}>
                  <View>
                    <Text style={styles.bannerTitle}>Today's Nutrition Intake</Text>
                    <Text style={styles.bannerSub}>{today.date_formatted || "Today"}</Text>
                  </View>
                  <View style={styles.adherenceBadge}>
                    <Text style={styles.adherenceBadgeText}>
                      {today.goal_completion_pct || 0}% Target
                    </Text>
                  </View>
                </View>
              </View>

              {/* 4 Macro Cards Grid */}
              <View style={styles.macroCardsGrid}>
                {/* Calories */}
                <View style={[styles.macroCard, { borderLeftColor: "#F59E0B" }]}>
                  <View style={styles.macroCardHeader}>
                    <Text style={styles.macroCardLabel}>🔥 Calories</Text>
                    <Text style={[styles.macroCardPct, { color: "#D97706" }]}>{today.goal_completion_pct || 0}%</Text>
                  </View>
                  <Text style={styles.macroCardVal}>{today.consumed_calories || 0} <Text style={styles.macroCardTarget}>/ {today.target_calories || 1800} kcal</Text></Text>
                  <View style={styles.progressBarBg}>
                    <View style={[styles.progressBarFill, { width: `${Math.min(100, today.goal_completion_pct || 0)}%`, backgroundColor: "#F59E0B" }]} />
                  </View>
                  <Text style={styles.macroCardRemaining}>Remaining: {today.remaining_calories || 0} kcal</Text>
                </View>

                {/* Protein */}
                <View style={[styles.macroCard, { borderLeftColor: "#7B2C3F" }]}>
                  <View style={styles.macroCardHeader}>
                    <Text style={styles.macroCardLabel}>💪 Protein</Text>
                    <Text style={[styles.macroCardPct, { color: "#7B2C3F" }]}>{today.protein_completion_pct || 0}%</Text>
                  </View>
                  <Text style={[styles.macroCardVal, { color: "#7B2C3F" }]}>{today.consumed_protein || 0}g <Text style={styles.macroCardTarget}>/ {today.target_protein || 100}g</Text></Text>
                  <View style={styles.progressBarBg}>
                    <View style={[styles.progressBarFill, { width: `${Math.min(100, today.protein_completion_pct || 0)}%`, backgroundColor: "#7B2C3F" }]} />
                  </View>
                  <Text style={styles.macroCardRemaining}>Remaining: {today.remaining_protein || 0}g</Text>
                </View>

                {/* Carbs */}
                <View style={[styles.macroCard, { borderLeftColor: "#10B981" }]}>
                  <View style={styles.macroCardHeader}>
                    <Text style={styles.macroCardLabel}>🍞 Carbs</Text>
                    <Text style={[styles.macroCardPct, { color: "#059669" }]}>{today.carbs_completion_pct || 0}%</Text>
                  </View>
                  <Text style={[styles.macroCardVal, { color: "#10B981" }]}>{today.consumed_carbs || 0}g <Text style={styles.macroCardTarget}>/ {today.target_carbs || 200}g</Text></Text>
                  <View style={styles.progressBarBg}>
                    <View style={[styles.progressBarFill, { width: `${Math.min(100, today.carbs_completion_pct || 0)}%`, backgroundColor: "#10B981" }]} />
                  </View>
                  <Text style={styles.macroCardRemaining}>Remaining: {today.remaining_carbs || 0}g</Text>
                </View>

                {/* Fat */}
                <View style={[styles.macroCard, { borderLeftColor: "#EF4444" }]}>
                  <View style={styles.macroCardHeader}>
                    <Text style={styles.macroCardLabel}>🥑 Healthy Fats</Text>
                    <Text style={[styles.macroCardPct, { color: "#DC2626" }]}>{today.fat_completion_pct || 0}%</Text>
                  </View>
                  <Text style={[styles.macroCardVal, { color: "#EF4444" }]}>{today.consumed_fat || 0}g <Text style={styles.macroCardTarget}>/ {today.target_fat || 50}g</Text></Text>
                  <View style={styles.progressBarBg}>
                    <View style={[styles.progressBarFill, { width: `${Math.min(100, today.fat_completion_pct || 0)}%`, backgroundColor: "#EF4444" }]} />
                  </View>
                  <Text style={styles.macroCardRemaining}>Remaining: {today.remaining_fat || 0}g</Text>
                </View>
              </View>

              {/* Today's Meals List */}
              <View style={styles.sectionCard}>
                <Text style={styles.sectionTitle}>🍽️ Today's Logged Meals ({today.today_meals?.length || 0})</Text>
                {today.today_meals && today.today_meals.length > 0 ? (
                  today.today_meals.map((m, idx) => (
                    <View key={`today-meal-${idx}`} style={styles.todayMealItem}>
                      <Image
                        source={{ uri: m.image_link || "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500" }}
                        style={styles.todayMealImg}
                      />
                      <View style={styles.todayMealInfo}>
                        <Text style={styles.todayMealName} numberOfLines={1}>{m.recipe_name}</Text>
                        <Text style={styles.todayMealSub}>{m.serving_size}x serving • {m.logged_time}</Text>
                      </View>
                      <View style={styles.todayMealNutri}>
                        <Text style={styles.todayMealCal}>🔥 {m.calories} kcal</Text>
                        <Text style={styles.todayMealMacro}>{m.protein}g P • {m.carbs}g C</Text>
                      </View>
                    </View>
                  ))
                ) : (
                  <Text style={styles.emptyNotice}>No meals logged yet today. Log recipes from the Home screen.</Text>
                )}
              </View>
            </View>
          )}

          {/* ======================================================== */}
          {/* 2. WEEK ANALYTICS VIEW (7 Days) */}
          {/* ======================================================== */}
          {analyticsSubTab === "week" && (
            <View>
              {/* Stat Summary Grid */}
              <View style={styles.statsGrid}>
                <View style={styles.statBox}>
                  <Text style={styles.statLbl}>Avg Daily Cal</Text>
                  <Text style={[styles.statNum, { color: "#F59E0B" }]}>{week.avg_daily_calories || 0}</Text>
                  <Text style={styles.statSub}>Target: {week.target_calories || 1800}</Text>
                </View>
                <View style={styles.statBox}>
                  <Text style={styles.statLbl}>Avg Daily Prot</Text>
                  <Text style={[styles.statNum, { color: "#7B2C3F" }]}>{week.avg_daily_protein || 0}g</Text>
                  <Text style={styles.statSub}>Target: {week.target_protein || 100}g</Text>
                </View>
                <View style={styles.statBox}>
                  <Text style={styles.statLbl}>Meals Logged</Text>
                  <Text style={[styles.statNum, { color: "#10B981" }]}>{week.total_meals_logged || 0}</Text>
                  <Text style={styles.statSub}>Past 7 days</Text>
                </View>
                <View style={styles.statBox}>
                  <Text style={styles.statLbl}>Active Days</Text>
                  <Text style={[styles.statNum, { color: "#3B82F6" }]}>{week.active_days_count || 0} / 7</Text>
                  <Text style={styles.statSub}>Consistency</Text>
                </View>
              </View>

              {/* 7-Day Visual Calorie Chart Card */}
              <View style={styles.sectionCard}>
                <Text style={styles.sectionTitle}>📊 7-Day Calorie Intake vs. Target</Text>
                <View style={styles.chartContainer}>
                  {(week.labels || []).map((lbl, idx) => {
                    const cal = week.calories?.[idx] || 0;
                    const target = week.targets?.[idx] || 1800;
                    const maxScale = Math.max(...(week.calories || [1800]), target, 2200);
                    const barHeightPct = Math.min(100, Math.max(10, Math.round((cal / maxScale) * 100)));
                    const isToday = idx === (week.labels?.length - 1);

                    return (
                      <View key={`bar-${idx}`} style={styles.barCol}>
                        <Text style={styles.barValText}>{cal > 0 ? `${cal}` : "-"}</Text>
                        <View style={styles.barTrack}>
                          <View
                            style={[
                              styles.barFill,
                              {
                                height: `${barHeightPct}%`,
                                backgroundColor: isToday ? "#7B2C3F" : cal >= target * 0.8 ? "#FF9E1F" : "#CBD5E1"
                              }
                            ]}
                          />
                        </View>
                        <Text style={[styles.barLblText, isToday && styles.barLblTextActive]}>
                          {lbl.substring(0, 3)}
                        </Text>
                      </View>
                    );
                  })}
                </View>
                <View style={styles.chartLegend}>
                  <View style={[styles.legendDot, { backgroundColor: "#FF9E1F" }]} />
                  <Text style={styles.legendText}>Logged Intake (Target: {week.target_calories || 1800} kcal)</Text>
                </View>
              </View>
            </View>
          )}

          {/* ======================================================== */}
          {/* 3. MONTH ANALYTICS VIEW (30 Days) */}
          {/* ======================================================== */}
          {analyticsSubTab === "month" && (
            <View>
              {/* Monthly Stats */}
              <View style={styles.statsGrid}>
                <View style={styles.statBox}>
                  <Text style={styles.statLbl}>Monthly Avg Cal</Text>
                  <Text style={[styles.statNum, { color: "#F59E0B" }]}>{month.avg_daily_calories || 0}</Text>
                  <Text style={styles.statSub}>kcal/day</Text>
                </View>
                <View style={styles.statBox}>
                  <Text style={styles.statLbl}>Goal Adherence</Text>
                  <Text style={[styles.statNum, { color: "#10B981" }]}>{month.goal_adherence_pct || 0}%</Text>
                  <Text style={styles.statSub}>On Track</Text>
                </View>
                <View style={styles.statBox}>
                  <Text style={styles.statLbl}>Meal Frequency</Text>
                  <Text style={[styles.statNum, { color: "#7B2C3F" }]}>{month.avg_meals_per_day || 0}</Text>
                  <Text style={styles.statSub}>meals/day</Text>
                </View>
                <View style={styles.statBox}>
                  <Text style={styles.statLbl}>Total Logged</Text>
                  <Text style={[styles.statNum, { color: "#3B82F6" }]}>{month.total_meals_logged || 0}</Text>
                  <Text style={styles.statSub}>30-Day total</Text>
                </View>
              </View>

              {/* Most Eaten Recipes */}
              <View style={styles.sectionCard}>
                <Text style={styles.sectionTitle}>👑 Most Eaten Recipes</Text>
                {month.most_eaten_recipes && month.most_eaten_recipes.length > 0 ? (
                  month.most_eaten_recipes.map((r, idx) => (
                    <View key={`top-${idx}`} style={styles.topRecipeItem}>
                      <Text style={styles.topRecipeRank}>#{idx + 1}</Text>
                      <Image source={{ uri: r.image_link }} style={styles.topRecipeImg} />
                      <Text style={styles.topRecipeName} numberOfLines={1}>{r.recipe_name}</Text>
                      <View style={styles.topRecipeBadge}>
                        <Text style={styles.topRecipeBadgeText}>{r.times_eaten}x eaten</Text>
                      </View>
                    </View>
                  ))
                ) : (
                  <Text style={styles.emptyNotice}>No recipe history recorded yet.</Text>
                )}
              </View>

              {/* Preferred Categories */}
              <View style={styles.sectionCard}>
                <Text style={styles.sectionTitle}>🏷️ Preferred Categories & Cuisines</Text>
                <View style={styles.categoryChipsWrap}>
                  {month.preferred_categories && month.preferred_categories.length > 0 ? (
                    month.preferred_categories.map((c, idx) => (
                      <View key={`cat-${idx}`} style={styles.catChip}>
                        <Text style={styles.catChipText}>{c.category} ({c.count})</Text>
                      </View>
                    ))
                  ) : (
                    <Text style={styles.emptyNotice}>No category history recorded yet.</Text>
                  )}
                </View>
              </View>
            </View>
          )}
        </ScrollView>
      ) : (
        /* ======================================================== */
        /* 4. EATEN RECIPES LOG FEED (Preserving existing behavior) */
        /* ======================================================== */
        <FlatList
          data={history}
          keyExtractor={(item, index) => item.recipe_id ? String(item.recipe_id) + index : String(index)}
          renderItem={({ item }) => (
            <View>
              <RecipeCard recipe={item} onPress={onSelectRecipe} />
              {Boolean(item.user_rating) ? (
                <View style={styles.ratingBadge}>
                  <Text style={styles.ratingBadgeText}>⭐ Rated {item.user_rating}/5: "{item.user_comment || "Good"}"</Text>
                </View>
              ) : null}
            </View>
          )}
          contentContainerStyle={styles.list}
          ListEmptyComponent={
            <View style={styles.emptyBox}>
              <Text style={styles.emptyTitle}>No Recipes Logged Yet</Text>
              <Text style={styles.emptyText}>Tap on any recipe from the Home screen and tap "Mark as Cooked / Eaten" to log it here.</Text>
            </View>
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
    padding: 16,
    backgroundColor: "#FFFFFF",
    borderBottomWidth: 1,
    borderBottomColor: "#E2E8F0"
  },
  title: {
    fontSize: 20,
    fontWeight: "800",
    color: "#0F172A"
  },
  subTitle: {
    fontSize: 12,
    color: "#64748B",
    marginTop: 2,
    marginBottom: 12
  },
  segmentedContainer: {
    flexDirection: "row",
    backgroundColor: "#F1F5F9",
    borderRadius: 10,
    padding: 3
  },
  segmentBtn: {
    flex: 1,
    paddingVertical: 7,
    alignItems: "center",
    borderRadius: 8
  },
  segmentBtnActive: {
    backgroundColor: "#7B2C3F"
  },
  segmentBtnText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#64748B"
  },
  segmentBtnTextActive: {
    color: "#FFFFFF",
    fontWeight: "700"
  },
  subTabContainer: {
    flexDirection: "row",
    backgroundColor: "#FFFFFF",
    borderRadius: 12,
    padding: 4,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: "#E2E8F0"
  },
  subTabBtn: {
    flex: 1,
    paddingVertical: 8,
    alignItems: "center",
    borderRadius: 8
  },
  subTabBtnActive: {
    backgroundColor: "#FF9E1F"
  },
  subTabBtnText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#64748B"
  },
  subTabBtnTextActive: {
    color: "#FFFFFF",
    fontWeight: "700"
  },
  scrollContent: {
    padding: 14,
    paddingBottom: 40
  },
  bannerCard: {
    backgroundColor: "#7B2C3F",
    borderRadius: 14,
    padding: 14,
    marginBottom: 14
  },
  bannerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center"
  },
  bannerTitle: {
    color: "#FFFFFF",
    fontSize: 15,
    fontWeight: "700"
  },
  bannerSub: {
    color: "rgba(255,255,255,0.75)",
    fontSize: 11,
    marginTop: 2
  },
  adherenceBadge: {
    backgroundColor: "#FF9E1F",
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12
  },
  adherenceBadgeText: {
    color: "#FFFFFF",
    fontSize: 11,
    fontWeight: "700"
  },
  macroCardsGrid: {
    gap: 10,
    marginBottom: 14
  },
  macroCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 12,
    padding: 12,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    borderLeftWidth: 4
  },
  macroCardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4
  },
  macroCardLabel: {
    fontSize: 12,
    fontWeight: "700",
    color: "#334155"
  },
  macroCardPct: {
    fontSize: 11,
    fontWeight: "700"
  },
  macroCardVal: {
    fontSize: 16,
    fontWeight: "800",
    color: "#0F172A"
  },
  macroCardTarget: {
    fontSize: 12,
    color: "#64748B",
    fontWeight: "500"
  },
  progressBarBg: {
    height: 6,
    backgroundColor: "#F1F5F9",
    borderRadius: 3,
    marginVertical: 6,
    overflow: "hidden"
  },
  progressBarFill: {
    height: "100%",
    borderRadius: 3
  },
  macroCardRemaining: {
    fontSize: 11,
    color: "#64748B"
  },
  sectionCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    marginBottom: 14
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: "#0F172A",
    marginBottom: 10
  },
  todayMealItem: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: "#F1F5F9"
  },
  todayMealImg: {
    width: 44,
    height: 44,
    borderRadius: 8,
    marginRight: 10
  },
  todayMealInfo: {
    flex: 1
  },
  todayMealName: {
    fontSize: 13,
    fontWeight: "700",
    color: "#0F172A"
  },
  todayMealSub: {
    fontSize: 11,
    color: "#64748B",
    marginTop: 2
  },
  todayMealNutri: {
    alignItems: "flex-end"
  },
  todayMealCal: {
    fontSize: 12,
    fontWeight: "700",
    color: "#D97706"
  },
  todayMealMacro: {
    fontSize: 10,
    color: "#64748B",
    marginTop: 1
  },
  statsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 14
  },
  statBox: {
    flex: 1,
    minWidth: "46%",
    backgroundColor: "#FFFFFF",
    borderRadius: 12,
    padding: 12,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    alignItems: "center"
  },
  statLbl: {
    fontSize: 11,
    color: "#64748B",
    fontWeight: "600"
  },
  statNum: {
    fontSize: 18,
    fontWeight: "800",
    marginVertical: 2
  },
  statSub: {
    fontSize: 10,
    color: "#94A3B8"
  },
  chartContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-end",
    height: 140,
    paddingTop: 20,
    paddingBottom: 4
  },
  barCol: {
    flex: 1,
    alignItems: "center",
    height: "100%",
    justifyContent: "flex-end"
  },
  barValText: {
    fontSize: 8,
    color: "#64748B",
    marginBottom: 2
  },
  barTrack: {
    width: 14,
    height: 90,
    backgroundColor: "#F1F5F9",
    borderRadius: 6,
    justifyContent: "flex-end",
    overflow: "hidden"
  },
  barFill: {
    width: "100%",
    borderRadius: 6
  },
  barLblText: {
    fontSize: 10,
    color: "#64748B",
    marginTop: 4
  },
  barLblTextActive: {
    fontWeight: "700",
    color: "#7B2C3F"
  },
  chartLegend: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    marginTop: 10,
    gap: 6
  },
  legendDot: {
    width: 8,
    height: 8,
    borderRadius: 4
  },
  legendText: {
    fontSize: 11,
    color: "#64748B"
  },
  topRecipeItem: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: "#F1F5F9"
  },
  topRecipeRank: {
    fontSize: 13,
    fontWeight: "800",
    color: "#7B2C3F",
    width: 26
  },
  topRecipeImg: {
    width: 38,
    height: 38,
    borderRadius: 6,
    marginRight: 10
  },
  topRecipeName: {
    flex: 1,
    fontSize: 13,
    fontWeight: "600",
    color: "#0F172A"
  },
  topRecipeBadge: {
    backgroundColor: "#FEF3C7",
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6
  },
  topRecipeBadgeText: {
    fontSize: 11,
    color: "#92400E",
    fontWeight: "700"
  },
  categoryChipsWrap: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6
  },
  catChip: {
    backgroundColor: "#F1F5F9",
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 16
  },
  catChipText: {
    fontSize: 11,
    color: "#334155",
    fontWeight: "600"
  },
  emptyNotice: {
    fontSize: 12,
    color: "#94A3B8",
    textAlign: "center",
    paddingVertical: 12
  },
  list: {
    padding: 16
  },
  ratingBadge: {
    backgroundColor: "#FEF3C7",
    padding: 8,
    borderRadius: 8,
    marginTop: -10,
    marginBottom: 16,
    marginHorizontal: 4
  },
  ratingBadgeText: {
    color: "#92400E",
    fontSize: 12,
    fontWeight: "600"
  },
  loadingBox: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center"
  },
  loadingText: {
    marginTop: 10,
    color: Colors.textMuted,
    fontSize: 13
  },
  emptyBox: {
    alignItems: "center",
    padding: 40
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: Colors.textDark,
    marginBottom: 6
  },
  emptyText: {
    fontSize: 13,
    color: Colors.textMuted,
    textAlign: "center",
    lineHeight: 18
  }
});
