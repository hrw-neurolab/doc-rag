import type { Tokens, TokensWithUser, User } from "@/types/api";
import { defineStore } from "pinia";
import { ref } from "vue";

export const useSessionStore = defineStore("session", () => {
  const user = ref<User | null>(null);
  const tokens = ref<Tokens | null>(null);

  const restoreSession = () => {
    const storedValue = localStorage.getItem("session");

    if (storedValue === null) {
      return;
    }

    const { user: storedUser, ...storedTokens } = JSON.parse(storedValue) as TokensWithUser;
    user.value = storedUser;
    tokens.value = storedTokens;
  };

  const storeSession = (tokensWithUser: TokensWithUser) => {
    user.value = tokensWithUser.user;

    tokens.value = {
      access_token: tokensWithUser.access_token,
      refresh_token: tokensWithUser.refresh_token,
    };

    localStorage.setItem("session", JSON.stringify(tokensWithUser));
  };

  const clearSession = () => {
    user.value = null;
    tokens.value = null;
    localStorage.removeItem("session");
  };

  return { user, tokens, restoreSession, storeSession, clearSession };
});
