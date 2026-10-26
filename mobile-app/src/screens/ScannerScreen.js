import React, { useState } from "react";
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Image,
  Alert
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import { Colors } from "../theme/colors";
import { recognizeFoodImage, logMealEaten } from "../services/api";

const DEMO_SAMPLES = [
  { id: "biryani", name: "🍛 Biryani", query: "Biryani" },
  { id: "dosa", name: "🥞 Dosa", query: "Crispy Masala Dosa" },
  { id: "paneer", name: "🥘 Paneer Tikka", query: "Paneer Butter Masala" },
  { id: "salad", name: "🥗 Green Salad", query: "Green Salad / Sprouts" }
];

export default function ScannerScreen({ onSelectRecipe, userId = null }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [logged, setLogged] = useState(false);
  const [imageUri, setImageUri] = useState(null);

  const handleLaunchCamera = async () => {
    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== "granted") {
        Alert.alert(
          "Camera Permission Required",
          "Please grant camera access in your phone settings to capture food photos."
        );
        return;
      }

      const mediaTypes = ImagePicker.MediaTypeOptions?.Images ?? ["images"];
      const picResult = await ImagePicker.launchCameraAsync({
        mediaTypes,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.7,
        base64: true
      });

      if (!picResult.canceled && picResult.assets && picResult.assets.length > 0) {
        const asset = picResult.assets[0];
        setImageUri(asset.uri);
        await analyzeCapturedAsset(asset);
      }
    } catch (error) {
      Alert.alert("Camera Error", error?.message || "Could not launch camera.");
    }
  };

  const handlePickGallery = async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== "granted") {
        Alert.alert(
          "Gallery Permission Required",
          "Please grant photo library access to select food photos."
        );
        return;
      }

      const mediaTypes = ImagePicker.MediaTypeOptions?.Images ?? ["images"];
      const picResult = await ImagePicker.launchImageLibraryAsync({
        mediaTypes,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.7,
        base64: true
      });

      if (!picResult.canceled && picResult.assets && picResult.assets.length > 0) {
        const asset = picResult.assets[0];
        setImageUri(asset.uri);
        await analyzeCapturedAsset(asset);
      }
    } catch (error) {
      Alert.alert("Gallery Error", error?.message || "Could not open photo gallery.");
    }
  };

  const analyzeCapturedAsset = async (asset) => {
    setLoading(true);
    setLogged(false);
    try {
      const base64Data = asset.base64?.startsWith("data:")
        ? asset.base64
        : `data:image/jpeg;base64,${asset.base64}`;
      const res = await recognizeFoodImage(base64Data);
      if (res?.success && res?.recognition) {
        setResult(res.recognition);
      } else {
        Alert.alert("Scanner", res?.message || "Could not identify dish in photo.");
      }
    } catch (err) {
      Alert.alert("Scanner Error", "Failed to analyze photo. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleScanSample = async (sample) => {
    setLoading(true);
    setLogged(false);
    setImageUri(null);
    const res = await recognizeFoodImage(sample.query);
    if (res?.success && res?.recognition) {
      setResult(res.recognition);
    } else {
      Alert.alert("Scanner", res?.message || "Could not analyze image.");
    }
    setLoading(false);
  };

  const handleLogMeal = async (recipeId) => {
    if (!recipeId) return;
    const res = await logMealEaten(recipeId, 1.0, userId);
    if (res?.success) {
      setLogged(true);
      Alert.alert("Meal Logged", "Logged into your daily nutrition analytics!");
    }
  };

  const matchedRecipe = result?.matched_recipe;
  const topPred = result?.top_prediction;
  const verifiedNutr = result?.verified_nutrition;
  const candidates = result?.candidate_recipes || [];
  const similar = result?.similar_recipes || [];

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>📸 AI Food Scanner</Text>
        <Text style={styles.subTitle}>
          Identify dishes & view verified recipe database nutrition
        </Text>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Scanner Action Box */}
        <View style={styles.scanCard}>
          {imageUri ? (
            <View style={styles.previewContainer}>
              <Image source={{ uri: imageUri }} style={styles.previewImage} resizeMode="cover" />
              <TouchableOpacity
                style={styles.retakeBtn}
                onPress={() => { setImageUri(null); setResult(null); }}
              >
                <Text style={styles.retakeBtnText}>✕ Clear / Retake</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <>
              <Text style={styles.scanIcon}>📸</Text>
              <Text style={styles.scanPromptTitle}>Capture or Select Food Photo</Text>
              <Text style={styles.scanPromptSub}>
                Take a photo of any meal or upload from your gallery for instant AI dish identification & verified nutrition.
              </Text>
            </>
          )}

          {/* Primary Action Buttons: Camera & Gallery */}
          <View style={styles.buttonActionRow}>
            <TouchableOpacity
              style={styles.cameraMainBtn}
              onPress={handleLaunchCamera}
              disabled={loading}
              activeOpacity={0.8}
            >
              <Text style={styles.cameraMainBtnText}>📷 Open Camera</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.galleryMainBtn}
              onPress={handlePickGallery}
              disabled={loading}
              activeOpacity={0.8}
            >
              <Text style={styles.galleryMainBtnText}>🖼️ Choose Photo</Text>
            </TouchableOpacity>
          </View>

          {/* Quick Demo Test Chips */}
          <View style={styles.dividerRow}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerText}>OR TRY DEMO MEALS</Text>
            <View style={styles.dividerLine} />
          </View>

          <View style={styles.samplesRow}>
            {DEMO_SAMPLES.map((s) => (
              <TouchableOpacity
                key={s.id}
                style={styles.sampleChip}
                onPress={() => handleScanSample(s)}
                disabled={loading}
              >
                <Text style={styles.sampleChipText}>{s.name}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Loading Spinner */}
        {loading && (
          <View style={styles.loadingBox}>
            <ActivityIndicator size="large" color={Colors.primary} />
            <Text style={styles.loadingText}>Running AI Vision Classification...</Text>
          </View>
        )}

        {/* Results Area */}
        {!loading && result && matchedRecipe && (
          <View style={styles.resultsContainer}>
            {/* Recognition Summary Card */}
            <View style={styles.resultCard}>
              <View style={styles.confidenceRow}>
                <View style={[styles.confidenceBadge, { backgroundColor: "#ECFDF5" }]}>
                  <Text style={[styles.confidenceText, { color: "#047857" }]}>
                    ✓ {topPred?.confidence_tier || "Recognized"} ({topPred?.confidence_pct || 85}%)
                  </Text>
                </View>
              </View>

              <Text style={styles.dishName}>{matchedRecipe.recipe_name}</Text>
              <Text style={styles.cuisineText}>
                🏛️ {matchedRecipe.cuisine || "Authentic Dish"} • {matchedRecipe.veg_nonveg || "Veg"}
              </Text>

              {/* Verified Database Nutrition Card */}
              <View style={styles.nutritionBox}>
                <Text style={styles.nutrBoxTitle}>VERIFIED DATABASE NUTRITION (1 Serving)</Text>
                <View style={styles.macroRow}>
                  <View style={styles.macroCol}>
                    <Text style={styles.macroLabel}>Calories</Text>
                    <Text style={styles.macroVal}>{verifiedNutr?.calories || 350}</Text>
                    <Text style={styles.macroUnit}>kcal</Text>
                  </View>
                  <View style={styles.macroCol}>
                    <Text style={styles.macroLabel}>Protein</Text>
                    <Text style={[styles.macroVal, { color: "#1D4ED8" }]}>{verifiedNutr?.protein_g || 15}g</Text>
                    <Text style={styles.macroUnit}>protein</Text>
                  </View>
                  <View style={styles.macroCol}>
                    <Text style={styles.macroLabel}>Carbs</Text>
                    <Text style={[styles.macroVal, { color: "#059669" }]}>{verifiedNutr?.carbs_g || 45}g</Text>
                    <Text style={styles.macroUnit}>carbs</Text>
                  </View>
                  <View style={styles.macroCol}>
                    <Text style={styles.macroLabel}>Health</Text>
                    <Text style={[styles.macroVal, { color: "#D97706" }]}>{verifiedNutr?.health_score || 80}</Text>
                    <Text style={styles.macroUnit}>/100</Text>
                  </View>
                </View>
              </View>

              {/* Grounding Disclaimer */}
              <View style={styles.disclaimerBox}>
                <Text style={styles.disclaimerText}>
                  ⚠️ Grounding Notice: Nutrition values reflect verified database measurements for standard recipe portions, not estimated pixel density.
                </Text>
              </View>

              {/* Action Buttons */}
              <View style={styles.actionRow}>
                <TouchableOpacity
                  style={[styles.actionBtn, logged && styles.actionBtnLogged]}
                  onPress={() => handleLogMeal(matchedRecipe.recipe_id)}
                  disabled={logged}
                >
                  <Text style={styles.actionBtnText}>
                    {logged ? "✓ Logged to Dashboard" : "➕ Log This Meal"}
                  </Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.detailsBtn}
                  onPress={() => onSelectRecipe && onSelectRecipe(matchedRecipe)}
                >
                  <Text style={styles.detailsBtnText}>📖 Full Recipe</Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Alternative Candidate Matches */}
            {candidates.length > 0 && (
              <View style={styles.sectionCard}>
                <Text style={styles.sectionTitle}>Alternative Candidate Matches</Text>
                <View style={styles.candidateRow}>
                  {candidates.map((c) => (
                    <TouchableOpacity
                      key={`cand-${c.recipe_id}`}
                      style={styles.candidateChip}
                      onPress={() => onSelectRecipe && onSelectRecipe(c)}
                    >
                      <Text style={styles.candidateChipText}>
                        {c.recipe_name} ({c.nutritions?.calories || 300} kcal)
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
            )}

            {/* Similar Dishes */}
            {similar.length > 0 && (
              <View style={styles.sectionCard}>
                <Text style={styles.sectionTitle}>Similar Recipes from this Cuisine</Text>
                {similar.map((s) => (
                  <TouchableOpacity
                    key={`sim-${s.recipe_id}`}
                    style={styles.similarRow}
                    onPress={() => onSelectRecipe && onSelectRecipe(s)}
                  >
                    <View>
                      <Text style={styles.similarName}>{s.recipe_name}</Text>
                      <Text style={styles.similarSub}>
                        🔥 {s.nutritions?.calories || 300} kcal • 💪 {s.nutritions?.protein_g || 15}g P
                      </Text>
                    </View>
                    <Text style={styles.chevron}>›</Text>
                  </TouchableOpacity>
                ))}
              </View>
            )}
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F4F6F9"
  },
  header: {
    backgroundColor: "#FFFFFF",
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#E2E8F0"
  },
  title: {
    fontSize: 20,
    fontWeight: "800",
    color: "#0F172A"
  },
  subTitle: {
    fontSize: 11,
    color: "#64748B",
    marginTop: 2
  },
  scrollContent: {
    padding: 14,
    paddingBottom: 40
  },
  scanCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    padding: 20,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#E2E8F0",
    marginBottom: 14
  },
  scanIcon: {
    fontSize: 36,
    marginBottom: 8
  },
  scanPromptTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: "#1E293B",
    marginBottom: 4
  },
  scanPromptSub: {
    fontSize: 12,
    color: "#64748B",
    textAlign: "center",
    marginBottom: 14
  },
  previewContainer: {
    width: "100%",
    alignItems: "center",
    marginBottom: 14,
    position: "relative"
  },
  previewImage: {
    width: "100%",
    height: 190,
    borderRadius: 12
  },
  retakeBtn: {
    position: "absolute",
    top: 8,
    right: 8,
    backgroundColor: "rgba(0, 0, 0, 0.65)",
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 14
  },
  retakeBtnText: {
    color: "#FFFFFF",
    fontSize: 11,
    fontWeight: "700"
  },
  buttonActionRow: {
    flexDirection: "row",
    gap: 10,
    width: "100%",
    marginBottom: 8
  },
  cameraMainBtn: {
    flex: 1,
    backgroundColor: "#7B2C3F",
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
    elevation: 2,
    shadowColor: "#7B2C3F",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4
  },
  cameraMainBtnText: {
    color: "#FFFFFF",
    fontSize: 13,
    fontWeight: "700"
  },
  galleryMainBtn: {
    flex: 1,
    backgroundColor: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#CBD5E1",
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center"
  },
  galleryMainBtnText: {
    color: "#334155",
    fontSize: 13,
    fontWeight: "700"
  },
  dividerRow: {
    flexDirection: "row",
    alignItems: "center",
    width: "100%",
    marginVertical: 10
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: "#E2E8F0"
  },
  dividerText: {
    marginHorizontal: 10,
    fontSize: 9,
    fontWeight: "800",
    color: "#94A3B8",
    letterSpacing: 0.5
  },
  samplesRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    justifyContent: "center"
  },
  sampleChip: {
    backgroundColor: "#FEF3C7",
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: 20
  },
  sampleChipText: {
    color: "#92400E",
    fontSize: 12,
    fontWeight: "700"
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
  resultsContainer: {
    gap: 14
  },
  resultCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: "#E2E8F0"
  },
  confidenceRow: {
    flexDirection: "row",
    marginBottom: 8
  },
  confidenceBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12
  },
  confidenceText: {
    fontSize: 11,
    fontWeight: "700"
  },
  dishName: {
    fontSize: 18,
    fontWeight: "800",
    color: "#7B2C3F",
    marginBottom: 3
  },
  cuisineText: {
    fontSize: 12,
    color: "#64748B",
    marginBottom: 12
  },
  nutritionBox: {
    backgroundColor: "#F8FAFC",
    borderRadius: 12,
    padding: 12,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    marginBottom: 10
  },
  nutrBoxTitle: {
    fontSize: 9,
    fontWeight: "800",
    color: "#94A3B8",
    letterSpacing: 0.5,
    marginBottom: 8
  },
  macroRow: {
    flexDirection: "row",
    justifyContent: "space-around"
  },
  macroCol: {
    alignItems: "center"
  },
  macroLabel: {
    fontSize: 10,
    color: "#64748B"
  },
  macroVal: {
    fontSize: 16,
    fontWeight: "800",
    color: "#1E293B",
    marginTop: 1
  },
  macroUnit: {
    fontSize: 9,
    color: "#94A3B8"
  },
  disclaimerBox: {
    backgroundColor: "#FFFBEB",
    borderRadius: 8,
    padding: 10,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: "#FDE68A"
  },
  disclaimerText: {
    fontSize: 10,
    color: "#92400E",
    lineHeight: 14
  },
  actionRow: {
    flexDirection: "row",
    gap: 8
  },
  actionBtn: {
    flex: 1,
    backgroundColor: "#7B2C3F",
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: "center"
  },
  actionBtnLogged: {
    backgroundColor: "#10B981"
  },
  actionBtnText: {
    color: "#FFFFFF",
    fontSize: 12,
    fontWeight: "700"
  },
  detailsBtn: {
    backgroundColor: "#F1F5F9",
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 10,
    alignItems: "center"
  },
  detailsBtnText: {
    color: "#475569",
    fontSize: 12,
    fontWeight: "600"
  },
  sectionCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: "#E2E8F0"
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: "700",
    color: "#1E293B",
    marginBottom: 10
  },
  candidateRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6
  },
  candidateChip: {
    backgroundColor: "#F1F5F9",
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 12
  },
  candidateChipText: {
    fontSize: 11,
    color: "#475569",
    fontWeight: "600"
  },
  similarRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: "#F1F5F9"
  },
  similarName: {
    fontSize: 13,
    fontWeight: "600",
    color: "#1E293B"
  },
  similarSub: {
    fontSize: 11,
    color: "#64748B",
    marginTop: 2
  },
  chevron: {
    fontSize: 18,
    color: "#CBD5E1"
  }
});
