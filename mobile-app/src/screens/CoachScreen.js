import React, { useState, useEffect, useRef } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  Image,
  StyleSheet,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Alert
} from "react-native";
import { Colors } from "../theme/colors";
import { chatWithCoach, fetchCoachContext, markRecipeEaten } from "../services/api";

const QUICK_PROMPTS = [
  "🍽️ What should I eat for dinner?",
  "🌱 High protein vegetarian meal",
  "🥘 I have chicken and rice. What can I cook?",
  "📊 How many calories did I eat today?",
  "💪 Reach my protein target",
  "🥗 Recipes below 500 calories",
  "📅 What did I eat this week?",
  "🔬 What is my BMR and TDEE?"
];

export default function CoachScreen({ onSelectRecipe, userId = null }) {
  const [messages, setMessages] = useState([
    {
      id: "init-1",
      sender: "bot",
      text: "👋 **Hello! I am your Tastio AI Nutrition Coach.**\n\nI have access to your personal metabolic baseline, dietary preferences, and logged meals. How can I help you reach your goals today?",
      recipes: []
    }
  ]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const flatListRef = useRef(null);

  useEffect(() => {
    loadContext();
  }, [userId]);

  const loadContext = async () => {
    const data = await fetchCoachContext(userId);
    if (data.success && data.metrics) {
      setMetrics(data.metrics);
    }
  };

  const handleSend = async (customText = null) => {
    const textToSend = (customText || inputText).trim();
    if (!textToSend || loading) return;

    const userMsg = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: textToSend,
      recipes: []
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!customText) setInputText("");
    setLoading(true);

    // Call Coach API
    const res = await chatWithCoach(textToSend, userId);
    setLoading(false);

    if (res.success) {
      const botMsg = {
        id: `bot-${Date.now()}`,
        sender: "bot",
        text: res.reply || "Here are recommendations based on your profile:",
        recipes: res.recipes || []
      };
      setMessages((prev) => [...prev, botMsg]);
      if (res.metrics) {
        setMetrics(res.metrics);
      }
    } else {
      const errorMsg = {
        id: `bot-err-${Date.now()}`,
        sender: "bot",
        text: res.reply || "⚠️ Unable to fetch advice. Please try again.",
        recipes: []
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  const handleLogMeal = async (recipe) => {
    try {
      const res = await markRecipeEaten(null, recipe.recipe_id, 1.0);
      Alert.alert("Meal Logged", `✅ "${recipe.recipe_name}" has been logged to your daily intake!`);
      loadContext();
    } catch (e) {
      Alert.alert("Meal Logged", `Logged "${recipe.recipe_name}"!`);
    }
  };

  const renderRecipeItem = (recipe) => {
    const isVeg = (recipe.veg_nonveg || "Veg").toLowerCase() === "veg";
    return (
      <View key={String(recipe.recipe_id)} style={styles.recipeCard}>
        <Image
          source={{ uri: recipe.image_link || "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500" }}
          style={styles.recipeImage}
          resizeMode="cover"
        />
        <View style={styles.recipeContent}>
          <View style={styles.cardHeaderRow}>
            <View style={[styles.vegBadge, { backgroundColor: isVeg ? "#E8F5E9" : "#FFEBEE" }]}>
              <Text style={[styles.vegBadgeText, { color: isVeg ? Colors.veg : Colors.nonVeg }]}>
                {isVeg ? "🌱 Veg" : "🍗 Non-Veg"}
              </Text>
            </View>
            <View style={styles.healthBadge}>
              <Text style={styles.healthText}>★ {recipe.health_score || 80}/100</Text>
            </View>
          </View>

          <Text style={styles.recipeTitle} numberOfLines={2}>{recipe.recipe_name}</Text>

          {/* Nutrients Badges */}
          <View style={styles.nutriRow}>
            <View style={[styles.nutriPill, { backgroundColor: "#FEF3C7" }]}>
              <Text style={[styles.nutriText, { color: "#92400E" }]}>🔥 {recipe.calories} kcal</Text>
            </View>
            <View style={[styles.nutriPill, { backgroundColor: "#E0E7FF" }]}>
              <Text style={[styles.nutriText, { color: "#3730A3" }]}>💪 {recipe.protein}</Text>
            </View>
            <View style={[styles.nutriPill, { backgroundColor: "#F1F5F9" }]}>
              <Text style={[styles.nutriText, { color: "#475569" }]}>⏱️ {recipe.prep_time}</Text>
            </View>
          </View>

          {/* AI Reason */}
          {recipe.reason ? (
            <View style={styles.reasonBox}>
              <Text style={styles.reasonText} numberOfLines={3}>💡 {recipe.reason}</Text>
            </View>
          ) : null}

          {/* Action Buttons */}
          <View style={styles.actionBtnRow}>
            <TouchableOpacity
              style={styles.btnView}
              onPress={() => onSelectRecipe && onSelectRecipe(recipe)}
            >
              <Text style={styles.btnViewText}>📖 View Recipe</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.btnLog}
              onPress={() => handleLogMeal(recipe)}
            >
              <Text style={styles.btnLogText}>✅ Log Meal</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    );
  };

  const renderMessage = ({ item }) => {
    const isUser = item.sender === "user";
    return (
      <View style={[styles.msgRow, isUser ? styles.msgRowUser : styles.msgRowBot]}>
        {!isUser && (
          <View style={styles.botAvatar}>
            <Text style={{ fontSize: 16 }}>🤖</Text>
          </View>
        )}
        <View style={[styles.bubble, isUser ? styles.bubbleUser : styles.bubbleBot]}>
          <Text style={[styles.msgText, isUser ? styles.msgTextUser : styles.msgTextBot]}>
            {item.text.replace(/\*\*/g, "").replace(/\*/g, "")}
          </Text>

          {/* Render embedded recipes if present */}
          {item.recipes && item.recipes.length > 0 && (
            <View style={styles.recipeListContainer}>
              {item.recipes.map((r) => renderRecipeItem(r))}
            </View>
          )}
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Vitality Summary Bar */}
      {metrics && (
        <View style={styles.metricsBar}>
          <View style={styles.metricsCol}>
            <Text style={styles.metricVal}>{metrics.remaining_calories || 0}</Text>
            <Text style={styles.metricLbl}>kcal left</Text>
          </View>
          <View style={styles.metricsCol}>
            <Text style={styles.metricVal}>{metrics.consumed_calories || 0}/{metrics.target_calories || 1800}</Text>
            <Text style={styles.metricLbl}>Calories</Text>
          </View>
          <View style={styles.metricsCol}>
            <Text style={styles.metricVal}>{metrics.consumed_protein || 0}g</Text>
            <Text style={styles.metricLbl}>Protein</Text>
          </View>
          <View style={styles.metricsCol}>
            <Text style={[styles.metricVal, { color: Colors.accent }]}>
              {metrics.diet_goal ? metrics.diet_goal.replace("_", " ") : "Goal"}
            </Text>
            <Text style={styles.metricLbl}>Plan</Text>
          </View>
        </View>
      )}

      {/* Chat Messages */}
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={(item) => item.id}
          renderItem={renderMessage}
          contentContainerStyle={styles.chatListContent}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
        />

        {/* Typing Indicator */}
        {loading && (
          <View style={styles.loadingRow}>
            <ActivityIndicator size="small" color={Colors.primary} />
            <Text style={styles.loadingText}>Tastio AI Coach analyzing targets...</Text>
          </View>
        )}

        {/* Quick Suggestion Chips */}
        <View style={styles.chipsScrollWrapper}>
          <FlatList
            horizontal
            showsHorizontalScrollIndicator={false}
            data={QUICK_PROMPTS}
            keyExtractor={(item, idx) => `chip-${idx}`}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={styles.chip}
                onPress={() => handleSend(item.replace(/^[^\w]+/, "").trim())}
              >
                <Text style={styles.chipText}>{item}</Text>
              </TouchableOpacity>
            )}
            contentContainerStyle={{ paddingHorizontal: 12 }}
          />
        </View>

        {/* Input Bar */}
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            placeholder="Ask AI Coach (e.g. 'Dinner under 400 cal')..."
            placeholderTextColor="#94A3B8"
            value={inputText}
            onChangeText={setInputText}
            onSubmitEditing={() => handleSend()}
            returnKeyType="send"
          />
          <TouchableOpacity
            style={[styles.sendBtn, !inputText.trim() && { opacity: 0.6 }]}
            onPress={() => handleSend()}
            disabled={loading || !inputText.trim()}
          >
            <Text style={styles.sendBtnText}>➤</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F4F6F9"
  },
  metricsBar: {
    flexDirection: "row",
    backgroundColor: "#7B2C3F",
    paddingVertical: 10,
    paddingHorizontal: 16,
    justifyContent: "space-between",
    alignItems: "center",
    borderBottomWidth: 1,
    borderBottomColor: "rgba(255,255,255,0.1)"
  },
  metricsCol: {
    alignItems: "center"
  },
  metricVal: {
    color: "#FFD180",
    fontWeight: "700",
    fontSize: 13
  },
  metricLbl: {
    color: "rgba(255,255,255,0.75)",
    fontSize: 10,
    fontWeight: "600",
    textTransform: "uppercase"
  },
  chatListContent: {
    padding: 14,
    paddingBottom: 20
  },
  msgRow: {
    flexDirection: "row",
    marginBottom: 16,
    alignItems: "flex-end"
  },
  msgRowUser: {
    justifyContent: "flex-end"
  },
  msgRowBot: {
    justifyContent: "flex-start"
  },
  botAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: "#7B2C3F",
    alignItems: "center",
    justifyContent: "center",
    marginRight: 8,
    marginBottom: 2
  },
  bubble: {
    borderRadius: 16,
    padding: 14,
    maxWidth: "84%"
  },
  bubbleUser: {
    backgroundColor: "#7B2C3F",
    borderBottomRightRadius: 2
  },
  bubbleBot: {
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#E2E8F0",
    borderBottomLeftRadius: 2
  },
  msgText: {
    fontSize: 14,
    lineHeight: 20
  },
  msgTextUser: {
    color: "#FFFFFF"
  },
  msgTextBot: {
    color: "#1E293B"
  },
  recipeListContainer: {
    marginTop: 12
  },
  recipeCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    marginBottom: 12,
    overflow: "hidden"
  },
  recipeImage: {
    width: "100%",
    height: 120
  },
  recipeContent: {
    padding: 10
  },
  cardHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 6
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
  healthBadge: {
    backgroundColor: "#DCFCE7",
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4
  },
  healthText: {
    color: "#166534",
    fontSize: 10,
    fontWeight: "700"
  },
  recipeTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: "#0F172A",
    marginBottom: 6
  },
  nutriRow: {
    flexDirection: "row",
    gap: 4,
    marginBottom: 6
  },
  nutriPill: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4
  },
  nutriText: {
    fontSize: 10,
    fontWeight: "700"
  },
  reasonBox: {
    backgroundColor: "#FFFBEB",
    borderLeftWidth: 3,
    borderLeftColor: "#F59E0B",
    padding: 6,
    borderRadius: 4,
    marginBottom: 8
  },
  reasonText: {
    fontSize: 11,
    color: "#78350F",
    lineHeight: 14
  },
  actionBtnRow: {
    flexDirection: "row",
    gap: 8
  },
  btnView: {
    flex: 1,
    backgroundColor: "#F1F5F9",
    paddingVertical: 6,
    borderRadius: 6,
    alignItems: "center"
  },
  btnViewText: {
    fontSize: 11,
    fontWeight: "600",
    color: "#334155"
  },
  btnLog: {
    flex: 1,
    backgroundColor: Colors.accent,
    paddingVertical: 6,
    borderRadius: 6,
    alignItems: "center"
  },
  btnLogText: {
    fontSize: 11,
    fontWeight: "700",
    color: "#FFFFFF"
  },
  loadingRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 8,
    gap: 8
  },
  loadingText: {
    fontSize: 12,
    color: Colors.textMuted,
    fontStyle: "italic"
  },
  chipsScrollWrapper: {
    paddingVertical: 6,
    backgroundColor: "#FFFFFF",
    borderTopWidth: 1,
    borderTopColor: "#E2E8F0"
  },
  chip: {
    backgroundColor: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#E2E8F0",
    borderRadius: 16,
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginRight: 6
  },
  chipText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#334155"
  },
  inputContainer: {
    flexDirection: "row",
    padding: 10,
    backgroundColor: "#FFFFFF",
    borderTopWidth: 1,
    borderTopColor: "#E2E8F0",
    alignItems: "center"
  },
  input: {
    flex: 1,
    backgroundColor: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#CBD5E1",
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    fontSize: 13,
    color: "#1E293B"
  },
  sendBtn: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: "#7B2C3F",
    alignItems: "center",
    justifyContent: "center",
    marginLeft: 8
  },
  sendBtnText: {
    color: "#FFFFFF",
    fontSize: 15,
    fontWeight: "bold"
  }
});
