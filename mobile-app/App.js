import React, { useState, useEffect } from "react";
import {
  StyleSheet,
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  Modal,
  TextInput,
  ActivityIndicator,
  Alert,
  Platform,
  StatusBar as RNStatusBar
} from "react-native";
import { StatusBar } from "expo-status-bar";
import { Colors } from "./src/theme/colors";
import HomeScreen from "./src/screens/HomeScreen";
import SearchScreen from "./src/screens/SearchScreen";
import MealPlanScreen from "./src/screens/MealPlanScreen";
import GroceryScreen from "./src/screens/GroceryScreen";
import ScannerScreen from "./src/screens/ScannerScreen";
import HistoryScreen from "./src/screens/HistoryScreen";
import ProfileScreen from "./src/screens/ProfileScreen";
import CoachScreen from "./src/screens/CoachScreen";
import RecipeDetailModal from "./src/screens/RecipeDetailModal";
import {
  apiLogin,
  apiSignup,
  getApiBaseUrl,
  setCustomHostIp,
  getDevHostIp,
  DEV_HOST_IP
} from "./src/services/api";

const TABS = [
  { id: "home", label: "Home", icon: "🏠" },
  { id: "search", label: "Search", icon: "🔍" },
  { id: "scanner", label: "Scan", icon: "📸" },
  { id: "planner", label: "Plan", icon: "📅" },
  { id: "grocery", label: "Grocery", icon: "🛒" },
  { id: "coach", label: "Coach", icon: "🤖" },
  { id: "history", label: "History", icon: "📊" },
  { id: "profile", label: "Profile", icon: "👤" }
];

export default function App() {
  const [currentTab, setCurrentTab] = useState("home");
  const [visitedTabs, setVisitedTabs] = useState({ home: true });

  const switchTab = (tabId) => {
    setCurrentTab(tabId);
    setVisitedTabs((prev) => (prev[tabId] ? prev : { ...prev, [tabId]: true }));
  };
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);

  // Authentication State
  const [currentUser, setCurrentUser] = useState({
    objectId: "1",
    name: "Demo Chef",
    email: "demo@tastio.ai"
  });
  const [authModalVisible, setAuthModalVisible] = useState(false);
  const [authMode, setAuthMode] = useState("login"); // 'login' | 'signup'
  const [authName, setAuthName] = useState("");
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authLoading, setAuthLoading] = useState(false);

  // Server Host Config State
  const [serverModalVisible, setServerModalVisible] = useState(false);
  const [customHost, setCustomHost] = useState(DEV_HOST_IP);
  const [serverStatus, setServerStatus] = useState("Checking...");
  const [testingConnection, setTestingConnection] = useState(false);

  const userId = currentUser?.objectId || currentUser?.id || null;

  useEffect(() => {
    checkServerHealth();
  }, []);

  const checkServerHealth = async () => {
    try {
      const url = `${getApiBaseUrl()}/health`;
      const res = await fetch(url);
      if (res.ok) {
        setServerStatus("Online (Connected)");
      } else {
        setServerStatus("Offline (Local Cache Active)");
      }
    } catch (e) {
      setServerStatus("Offline (Local Cache Active)");
    }
  };

  const handleTestConnection = async () => {
    setTestingConnection(true);
    try {
      const targetBase = customHost.startsWith("http")
        ? (customHost.endsWith("/api") ? customHost : `${customHost}/api`)
        : `http://${customHost}:5000/api`;
      const res = await fetch(`${targetBase}/health`);
      if (res.ok) {
        setServerStatus("Online (Connected)");
        Alert.alert("Connection Successful! ✅", `Successfully connected to Tastio backend at:\n${targetBase}`);
      } else {
        setServerStatus("Server Error");
        Alert.alert("Server Responded with Error", `HTTP ${res.status}. Please check your backend terminal.`);
      }
    } catch (e) {
      setServerStatus("Offline");
      Alert.alert(
        "Connection Failed ❌",
        `Could not connect to ${customHost}:5000.\n\nMake sure:\n1. 'python app.py' is running in the backend folder.\n2. Your phone and laptop are on the same Wi-Fi.\n3. The IP address matches your computer's Wi-Fi IPv4.`
      );
    }
    setTestingConnection(false);
  };

  const handleSaveHost = () => {
    if (customHost.trim()) {
      setCustomHostIp(customHost.trim());
      setServerModalVisible(false);
      checkServerHealth();
      Alert.alert("Host Saved", `API endpoint set to: ${getApiBaseUrl()}`);
    }
  };

  const handleSelectRecipe = (recipe) => {
    setSelectedRecipe(recipe);
    setModalVisible(true);
  };

  const handleCloseModal = () => {
    setModalVisible(false);
    setSelectedRecipe(null);
  };

  const handleAuthSubmit = async () => {
    const cleanEmail = authEmail.trim();
    const cleanPassword = authPassword.trim();
    const cleanName = authName.trim();

    if (!cleanEmail || !cleanPassword) {
      Alert.alert("Input Required", "Please enter both your email and password.");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(cleanEmail)) {
      Alert.alert("Invalid Email", "Please enter a valid email address (e.g., name@example.com).");
      return;
    }

    if (cleanPassword.length < 4) {
      Alert.alert("Password Too Short", "Password must be at least 4 characters long.");
      return;
    }

    if (authMode === "signup" && !cleanName) {
      Alert.alert("Name Required", "Please enter your full name to register.");
      return;
    }

    setAuthLoading(true);
    let res;
    if (authMode === "signup") {
      res = await apiSignup(cleanName, cleanEmail, cleanPassword);
    } else {
      res = await apiLogin(cleanEmail, cleanPassword);
    }
    setAuthLoading(false);

    if (res && res.success && res.user) {
      setCurrentUser(res.user);
      setAuthModalVisible(false);
      setAuthPassword("");
      Alert.alert(
        "Welcome! 🎉",
        authMode === "signup"
          ? `Welcome to Tastio, ${res.user.name || "Chef"}! Your profile is ready.`
          : `Welcome back, ${res.user.name || "Chef"}!`
      );
    } else {
      Alert.alert(
        authMode === "signup" ? "Registration Failed" : "Login Failed",
        res?.message || "Invalid credentials. Please verify your details."
      );
    }
  };

  const handleSignOut = () => {
    setCurrentUser(null);
    setAuthModalVisible(false);
    Alert.alert("Signed Out", "You are now using Tastio in Guest mode.");
  };

  return (
    <View style={[styles.container, styles.safeTop]}>
      <StatusBar style="dark" />

      {/* Top Floating Server Indicator Bar */}
      <View style={styles.statusBarRow}>
        <TouchableOpacity
          style={styles.serverPill}
          onPress={() => setServerModalVisible(true)}
          activeOpacity={0.8}
        >
          <View style={[styles.statusDot, { backgroundColor: serverStatus.includes("Online") ? "#22C55E" : "#F59E0B" }]} />
          <Text style={styles.serverPillText} numberOfLines={1}>
            {serverStatus.includes("Online") ? `API: ${getDevHostIp()}` : `Cache: ${getDevHostIp()}`}
          </Text>
          <Text style={styles.serverPillConfigIcon}>⚙️</Text>
        </TouchableOpacity>
      </View>

      {/* Main Screen View Container */}
      <View style={styles.screenContainer}>
        {visitedTabs.home && (
          <View style={[styles.tabContent, currentTab !== "home" && styles.hiddenTab]}>
            <HomeScreen
              onSelectRecipe={handleSelectRecipe}
              currentUser={currentUser}
              onOpenAuth={() => setAuthModalVisible(true)}
            />
          </View>
        )}
        {visitedTabs.search && (
          <View style={[styles.tabContent, currentTab !== "search" && styles.hiddenTab]}>
            <SearchScreen
              onSelectRecipe={handleSelectRecipe}
              userId={userId}
            />
          </View>
        )}
        {visitedTabs.scanner && (
          <View style={[styles.tabContent, currentTab !== "scanner" && styles.hiddenTab]}>
            <ScannerScreen
              onSelectRecipe={handleSelectRecipe}
              userId={userId}
            />
          </View>
        )}
        {visitedTabs.planner && (
          <View style={[styles.tabContent, currentTab !== "planner" && styles.hiddenTab]}>
            <MealPlanScreen
              onSelectRecipe={handleSelectRecipe}
              userId={userId}
            />
          </View>
        )}
        {visitedTabs.grocery && (
          <View style={[styles.tabContent, currentTab !== "grocery" && styles.hiddenTab]}>
            <GroceryScreen
              userId={userId}
              onNavigateToPlanner={() => switchTab("planner")}
            />
          </View>
        )}
        {visitedTabs.coach && (
          <View style={[styles.tabContent, currentTab !== "coach" && styles.hiddenTab]}>
            <CoachScreen
              onSelectRecipe={handleSelectRecipe}
              userId={userId}
            />
          </View>
        )}
        {visitedTabs.history && (
          <View style={[styles.tabContent, currentTab !== "history" && styles.hiddenTab]}>
            <HistoryScreen
              onSelectRecipe={handleSelectRecipe}
              userId={userId}
            />
          </View>
        )}
        {visitedTabs.profile && (
          <View style={[styles.tabContent, currentTab !== "profile" && styles.hiddenTab]}>
            <ProfileScreen
              currentUser={currentUser}
              onOpenAuth={() => setAuthModalVisible(true)}
              onNavigateToHistory={() => switchTab("history")}
              onNavigateToPlanner={() => switchTab("planner")}
            />
          </View>
        )}
      </View>

      {/* Bottom Navigation Tab Bar */}
      <View style={styles.bottomBarWrap}>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.bottomBarScroll}
        >
          {TABS.map((tab) => {
            const isActive = currentTab === tab.id;
            return (
              <TouchableOpacity
                key={tab.id}
                style={[styles.tabItem, isActive && styles.tabItemActive]}
                onPress={() => switchTab(tab.id)}
              >
                <Text style={[styles.tabIcon, isActive && styles.tabIconActive]}>
                  {tab.icon}
                </Text>
                <Text style={[styles.tabLabel, isActive && styles.tabLabelActive]}>
                  {tab.label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      </View>

      {/* Recipe Detail Full Modal */}
      {Boolean(modalVisible && selectedRecipe) && (
        <RecipeDetailModal
          visible={modalVisible}
          recipe={selectedRecipe}
          userId={userId}
          onClose={handleCloseModal}
        />
      )}

      {/* Server Connection Config Modal */}
      <Modal
        visible={serverModalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setServerModalVisible(false)}
      >
        <View style={styles.authModalOverlay}>
          <View style={styles.authCard}>
            <View style={styles.authHeader}>
              <Text style={styles.authTitle}>🌐 Server & API Settings</Text>
              <TouchableOpacity onPress={() => setServerModalVisible(false)}>
                <Text style={styles.authClose}>✕</Text>
              </TouchableOpacity>
            </View>

            <Text style={styles.serverModalInfo}>
              Tastio connects your mobile phone to the Python backend running on your computer.
            </Text>

            <View style={styles.statusBox}>
              <Text style={styles.statusBoxLabel}>Current Connection:</Text>
              <Text style={[styles.statusBoxValue, { color: serverStatus.includes("Online") ? "#15803D" : "#B45309" }]}>
                {serverStatus}
              </Text>
              <Text style={styles.currentUrlText}>{getApiBaseUrl()}</Text>
            </View>

            <Text style={styles.authInputLabel}>Host IP / URL:</Text>
            <TextInput
              style={styles.authInput}
              value={customHost}
              onChangeText={setCustomHost}
              placeholder="e.g. 10.231.101.150 or localhost"
              placeholderTextColor="#94A3B8"
              autoCapitalize="none"
              autoCorrect={false}
            />

            {/* Quick Presets */}
            <View style={styles.presetsRow}>
              <TouchableOpacity
                style={styles.presetChip}
                onPress={() => setCustomHost(DEV_HOST_IP)}
              >
                <Text style={styles.presetChipText}>📡 Wi-Fi IP ({DEV_HOST_IP})</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.presetChip}
                onPress={() => setCustomHost("localhost")}
              >
                <Text style={styles.presetChipText}>💻 Localhost (Web)</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.presetChip}
                onPress={() => setCustomHost("127.0.0.1")}
              >
                <Text style={styles.presetChipText}>🔌 USB (127.0.0.1)</Text>
              </TouchableOpacity>
            </View>

            <View style={styles.serverActionsRow}>
              <TouchableOpacity
                style={[styles.btnTestConn, testingConnection && styles.btnDisabled]}
                onPress={handleTestConnection}
                disabled={testingConnection}
              >
                {testingConnection ? (
                  <ActivityIndicator size="small" color="#7B2C3F" />
                ) : (
                  <Text style={styles.btnTestConnText}>🔍 Test Connection</Text>
                )}
              </TouchableOpacity>

              <TouchableOpacity style={styles.btnSaveHost} onPress={handleSaveHost}>
                <Text style={styles.btnSaveHostText}>💾 Save & Apply</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Authentication / User Account Modal */}
      <Modal
        visible={authModalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setAuthModalVisible(false)}
      >
        <View style={styles.authModalOverlay}>
          <View style={styles.authCard}>
            <View style={styles.authHeader}>
              <Text style={styles.authTitle}>
                {currentUser ? "👤 User Account" : authMode === "login" ? "🔑 Welcome Back" : "✨ Create Account"}
              </Text>
              <TouchableOpacity onPress={() => setAuthModalVisible(false)}>
                <Text style={styles.authClose}>✕</Text>
              </TouchableOpacity>
            </View>

            {currentUser ? (
              <View style={styles.accountCard}>
                <View style={styles.avatarCircle}>
                  <Text style={styles.avatarInitial}>
                    {(currentUser.name || "U").charAt(0).toUpperCase()}
                  </Text>
                </View>
                <Text style={styles.accountName}>{currentUser.name || "Chef"}</Text>
                <Text style={styles.accountEmail}>{currentUser.email || "No email"}</Text>
                <TouchableOpacity style={styles.signOutBtn} onPress={handleSignOut}>
                  <Text style={styles.signOutText}>🚪 Sign Out</Text>
                </TouchableOpacity>
              </View>
            ) : (
              <View>
                <View style={styles.authTabs}>
                  <TouchableOpacity
                    style={[styles.authTabBtn, authMode === "login" && styles.authTabBtnActive]}
                    onPress={() => setAuthMode("login")}
                  >
                    <Text style={[styles.authTabText, authMode === "login" && styles.authTabTextActive]}>
                      Sign In
                    </Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.authTabBtn, authMode === "signup" && styles.authTabBtnActive]}
                    onPress={() => setAuthMode("signup")}
                  >
                    <Text style={[styles.authTabText, authMode === "signup" && styles.authTabTextActive]}>
                      Register
                    </Text>
                  </TouchableOpacity>
                </View>

                {authMode === "signup" && (
                  <View>
                    <Text style={styles.authInputLabel}>Full Name</Text>
                    <TextInput
                      style={styles.authInput}
                      placeholder="Chef Name"
                      value={authName}
                      onChangeText={setAuthName}
                    />
                  </View>
                )}

                <Text style={styles.authInputLabel}>Email Address</Text>
                <TextInput
                  style={styles.authInput}
                  placeholder="chef@tastio.ai"
                  keyboardType="email-address"
                  autoCapitalize="none"
                  value={authEmail}
                  onChangeText={setAuthEmail}
                />

                <Text style={styles.authInputLabel}>Password</Text>
                <TextInput
                  style={styles.authInput}
                  placeholder="••••••••"
                  secureTextEntry={true}
                  value={authPassword}
                  onChangeText={setAuthPassword}
                />
                <Text style={{ fontSize: 11, color: "#64748B", marginTop: 4, marginBottom: 8 }}>
                  Minimum 4 characters
                </Text>

                <TouchableOpacity
                  style={styles.authSubmitBtn}
                  onPress={handleAuthSubmit}
                  disabled={authLoading}
                >
                  {authLoading ? (
                    <ActivityIndicator size="small" color="#FFFFFF" />
                  ) : (
                    <Text style={styles.authSubmitText}>
                      {authMode === "login" ? "Sign In to Tastio" : "Create Account"}
                    </Text>
                  )}
                </TouchableOpacity>
              </View>
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
    backgroundColor: "#F8FAFC"
  },
  safeTop: {
    paddingTop: Platform.OS === "android" ? (RNStatusBar.currentHeight || 28) : 0
  },
  statusBarRow: {
    paddingHorizontal: 12,
    paddingTop: 4,
    paddingBottom: 4,
    backgroundColor: "#FFFFFF",
    borderBottomWidth: 1,
    borderBottomColor: "#F1F5F9",
    flexDirection: "row",
    justifyContent: "flex-end"
  },
  serverPill: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#F1F5F9",
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 20
  },
  statusDot: {
    width: 7,
    height: 7,
    borderRadius: 4,
    marginRight: 6
  },
  serverPillText: {
    fontSize: 11,
    fontWeight: "600",
    color: "#475569"
  },
  serverPillConfigIcon: {
    fontSize: 10,
    marginLeft: 6
  },
  screenContainer: {
    flex: 1
  },
  tabContent: {
    flex: 1
  },
  hiddenTab: {
    display: "none"
  },
  bottomBarWrap: {
    backgroundColor: "#FFFFFF",
    borderTopWidth: 1,
    borderTopColor: "#E2E8F0",
    paddingBottom: 4
  },
  bottomBarScroll: {
    flexDirection: "row",
    paddingHorizontal: 4,
    paddingVertical: 4
  },
  tabItem: {
    alignItems: "center",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    marginHorizontal: 2
  },
  tabItemActive: {
    backgroundColor: "#FFF1F2"
  },
  tabIcon: {
    fontSize: 18,
    marginBottom: 2
  },
  tabIconActive: {
    transform: [{ scale: 1.15 }]
  },
  tabLabel: {
    fontSize: 11,
    color: "#64748B",
    fontWeight: "600"
  },
  tabLabelActive: {
    color: "#7B2C3F",
    fontWeight: "800"
  },
  authModalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.5)",
    justifyContent: "center",
    alignItems: "center",
    padding: 20
  },
  authCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 20,
    padding: 22,
    width: "100%",
    maxWidth: 420
  },
  authHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 14
  },
  authTitle: {
    fontSize: 17,
    fontWeight: "800",
    color: "#0F172A"
  },
  authClose: {
    fontSize: 20,
    color: "#64748B",
    padding: 4
  },
  serverModalInfo: {
    fontSize: 12,
    color: "#64748B",
    lineHeight: 17,
    marginBottom: 12
  },
  statusBox: {
    backgroundColor: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#E2E8F0",
    borderRadius: 10,
    padding: 10,
    marginBottom: 14
  },
  statusBoxLabel: {
    fontSize: 11,
    color: "#64748B",
    fontWeight: "600"
  },
  statusBoxValue: {
    fontSize: 13,
    fontWeight: "700",
    marginTop: 2
  },
  currentUrlText: {
    fontSize: 11,
    color: "#94A3B8",
    marginTop: 2
  },
  presetsRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
    marginBottom: 16
  },
  presetChip: {
    backgroundColor: "#F1F5F9",
    paddingHorizontal: 8,
    paddingVertical: 5,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: "#E2E8F0"
  },
  presetChipText: {
    fontSize: 11,
    color: "#334155",
    fontWeight: "600"
  },
  serverActionsRow: {
    flexDirection: "row",
    gap: 10
  },
  btnTestConn: {
    flex: 1,
    backgroundColor: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#CBD5E1",
    paddingVertical: 11,
    borderRadius: 10,
    alignItems: "center"
  },
  btnTestConnText: {
    fontSize: 13,
    fontWeight: "700",
    color: "#334155"
  },
  btnSaveHost: {
    flex: 1,
    backgroundColor: "#7B2C3F",
    paddingVertical: 11,
    borderRadius: 10,
    alignItems: "center"
  },
  btnSaveHostText: {
    fontSize: 13,
    fontWeight: "800",
    color: "#FFFFFF"
  },
  btnDisabled: {
    opacity: 0.6
  },
  accountCard: {
    alignItems: "center",
    paddingVertical: 16
  },
  avatarCircle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: "#7B2C3F",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 12
  },
  avatarInitial: {
    fontSize: 24,
    color: "#FFFFFF",
    fontWeight: "800"
  },
  accountName: {
    fontSize: 18,
    fontWeight: "700",
    color: "#0F172A"
  },
  accountEmail: {
    fontSize: 13,
    color: "#64748B",
    marginTop: 4
  },
  signOutBtn: {
    marginTop: 20,
    backgroundColor: "#FEE2E2",
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 10
  },
  signOutText: {
    color: "#DC2626",
    fontWeight: "700"
  },
  authTabs: {
    flexDirection: "row",
    backgroundColor: "#F1F5F9",
    borderRadius: 10,
    padding: 3,
    marginBottom: 14
  },
  authTabBtn: {
    flex: 1,
    paddingVertical: 8,
    alignItems: "center",
    borderRadius: 8
  },
  authTabBtnActive: {
    backgroundColor: "#7B2C3F"
  },
  authTabText: {
    fontSize: 13,
    fontWeight: "600",
    color: "#64748B"
  },
  authTabTextActive: {
    color: "#FFFFFF",
    fontWeight: "700"
  },
  authInputLabel: {
    fontSize: 12,
    fontWeight: "700",
    color: "#334155",
    marginBottom: 4,
    marginTop: 6
  },
  authInput: {
    backgroundColor: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#CBD5E1",
    borderRadius: 8,
    padding: 10,
    fontSize: 13,
    color: "#0F172A",
    marginBottom: 8
  },
  authSubmitBtn: {
    backgroundColor: "#7B2C3F",
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: "center",
    marginTop: 10
  },
  authSubmitText: {
    color: "#FFFFFF",
    fontSize: 14,
    fontWeight: "800"
  }
});
