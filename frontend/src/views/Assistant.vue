<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import {
  Sparkles,
  Send,
  Plus,
  ArrowUpRight,
  Unplug,
  BookOpen,
  MessageCircle,
  UserRound,
} from "lucide-vue-next";
import { api, json } from "../api";
import { useAuth } from "../stores/auth";
import type { Course } from "../types";
import UiError from "../components/UiError.vue";
import MarkdownText from "../components/MarkdownText.vue";
const { t, locale } = useI18n(),
  route = useRoute(),
  auth = useAuth();
interface Message {
  role: "user" | "assistant";
  content: string;
}
const messages = ref<Message[]>([]),
  question = ref(""),
  busy = ref(false),
  checking = ref(true),
  configured = ref(false),
  error = ref<unknown>(null),
  course = ref<Course | null>(null),
  contextLost = ref(false),
  list = ref<HTMLElement | null>(null);
const ready = computed(
    () => !!auth.user && configured.value && !checking.value,
  ),
  full = computed(() => messages.value.length >= 20);
let sequence = 0;
let conversationVersion = 0;
async function check() {
  const id = ++sequence;
  checking.value = true;
  error.value = null;
  try {
    const status = await api<{ data: { configured: boolean } }>(
      "/assistant/status",
    );
    if (id !== sequence) return;
    configured.value = status.data.configured;
    course.value = null;
    contextLost.value = false;
    if (route.query.course) {
      try {
        const result = await api<{ data: Course }>(
          `/courses/${encodeURIComponent(String(route.query.course))}`,
        );
        if (id === sequence) course.value = result.data;
      } catch {
        if (id === sequence) contextLost.value = true;
      }
    }
  } catch (e) {
    if (id === sequence) error.value = e;
  } finally {
    if (id === sequence) checking.value = false;
  }
}
async function send() {
  if (!ready.value || busy.value || full.value || !question.value.trim())
    return;
  const text = question.value.trim();
  const version = conversationVersion;
  busy.value = true;
  error.value = null;
  const requestMessages: Message[] = [
    ...messages.value,
    { role: "user", content: text },
  ];
  try {
    const result = await api<{ data: { answer: string } }>(
      "/assistant/chat",
      json("POST", {
        messages: requestMessages,
        ...(course.value ? { course_id: course.value.id } : {}),
      }),
    );
    if (version !== conversationVersion) return;
    messages.value = [
      ...requestMessages,
      { role: "assistant", content: result.data.answer },
    ];
    question.value = "";
    await nextTick();
    list.value?.scrollTo({ top: list.value.scrollHeight, behavior: "smooth" });
  } catch (e) {
    if (version === conversationVersion) error.value = e;
  } finally {
    busy.value = false;
  }
}
function clear() {
  conversationVersion++;
  messages.value = [];
  error.value = null;
  question.value = "";
}
watch([() => route.query.course, locale], check, { immediate: true });
watch(() => route.query.course, clear);
watch(() => auth.user?.id, clear);
</script>
<template>
  <div class="container page assistant-page">
    <div class="assistant-heading">
      <div>
        <span class="section-kicker">A LITTLE HELP ALONG THE WAY</span>
        <h1>{{ t("ai.title") }} <Sparkles :size="29" /></h1>
        <p class="page-subtitle">{{ t("ai.subtitle") }}</p>
      </div>
      <span class="powered"><span></span>{{ t("ai.powered") }}</span>
    </div>
    <div class="assistant-shell">
      <aside class="chat-sidebar">
        <div class="buddy-icon"><Sparkles :size="27" /></div>
        <h3>{{ t("ai.title") }}</h3>
        <p>{{ t("ai.welcomeSub") }}</p>
        <button
          class="button button-outline wide"
          @click="clear"
          :disabled="busy"
        >
          <Plus :size="16" />{{ t("ai.clear") }}
        </button>
        <div class="chat-context">
          <span>{{ t("ai.context") }}</span
          ><strong
            ><BookOpen :size="16" />{{
              course?.title || t("ai.general")
            }}</strong
          >
          <p v-if="contextLost">{{ t("ai.courseUnavailable") }}</p>
        </div>
        <small>{{ t("ai.limit") }}</small>
      </aside>
      <section class="chat-main">
        <div ref="list" class="chat-scroll">
          <div v-if="!messages.length" class="chat-welcome">
            <span class="welcome-icon"
              ><MessageCircle :size="32" :stroke-width="1.5"
            /></span>
            <h2>{{ t("ai.welcome") }}</h2>
            <p>{{ t("ai.welcomeSub") }}</p>
            <div class="prompt-list">
              <button
                v-for="n in 3"
                :key="n"
                @click="question = t(`ai.prompt${n}`)"
                :disabled="busy"
              >
                {{ t(`ai.prompt${n}`) }}<ArrowUpRight :size="15" />
              </button>
            </div>
          </div>
          <div v-else class="messages" aria-live="polite">
            <article
              v-for="(message, index) in messages"
              :key="index"
              :class="['message', message.role]"
            >
              <span class="message-icon"
                ><UserRound
                  v-if="message.role === 'user'"
                  :size="17" /><Sparkles v-else :size="17"
              /></span>
              <div>
                <strong>{{
                  t(message.role === "user" ? "ai.you" : "ai.assistant")
                }}</strong
                ><MarkdownText :text="message.content" />
              </div>
            </article>
          </div>
          <p v-if="busy" role="status" class="thinking">
            <Sparkles :size="16" />{{ t("ai.sending") }}
          </p>
        </div>
        <div class="chat-compose">
          <UiError :error="error" /><button
            v-if="error && !configured"
            class="text-link clear-button"
            @click="check"
          >
            {{ t("common.retry") }}
          </button>
          <p v-if="checking" class="chat-status" role="status">
            {{ t("common.loading") }}
          </p>
          <div v-else-if="!auth.user" class="chat-notice">
            <UserRound :size="22" />
            <div>
              <strong>{{ t("ai.login") }}</strong>
              <p>{{ t("ai.loginSub") }}</p>
              <RouterLink
                :to="{ path: '/login', query: { redirect: route.fullPath } }"
                class="text-link"
                >{{ t("nav.login") }}<ArrowUpRight :size="14"
              /></RouterLink>
            </div>
          </div>
          <div v-else-if="!configured" class="chat-notice">
            <Unplug :size="22" />
            <div>
              <strong>{{ t("ai.disabled") }}</strong>
              <p>{{ t("ai.disabledSub") }}</p>
            </div>
          </div>
          <p v-if="full" class="success-box">{{ t("ai.full") }}</p>
          <form class="chat-input" @submit.prevent="send">
            <label class="sr-only" for="question">{{
              t("ai.inputLabel")
            }}</label
            ><textarea
              id="question"
              v-model="question"
              rows="2"
              maxlength="2000"
              :placeholder="t('ai.placeholder')"
              :disabled="!ready || busy || full"
              @keydown.enter.exact.prevent="send"
            ></textarea
            ><button
              class="send-button"
              :disabled="!ready || busy || full || !question.trim()"
              :aria-label="t('ai.send')"
            >
              <Send :size="19" /></button
            ><span class="character-count">{{ question.length }} / 2000</span>
          </form>
          <p class="chat-disclaimer">{{ t("ai.disclaimer") }}</p>
        </div>
      </section>
    </div>
  </div>
</template>
