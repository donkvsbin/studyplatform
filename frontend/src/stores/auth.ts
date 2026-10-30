import { defineStore } from "pinia";
import { ref } from "vue";
import { api, ApiError, json, resetCsrf } from "../api";
import { explicitlySelected, i18n, setLocale, type Locale } from "../locales";
export interface User {
  id: number;
  phone: string;
  nickname: string;
  role: "student" | "admin";
  locale: Locale;
}
export const useAuth = defineStore("auth", () => {
  const user = ref<User | null>(null);
  let initialized = false;
  let pending: Promise<void> | null = null;
  async function init() {
    if (initialized) return;
    if (pending) return pending;
    pending = (async () => {
      try {
        user.value = (await api<{ data: User }>("/auth/me")).data;
        if (!explicitlySelected) setLocale(user.value.locale);
        initialized = true;
      } catch (e) {
        if (!(e instanceof ApiError && e.status === 401)) throw e;
        initialized = true;
      } finally {
        pending = null;
      }
    })();
    return pending;
  }
  async function login(phone: string, password: string) {
    user.value = (
      await api<{ data: User }>(
        "/auth/login",
        json("POST", { phone, password }),
      )
    ).data;
    resetCsrf();
    if (explicitlySelected)
      user.value = (
        await api<{ data: User }>(
          "/me",
          json("PATCH", { locale: i18n.global.locale.value }),
        )
      ).data;
    else setLocale(user.value.locale);
  }
  async function logout() {
    try {
      await api("/auth/logout", json("POST"));
    } catch (e) {
      if (!(e instanceof ApiError && e.status === 401)) throw e;
    }
    user.value = null;
    resetCsrf();
  }
  async function switchLocale(value: Locale) {
    setLocale(value, true);
    if (user.value)
      user.value = (
        await api<{ data: User }>("/me", json("PATCH", { locale: value }))
      ).data;
  }
  return { user, init, login, logout, switchLocale };
});
