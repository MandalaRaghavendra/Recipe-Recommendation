// authStorage.js - Secure token and user session persistence using Expo SecureStore
import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

const TOKEN_KEY = 'tastio_auth_token';
const USER_KEY = 'tastio_auth_user';

// In-memory fallback for web, node, or test environments where native keystore is unavailable
const memoryStore = new Map();

/**
 * Persists Bearer authentication token in Expo SecureStore (hardware-backed Keystore/Keychain).
 */
export async function saveAuthToken(token) {
  if (!token) return;
  const tokenStr = String(token).trim();
  try {
    if (Platform.OS !== 'web' && SecureStore && SecureStore.setItemAsync) {
      await SecureStore.setItemAsync(TOKEN_KEY, tokenStr);
    } else {
      memoryStore.set(TOKEN_KEY, tokenStr);
    }
  } catch (err) {
    memoryStore.set(TOKEN_KEY, tokenStr);
  }
}

/**
 * Retrieves the stored Bearer token from SecureStore.
 */
export async function getStoredAuthToken() {
  try {
    if (Platform.OS !== 'web' && SecureStore && SecureStore.getItemAsync) {
      const val = await SecureStore.getItemAsync(TOKEN_KEY);
      if (val) return val;
    }
    return memoryStore.get(TOKEN_KEY) || null;
  } catch (err) {
    return memoryStore.get(TOKEN_KEY) || null;
  }
}

/**
 * Deletes the Bearer token from SecureStore.
 */
export async function removeAuthToken() {
  try {
    if (Platform.OS !== 'web' && SecureStore && SecureStore.deleteItemAsync) {
      await SecureStore.deleteItemAsync(TOKEN_KEY);
    }
  } catch (err) {}
  memoryStore.delete(TOKEN_KEY);
}

/**
 * Persists the user profile (id, name, email) in SecureStore.
 * IMPORTANT: Passwords are NEVER persisted in local storage or SecureStore!
 */
export async function saveStoredUser(user) {
  if (!user) return;
  const sanitized = {
    objectId: String(user.objectId || user.id || "1"),
    name: String(user.name || "Chef"),
    email: String(user.email || "")
  };
  const jsonStr = JSON.stringify(sanitized);
  try {
    if (Platform.OS !== 'web' && SecureStore && SecureStore.setItemAsync) {
      await SecureStore.setItemAsync(USER_KEY, jsonStr);
    } else {
      memoryStore.set(USER_KEY, jsonStr);
    }
  } catch (err) {
    memoryStore.set(USER_KEY, jsonStr);
  }
}

/**
 * Retrieves the persisted user profile from SecureStore.
 */
export async function getStoredUser() {
  try {
    let jsonStr = null;
    if (Platform.OS !== 'web' && SecureStore && SecureStore.getItemAsync) {
      jsonStr = await SecureStore.getItemAsync(USER_KEY);
    }
    if (!jsonStr) {
      jsonStr = memoryStore.get(USER_KEY);
    }
    return jsonStr ? JSON.parse(jsonStr) : null;
  } catch (err) {
    return null;
  }
}

/**
 * Clears both token and user profile upon logout.
 */
export async function clearAuthSession() {
  await removeAuthToken();
  try {
    if (Platform.OS !== 'web' && SecureStore && SecureStore.deleteItemAsync) {
      await SecureStore.deleteItemAsync(USER_KEY);
    }
  } catch (err) {}
  memoryStore.delete(USER_KEY);
}

