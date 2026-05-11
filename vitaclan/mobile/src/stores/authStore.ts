import { create } from "zustand";
import * as SecureStore from "expo-secure-store";
import { apiClient } from "../api/client";

interface AuthState {
  userId: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  sendOtp: (phone: string) => Promise<void>;
  verifyOtp: (phone: string, code: string, name?: string) => Promise<void>;
  logout: () => Promise<void>;
  hydrate: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  userId: null,
  isAuthenticated: false,
  isLoading: true,

  hydrate: async () => {
    const token = await SecureStore.getItemAsync("access_token");
    const userId = await SecureStore.getItemAsync("user_id");
    set({ isAuthenticated: !!token, userId, isLoading: false });
  },

  sendOtp: async (phone: string) => {
    await apiClient.post("/auth/send-otp", { phone, consent_given: true });
  },

  verifyOtp: async (phone: string, code: string, name?: string) => {
    const { data } = await apiClient.post("/auth/verify-otp", { phone, code, name });
    await SecureStore.setItemAsync("access_token", data.access_token);
    await SecureStore.setItemAsync("user_id", data.user_id);
    set({ isAuthenticated: true, userId: data.user_id });
  },

  logout: async () => {
    await SecureStore.deleteItemAsync("access_token");
    await SecureStore.deleteItemAsync("user_id");
    set({ isAuthenticated: false, userId: null });
  },
}));
