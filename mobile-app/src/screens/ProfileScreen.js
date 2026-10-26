import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  ScrollView,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert
} from "react-native";
import { Colors } from "../theme/colors";
import { fetchUserProfile, updateUserProfile } from "../services/api";

const DIET_GOALS = [
  { id: "weight_loss", label: "🥗 Weight Loss (-500 kcal)" },
  { id: "muscle_gain", label: "🥩 Muscle Gain (+350 kcal)" },
  { id: "maintenance", label: "⚖️ Maintenance (Equilibrium)" },
  { id: "diabetic", label: "🩸 Diabetic Friendly" },
  { id: "keto", label: "🥑 Keto / Low Carb" }
];

const FOOD_PREFS = [
  { id: "both", label: "🍽️ Both (Veg & Non-Veg)" },
  { id: "veg", label: "🌱 Pure Vegetarian" },
  { id: "nonveg", label: "🍗 Non-Vegetarian" }
];

const GENDER_OPTIONS = [
  { id: "male", label: "👨 Male" },
  { id: "female", label: "👩 Female" }
];

export default function ProfileScreen({
  currentUser = null,
  onOpenAuth = null,
  onNavigateToHistory = null,
  onNavigateToPlanner = null
}) {
  const userId = currentUser?.objectId || currentUser?.id || null;

  const [age, setAge] = useState("25");
  const [gender, setGender] = useState("male");
  const [height, setHeight] = useState("175");
  const [weight, setWeight] = useState("70");
  const [dietGoal, setDietGoal] = useState("weight_loss");
  const [foodPref, setFoodPref] = useState("both");
  const [allergies, setAllergies] = useState("peanuts, shellfish");
  const [durationMonths, setDurationMonths] = useState("3");
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadProfile();
  }, [currentUser]);

  const loadProfile = async () => {
    setLoading(true);
    const res = await fetchUserProfile(userId);
    if (res.success && res.profile) {
      const p = res.profile;
      if (p.age) setAge(String(p.age));
      if (p.gender) setGender(String(p.gender));
      if (p.height) setHeight(String(p.height));
      if (p.weight) setWeight(String(p.weight));
      if (p.diet_goal) setDietGoal(String(p.diet_goal));
      if (p.food_pref) setFoodPref(String(p.food_pref));
      if (p.duration_months) setDurationMonths(String(p.duration_months));
      if (p.allergies) setAllergies(Array.isArray(p.allergies) ? p.allergies.join(", ") : String(p.allergies));
      if (res.diet_report) setReport(res.diet_report);
    }
    setLoading(false);
  };

  const handleSave = async () => {
    setSaving(true);
    const payload = {
      age: parseInt(age) || 25,
      gender: gender,
      height: parseFloat(height) || 170,
      weight: parseFloat(weight) || 70,
      diet_goal: dietGoal,
      food_pref: foodPref,
      duration_months: parseInt(durationMonths) || 3,
      allergies: allergies
    };
    const res = await updateUserProfile(userId, payload);
    setSaving(false);
    if (res.success) {
      Alert.alert("Profile Updated! ✅", "Your Mifflin-St Jeor metabolic baseline and targets are updated!");
      loadProfile();
    } else {
      Alert.alert("Notice", res.message || "Failed to update profile.");
    }
  };

  // BMI Calculation
  const numHeightM = (parseFloat(height) || 170) / 100;
  const numWeightKg = parseFloat(weight) || 70;
  const bmi = (numWeightKg / (numHeightM * numHeightM)).toFixed(1);

  let bmiCategory = "Normal";
  let bmiColor = "#10B981";
  if (bmi < 18.5) { bmiCategory = "Underweight"; bmiColor = "#3B82F6"; }
  else if (bmi >= 25 && bmi < 30) { bmiCategory = "Overweight"; bmiColor = "#F59E0B"; }
  else if (bmi >= 30) { bmiCategory = "Obese"; bmiColor = "#EF4444"; }

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        {/* User Account Bar */}
        <View style={styles.accountCard}>
          <View style={styles.accountInfo}>
            <Text style={styles.accountName}>
              {currentUser ? `👤 ${currentUser.name || "User"}` : "👤 Guest User"}
            </Text>
            <Text style={styles.accountEmail}>
              {currentUser ? currentUser.email : "Sign in to sync your profile across devices"}
            </Text>
          </View>
          <TouchableOpacity style={styles.accountBtn} onPress={onOpenAuth}>
            <Text style={styles.accountBtnText}>{currentUser ? "Switch" : "Sign In"}</Text>
          </TouchableOpacity>
        </View>

        {/* Quick Nav Shortcuts: History & Meal Plan */}
        <View style={styles.shortcutsRow}>
          <TouchableOpacity style={styles.shortcutCard} onPress={onNavigateToHistory}>
            <Text style={styles.shortcutIcon}>📊</Text>
            <Text style={styles.shortcutTitle}>Nutrition History</Text>
            <Text style={styles.shortcutSub}>Analytics & Eaten Log</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.shortcutCard} onPress={onNavigateToPlanner}>
            <Text style={styles.shortcutIcon}>📅</Text>
            <Text style={styles.shortcutTitle}>7-Day Meal Plan</Text>
            <Text style={styles.shortcutSub}>AI Macro Schedule</Text>
          </TouchableOpacity>
        </View>

        {/* Metabolic Target Card */}
        {report && report.target_goals && (
          <View style={styles.targetCard}>
            <Text style={styles.targetHeader}>🎯 Target Calorie & Macro Goals</Text>
            <View style={styles.statGrid}>
              <View style={styles.statBox}>
                <Text style={styles.statVal}>{report.target_goals.bmr}</Text>
                <Text style={styles.statLbl}>BMR kcal</Text>
              </View>
              <View style={styles.statBox}>
                <Text style={styles.statVal}>{report.target_goals.tdee}</Text>
                <Text style={styles.statLbl}>TDEE kcal</Text>
              </View>
              <View style={[styles.statBox, { backgroundColor: "#FEF3C7" }]}>
                <Text style={[styles.statVal, { color: "#92400E" }]}>{report.target_goals.target_calories}</Text>
                <Text style={[styles.statLbl, { color: "#92400E" }]}>Target kcal</Text>
              </View>
            </View>

            {/* BMI Badge Row */}
            <View style={styles.bmiRow}>
              <Text style={styles.bmiText}>Calculated BMI: <Text style={{ fontWeight: "bold" }}>{bmi}</Text></Text>
              <View style={[styles.bmiBadge, { backgroundColor: `${bmiColor}20` }]}>
                <Text style={[styles.bmiBadgeText, { color: bmiColor }]}>{bmiCategory}</Text>
              </View>
            </View>

            <Text style={styles.strategyText}>💡 {report.strategy_text || "Calorie equilibrium target."}</Text>
          </View>
        )}

        {/* Profile Inputs Form */}
        <View style={styles.formCard}>
          <Text style={styles.formHeader}>⚙️ Update Physical Stats & Goals</Text>

          {/* Gender Selector */}
          <Text style={styles.label}>Gender</Text>
          <View style={styles.pillSelectorRow}>
            {GENDER_OPTIONS.map((g) => (
              <TouchableOpacity
                key={g.id}
                style={[styles.pillOption, gender === g.id && styles.pillOptionActive]}
                onPress={() => setGender(g.id)}
              >
                <Text style={[styles.pillOptionText, gender === g.id && styles.pillOptionTextActive]}>
                  {g.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* Age & Duration Row */}
          <View style={styles.twoColRow}>
            <View style={styles.colHalf}>
              <Text style={styles.label}>Age (years)</Text>
              <TextInput style={styles.input} value={age} onChangeText={setAge} keyboardType="numeric" />
            </View>
            <View style={styles.colHalf}>
              <Text style={styles.label}>Target (months)</Text>
              <TextInput style={styles.input} value={durationMonths} onChangeText={setDurationMonths} keyboardType="numeric" />
            </View>
          </View>

          {/* Height & Weight Row */}
          <View style={styles.twoColRow}>
            <View style={styles.colHalf}>
              <Text style={styles.label}>Height (cm)</Text>
              <TextInput style={styles.input} value={height} onChangeText={setHeight} keyboardType="numeric" />
            </View>
            <View style={styles.colHalf}>
              <Text style={styles.label}>Weight (kg)</Text>
              <TextInput style={styles.input} value={weight} onChangeText={setWeight} keyboardType="numeric" />
            </View>
          </View>

          {/* Food Preference Selector */}
          <Text style={styles.label}>Food Preference</Text>
          <View style={styles.goalPillsWrap}>
            {FOOD_PREFS.map((f) => (
              <TouchableOpacity
                key={f.id}
                style={[styles.goalPill, foodPref === f.id && styles.goalPillActive]}
                onPress={() => setFoodPref(f.id)}
              >
                <Text style={[styles.goalPillText, foodPref === f.id && styles.goalPillTextActive]}>
                  {f.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* Diet Goal Selector */}
          <Text style={styles.label}>Health & Diet Goal</Text>
          <View style={styles.goalPillsWrap}>
            {DIET_GOALS.map((d) => (
              <TouchableOpacity
                key={d.id}
                style={[styles.goalPill, dietGoal === d.id && styles.goalPillActivePrimary]}
                onPress={() => setDietGoal(d.id)}
              >
                <Text style={[styles.goalPillText, dietGoal === d.id && styles.goalPillTextActive]}>
                  {d.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* Allergies Input */}
          <Text style={styles.label}>Allergies (comma separated)</Text>
          <TextInput
            style={styles.input}
            value={allergies}
            onChangeText={setAllergies}
            placeholder="e.g. peanuts, shellfish, milk, eggs"
            placeholderTextColor="#94A3B8"
          />

          {/* Save Button */}
          <TouchableOpacity style={styles.saveBtn} onPress={handleSave} disabled={saving}>
            {saving ? (
              <ActivityIndicator color="#FFFFFF" />
            ) : (
              <Text style={styles.saveBtnText}>💾 Save & Recalculate Targets</Text>
            )}
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F8FAFC"
  },
  scroll: {
    padding: 16,
    paddingBottom: 36
  },
  accountCard: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: "#FFFFFF",
    borderRadius: 14,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: "#E2E8F0"
  },
  accountInfo: {
    flex: 1,
    marginRight: 10
  },
  accountName: {
    fontSize: 16,
    fontWeight: "800",
    color: "#0F172A"
  },
  accountEmail: {
    fontSize: 12,
    color: "#64748B",
    marginTop: 2
  },
  accountBtn: {
    backgroundColor: "#7B2C3F",
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 10
  },
  accountBtnText: {
    color: "#FFFFFF",
    fontWeight: "700",
    fontSize: 12
  },
  shortcutsRow: {
    flexDirection: "row",
    gap: 10,
    marginBottom: 14
  },
  shortcutCard: {
    flex: 1,
    backgroundColor: "#FFFFFF",
    borderRadius: 12,
    padding: 12,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    alignItems: "center"
  },
  shortcutIcon: {
    fontSize: 22,
    marginBottom: 4
  },
  shortcutTitle: {
    fontSize: 12,
    fontWeight: "700",
    color: "#0F172A"
  },
  shortcutSub: {
    fontSize: 10,
    color: "#64748B",
    marginTop: 1
  },
  targetCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 14,
    padding: 16,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: "#E2E8F0"
  },
  targetHeader: {
    fontSize: 15,
    fontWeight: "800",
    color: "#0F172A",
    marginBottom: 10
  },
  statGrid: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 10
  },
  statBox: {
    backgroundColor: "#F1F5F9",
    padding: 10,
    borderRadius: 10,
    alignItems: "center",
    flex: 1,
    marginHorizontal: 3
  },
  statVal: {
    fontSize: 16,
    fontWeight: "800",
    color: "#7B2C3F"
  },
  statLbl: {
    fontSize: 11,
    color: "#64748B",
    marginTop: 2
  },
  bmiRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: "#F8FAFC",
    padding: 8,
    borderRadius: 8,
    marginBottom: 8
  },
  bmiText: {
    fontSize: 12,
    color: "#334155"
  },
  bmiBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6
  },
  bmiBadgeText: {
    fontSize: 11,
    fontWeight: "800"
  },
  strategyText: {
    fontSize: 12,
    color: "#334155",
    lineHeight: 18,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: "#F1F5F9"
  },
  formCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: "#E2E8F0"
  },
  formHeader: {
    fontSize: 15,
    fontWeight: "800",
    color: "#0F172A",
    marginBottom: 12
  },
  label: {
    fontSize: 12,
    fontWeight: "700",
    color: "#334155",
    marginBottom: 5,
    marginTop: 4
  },
  pillSelectorRow: {
    flexDirection: "row",
    gap: 8,
    marginBottom: 10
  },
  pillOption: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: "#F1F5F9",
    alignItems: "center"
  },
  pillOptionActive: {
    backgroundColor: "#7B2C3F"
  },
  pillOptionText: {
    fontSize: 12,
    fontWeight: "700",
    color: "#475569"
  },
  pillOptionTextActive: {
    color: "#FFFFFF"
  },
  twoColRow: {
    flexDirection: "row",
    gap: 10
  },
  colHalf: {
    flex: 1
  },
  input: {
    backgroundColor: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#CBD5E1",
    borderRadius: 8,
    padding: 9,
    fontSize: 13,
    color: "#0F172A",
    marginBottom: 10
  },
  goalPillsWrap: {
    gap: 6,
    marginBottom: 10
  },
  goalPill: {
    backgroundColor: "#F1F5F9",
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8
  },
  goalPillActive: {
    backgroundColor: "#10B981"
  },
  goalPillActivePrimary: {
    backgroundColor: "#7B2C3F"
  },
  goalPillText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#475569"
  },
  goalPillTextActive: {
    color: "#FFFFFF",
    fontWeight: "700"
  },
  saveBtn: {
    backgroundColor: "#FF9E1F",
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: "center",
    marginTop: 6
  },
  saveBtnText: {
    color: "#0F172A",
    fontSize: 14,
    fontWeight: "800"
  }
});
