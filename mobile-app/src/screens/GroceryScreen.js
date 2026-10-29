import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  TextInput,
  Modal,
  Alert,
  RefreshControl
} from "react-native";
import { Colors } from "../theme/colors";
import {
  getDefaultLocalGroceryList,
  fetchGroceryList,
  generateGroceryFromPlan,
  addGroceryItem,
  toggleGroceryItem,
  removeGroceryItem,
  clearCompletedGroceryItems,
  clearAllGroceryItems
} from "../services/api";

const CATEGORIES = ["Vegetables", "Fruits", "Protein", "Grains", "Dairy", "Spices", "Other"];

const CATEGORY_ICONS = {
  Vegetables: "🥦",
  Fruits: "🍎",
  Protein: "🍗",
  Grains: "🌾",
  Dairy: "🥛",
  Spices: "🌶️",
  Other: "📦"
};

export default function GroceryScreen({ userId = null, isActive = false, refreshTrigger = 0, onNavigateToPlanner }) {
  const [grocery, setGrocery] = useState(() => getDefaultLocalGroceryList());
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [compiling, setCompiling] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [newItemName, setNewItemName] = useState("");
  const [newItemCategory, setNewItemCategory] = useState("Protein");

  useEffect(() => {
    loadGroceryList();
  }, [userId, isActive, refreshTrigger]);

  const loadGroceryList = async (isManualRefresh = false) => {
    if (isManualRefresh) setRefreshing(true);
    try {
      const data = await fetchGroceryList(userId);
      if (data?.success && data?.grocery) {
        setGrocery(data.grocery);
      }
    } catch (e) {
      // Keep existing local grocery
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    loadGroceryList(true);
  };

  const handleGenerateFromPlan = async () => {
    setCompiling(true);
    const res = await generateGroceryFromPlan(userId);
    if (res?.success && res?.grocery) {
      setGrocery(res.grocery);
      Alert.alert("Success", res.message || "Compiled grocery list from your meal plan!");
    } else {
      Alert.alert(
        "Meal Plan Required",
        res?.message || "Please create a 7-Day Meal Plan first.",
        [
          { text: "Cancel", style: "cancel" },
          { text: "Go to Planner", onPress: onNavigateToPlanner }
        ]
      );
    }
    setCompiling(false);
  };

  const handleToggleItem = async (itemId) => {
    // Optimistic UI update
    if (!grocery) return;
    const updatedItems = (grocery.items || []).map((it) => {
      if (it.objectId === itemId) {
        return { ...it, checked: !it.checked };
      }
      return it;
    });

    const updatedCategories = {};
    for (const cat of CATEGORIES) {
      updatedCategories[cat] = updatedItems.filter((i) => i.category === cat);
    }

    const completed = updatedItems.filter((i) => i.checked).length;
    setGrocery({
      ...grocery,
      items: updatedItems,
      categories: updatedCategories,
      completed_items: completed
    });

    await toggleGroceryItem(itemId, userId);
  };

  const handleRemoveItem = async (itemId) => {
    const res = await removeGroceryItem(itemId, userId);
    if (res?.success && res?.grocery) {
      setGrocery(res.grocery);
    }
  };

  const handleClearCompleted = async () => {
    const res = await clearCompletedGroceryItems(userId);
    if (res?.success && res?.grocery) {
      setGrocery(res.grocery);
    }
  };

  const handleClearAll = () => {
    Alert.alert(
      "Clear Grocery List",
      "Are you sure you want to remove all items from your grocery list? This action cannot be undone.",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Clear All",
          style: "destructive",
          onPress: async () => {
            const res = await clearAllGroceryItems(userId);
            if (res?.success) {
              setGrocery(res.grocery || {
                total_items: 0,
                completed_items: 0,
                categories: {},
                items: []
              });
            }
          }
        }
      ]
    );
  };

  const handleAddCustomItem = async () => {
    if (!newItemName.trim()) {
      Alert.alert("Error", "Please enter an item name.");
      return;
    }

    const res = await addGroceryItem(userId, newItemName.trim(), newItemCategory);
    if (res?.success && res?.grocery) {
      setGrocery(res.grocery);
      setNewItemName("");
      setModalVisible(false);
    }
  };

  const totalItems = grocery?.total_items || 0;
  const completedItems = grocery?.completed_items || 0;
  const progressPct = totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0;
  const categories = grocery?.categories || {};

  return (
    <View style={styles.container}>
      {/* Top Header */}
      <View style={styles.header}>
        <View style={styles.headerRow}>
          <View>
            <Text style={styles.title}>🛒 Smart Grocery List</Text>
            <Text style={styles.subTitle}>Categorized ingredient checklist from your 7-Day Plan</Text>
          </View>
          <TouchableOpacity
            style={styles.addButton}
            onPress={() => setModalVisible(true)}
          >
            <Text style={styles.addButtonText}>+ Add Item</Text>
          </TouchableOpacity>
        </View>

        {/* Progress Card */}
        {totalItems > 0 && (
          <View style={styles.progressCard}>
            <View style={styles.progressHeader}>
              <Text style={styles.progressText}>
                {completedItems} of {totalItems} items checked ({progressPct}%)
              </Text>
              <Text style={styles.progressPctText}>{progressPct}% Ready</Text>
            </View>
            <View style={styles.progressBarBg}>
              <View style={[styles.progressBarFill, { width: `${progressPct}%` }]} />
            </View>
          </View>
        )}

        {/* Action Buttons Toolbar */}
        <View style={styles.toolbar}>
          <TouchableOpacity
            style={[styles.compileBtn, compiling && styles.btnDisabled]}
            onPress={handleGenerateFromPlan}
            disabled={compiling}
          >
            {compiling ? (
              <ActivityIndicator size="small" color="#FFFFFF" />
            ) : (
              <Text style={styles.compileBtnText}>🪄 Compile from 7-Day Plan</Text>
            )}
          </TouchableOpacity>

          {completedItems > 0 && (
            <TouchableOpacity style={styles.clearBtn} onPress={handleClearCompleted}>
              <Text style={styles.clearBtnText}>🧹 Clear Checked</Text>
            </TouchableOpacity>
          )}

          {totalItems > 0 && (
            <TouchableOpacity style={styles.clearAllBtn} onPress={handleClearAll}>
              <Text style={styles.clearAllBtnText}>🗑️ Clear All</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* Main List Area */}
      {loading ? (
        <View style={styles.loadingBox}>
          <ActivityIndicator size="large" color={Colors.primary} />
          <Text style={styles.loadingText}>Loading grocery list...</Text>
        </View>
      ) : totalItems === 0 ? (
        <ScrollView
          contentContainerStyle={[styles.scrollContent, { flexGrow: 1, justifyContent: "center" }]}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={["#7B2C3F"]} />
          }
        >
          <View style={styles.emptyBox}>
            <Text style={styles.emptyIcon}>🛒</Text>
            <Text style={styles.emptyTitle}>Your Grocery List is Empty</Text>
            <Text style={styles.emptySub}>
              Compile ingredients automatically from your 7-Day Meal Plan or add custom items you need.
            </Text>
            <TouchableOpacity style={styles.emptyActionBtn} onPress={handleGenerateFromPlan}>
              <Text style={styles.emptyActionBtnText}>🪄 Compile from 7-Day Plan</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      ) : (
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={["#7B2C3F"]} />
          }
        >
          {CATEGORIES.map((cat) => {
            const catItems = categories[cat] || [];
            if (catItems.length === 0) return null;

            return (
              <View key={`cat-${cat}`} style={styles.categoryCard}>
                {/* Category Header */}
                <View style={styles.categoryHeader}>
                  <Text style={styles.categoryTitle}>
                    {CATEGORY_ICONS[cat]} {cat}
                  </Text>
                  <View style={styles.categoryBadge}>
                    <Text style={styles.categoryBadgeText}>{catItems.length} items</Text>
                  </View>
                </View>

                {/* Items in this Category */}
                {catItems.map((item) => (
                  <View
                    key={`item-${item.objectId}`}
                    style={[styles.itemRow, Boolean(item.checked) && styles.itemRowChecked]}
                  >
                    <TouchableOpacity
                      style={styles.checkboxContainer}
                      onPress={() => handleToggleItem(item.objectId)}
                    >
                      <View style={[styles.checkbox, Boolean(item.checked) && styles.checkboxActive]}>
                        {Boolean(item.checked) ? <Text style={styles.checkmark}>✓</Text> : null}
                      </View>
                      <View style={styles.itemTextContainer}>
                        <Text style={[styles.itemName, Boolean(item.checked) && styles.itemNameChecked]}>
                          {item.item_name}
                        </Text>
                        {item.recipe_sources && item.recipe_sources.length > 0 && (
                          <Text style={styles.sourceText} numberOfLines={1}>
                            📖 {item.recipe_sources.join(", ")}
                          </Text>
                        )}
                      </View>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={styles.deleteBtn}
                      onPress={() => handleRemoveItem(item.objectId)}
                    >
                      <Text style={styles.deleteBtnText}>✕</Text>
                    </TouchableOpacity>
                  </View>
                ))}
              </View>
            );
          })}
        </ScrollView>
      )}

      {/* Add Custom Item Modal */}
      <Modal visible={modalVisible} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>➕ Add Grocery Item</Text>
            
            <Text style={styles.inputLabel}>Item Name</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g. Sambar Onions, Basmati Rice"
              value={newItemName}
              onChangeText={setNewItemName}
              autoFocus
            />

            <Text style={styles.inputLabel}>Select Category</Text>
            <View style={styles.categoryPickerWrap}>
              {CATEGORIES.map((cat) => (
                <TouchableOpacity
                  key={`pick-${cat}`}
                  style={[
                    styles.pickerChip,
                    newItemCategory === cat && styles.pickerChipActive
                  ]}
                  onPress={() => setNewItemCategory(cat)}
                >
                  <Text
                    style={[
                      styles.pickerChipText,
                      newItemCategory === cat && styles.pickerChipTextActive
                    ]}
                  >
                    {CATEGORY_ICONS[cat]} {cat}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.modalCancelBtn}
                onPress={() => setModalVisible(false)}
              >
                <Text style={styles.modalCancelText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.modalSubmitBtn}
                onPress={handleAddCustomItem}
              >
                <Text style={styles.modalSubmitText}>Add to List</Text>
              </TouchableOpacity>
            </View>
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
  header: {
    backgroundColor: "#FFFFFF",
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#E2E8F0"
  },
  headerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10
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
  addButton: {
    backgroundColor: "#7B2C3F",
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 20
  },
  addButtonText: {
    color: "#FFFFFF",
    fontSize: 12,
    fontWeight: "700"
  },
  progressCard: {
    backgroundColor: "#F8FAFC",
    borderRadius: 10,
    padding: 10,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: "#E2E8F0"
  },
  progressHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 6
  },
  progressText: {
    fontSize: 11,
    color: "#475569",
    fontWeight: "600"
  },
  progressPctText: {
    fontSize: 11,
    color: "#10B981",
    fontWeight: "700"
  },
  progressBarBg: {
    height: 6,
    backgroundColor: "#E2E8F0",
    borderRadius: 3,
    overflow: "hidden"
  },
  progressBarFill: {
    height: "100%",
    backgroundColor: "#10B981",
    borderRadius: 3
  },
  toolbar: {
    flexDirection: "row",
    gap: 8
  },
  compileBtn: {
    flex: 1,
    backgroundColor: "#FF9E1F",
    paddingVertical: 8,
    borderRadius: 8,
    alignItems: "center"
  },
  btnDisabled: {
    opacity: 0.6
  },
  compileBtnText: {
    color: "#1E293B",
    fontSize: 12,
    fontWeight: "700"
  },
  clearBtn: {
    backgroundColor: "#F1F5F9",
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    alignItems: "center"
  },
  clearBtnText: {
    color: "#64748B",
    fontSize: 12,
    fontWeight: "600"
  },
  clearAllBtn: {
    backgroundColor: "#FEE2E2",
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    alignItems: "center"
  },
  clearAllBtnText: {
    color: "#DC2626",
    fontSize: 12,
    fontWeight: "700"
  },
  scrollContent: {
    padding: 14,
    paddingBottom: 40
  },
  categoryCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 14,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    marginBottom: 14,
    overflow: "hidden"
  },
  categoryHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 10,
    paddingHorizontal: 14,
    backgroundColor: "#F8FAFC",
    borderBottomWidth: 1,
    borderBottomColor: "#E2E8F0"
  },
  categoryTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: "#1E293B"
  },
  categoryBadge: {
    backgroundColor: "#E2E8F0",
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10
  },
  categoryBadgeText: {
    fontSize: 10,
    color: "#475569",
    fontWeight: "600"
  },
  itemRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderBottomWidth: 1,
    borderBottomColor: "#F1F5F9"
  },
  itemRowChecked: {
    backgroundColor: "#FAFAFA",
    opacity: 0.6
  },
  checkboxContainer: {
    flexDirection: "row",
    alignItems: "center",
    flex: 1
  },
  checkbox: {
    width: 20,
    height: 20,
    borderRadius: 5,
    borderWidth: 2,
    borderColor: "#CBD5E1",
    marginRight: 10,
    alignItems: "center",
    justifyContent: "center"
  },
  checkboxActive: {
    backgroundColor: "#7B2C3F",
    borderColor: "#7B2C3F"
  },
  checkmark: {
    color: "#FFFFFF",
    fontSize: 12,
    fontWeight: "800"
  },
  itemTextContainer: {
    flex: 1
  },
  itemName: {
    fontSize: 13,
    fontWeight: "600",
    color: "#1E293B"
  },
  itemNameChecked: {
    textDecorationLine: "line-through",
    color: "#94A3B8"
  },
  sourceText: {
    fontSize: 10,
    color: "#94A3B8",
    marginTop: 2
  },
  deleteBtn: {
    padding: 6
  },
  deleteBtnText: {
    color: "#CBD5E1",
    fontSize: 14,
    fontWeight: "700"
  },
  loadingBox: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center"
  },
  loadingText: {
    marginTop: 10,
    color: "#64748B",
    fontSize: 13
  },
  emptyBox: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 30
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 12
  },
  emptyTitle: {
    fontSize: 17,
    fontWeight: "700",
    color: "#1E293B",
    marginBottom: 6
  },
  emptySub: {
    fontSize: 13,
    color: "#64748B",
    textAlign: "center",
    lineHeight: 18,
    marginBottom: 18
  },
  emptyActionBtn: {
    backgroundColor: "#FF9E1F",
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 25
  },
  emptyActionBtnText: {
    color: "#1E293B",
    fontSize: 13,
    fontWeight: "700"
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
    padding: 20,
    paddingBottom: 35
  },
  modalTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#1E293B",
    marginBottom: 14
  },
  inputLabel: {
    fontSize: 12,
    fontWeight: "600",
    color: "#475569",
    marginBottom: 6
  },
  input: {
    backgroundColor: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#E2E8F0",
    borderRadius: 8,
    padding: 10,
    fontSize: 13,
    marginBottom: 14
  },
  categoryPickerWrap: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
    marginBottom: 20
  },
  pickerChip: {
    backgroundColor: "#F1F5F9",
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 16
  },
  pickerChipActive: {
    backgroundColor: "#7B2C3F"
  },
  pickerChipText: {
    fontSize: 11,
    color: "#475569",
    fontWeight: "600"
  },
  pickerChipTextActive: {
    color: "#FFFFFF"
  },
  modalActions: {
    flexDirection: "row",
    gap: 10
  },
  modalCancelBtn: {
    flex: 1,
    backgroundColor: "#F1F5F9",
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: "center"
  },
  modalCancelText: {
    color: "#64748B",
    fontSize: 13,
    fontWeight: "600"
  },
  modalSubmitBtn: {
    flex: 1,
    backgroundColor: "#7B2C3F",
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: "center"
  },
  modalSubmitText: {
    color: "#FFFFFF",
    fontSize: 13,
    fontWeight: "700"
  }
});
