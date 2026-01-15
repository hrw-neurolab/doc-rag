<script setup lang="ts">
import MessageList from "@/components/resource-chat/MessageList.vue";
import type { AssistantMessage, Message } from "@/types/resource-chat";
import { onMounted, reactive, ref } from "vue";
import MessageInput from "./MessageInput.vue";
import { useApi } from "@/api/use-api";
import routes from "@/api/routes";
import type { ResourceChatBody } from "@/types/api";
import { getMongoId } from "@/util/text-parsing";
import { useResourceStore } from "@/stores/resource-store";
import WelcomeScreen from "./WelcomeScreen.vue";
import { storeToRefs } from "pinia";
import type { Chunk } from "@/types/api";
import { useSessionStore } from "@/stores/session-store";

const messages = reactive<Message[]>([]);

const { post: clearChat } = useApi(routes.chat.post.clear);
const { post: sendMessage, loading } = useApi(routes.chat.post.sendMessage);

const resourceStore = useResourceStore();
const { selectedResourceIds } = storeToRefs(resourceStore);
const streaming = ref(false);

const messageList = ref();

const BASE_URL = import.meta.env.VITE_API_URL

const streamToMessage = async (stream: ReadableStream) => {
  const reader = stream.getReader();
  const decoder = new TextDecoder();

  streaming.value = true;
  while (streaming.value) {
    const { value, done } = await reader.read();

    streaming.value = !done;
    if (value === undefined) continue;

    const chunk = decoder.decode(value, { stream: true });

    const message = messages[messages.length - 1] as AssistantMessage;
    const newText = message.content.text + chunk;

    const id = getMongoId(newText);
    if (!id) {
      message.content.text = newText;
      continue;
    }

    const index = message.content.citations.indexOf(id);
    if (index !== -1) {
      message.content.text = newText.replace(id, (index + 1).toString());
      continue;
    }

    const newLength = message.content.citations.push(id);
    message.content.text = newText.replace(id, newLength.toString());
  }
};

const handleSubmit = async (text: string) => {
  messages.push({ role: "user", content: text });
  messages.push({ role: "assistant", content: { text: "", citations: [] } });

  await messageList.value?.scrollToBottom();

  const response = await sendMessage<ReadableStream, ResourceChatBody>({
    data: { query: text, recource_ids: Array.from(selectedResourceIds.value) },
    config: { responseType: "stream", adapter: "fetch" },
  });

  if (!response) return;
  await streamToMessage(response.data);
};


function formatAsPlainText(msgs: Message[]): string {
  const parts: string[] = [];
  for (const m of msgs) {
    if (m.role === "user") {
      parts.push(`User: ${m.content}`);
    } else {
      parts.push(`Assistant: ${m.content.text}`);
      if (m.content.citations?.length) {
        parts.push(`References: ${m.content.citations.join(", ")}`);
      }
    }
  }
  return parts.join("\n\n");
}

function truncate(text: string, max = 300): string {
  if (text.length <= max) return text;
  return text.slice(0, max - 1) + "…";
}

function formatAsPlainTextWithReferences(
  msgs: Message[],
  citationDetails: Map<string, { title: string; page?: number; content: string }>
): string {
  const parts: string[] = [];
  for (const m of msgs) {
    if (m.role === "user") {
      parts.push(`User:\n${m.content}`);
    } else {
      parts.push(`Assistant:\n${m.content.text}`);

      const ids = m.content.citations ?? [];
      if (ids.length > 0) {
        parts.push(`\nReferences`);
        ids.forEach((id, idx) => {
          const num = idx + 1;
          const d = citationDetails.get(id);
          if (!d) {
            parts.push(`[${num}] (unavailable)`);
            return;
          }
          const pageSuffix = typeof d.page === "number" ? ` — Page ${d.page}` : "";
          parts.push(`[${num}] ${d.title}${pageSuffix}`);
          parts.push(`Excerpt: "${truncate(d.content)}"`);
        });
      }
    }
    parts.push(""); // blank line between messages
  }
  return parts.join("\n");
}

function downloadFile(filename: string, content: string, mime: string) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

async function fetchChunkSilently<T>(urlPath: string): Promise<T | null> {
  try {
    const sessionStore = useSessionStore();
    const token = sessionStore.tokens?.access_token;
    const res = await fetch(`${BASE_URL}${urlPath}`, {
      method: "GET",
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

async function handleExport() {
  const ts = new Date().toISOString().replace(/[:.]/g, "-");

  const allIds = messages
    .filter((m) => m.role !== "user")
    .flatMap((m: any) => m.content?.citations ?? []);

  const citationDetails = await resolveCitationsForExport(allIds);

  const txt = formatAsPlainTextWithReferences(messages, citationDetails);
  downloadFile(`chat-${ts}.txt`, txt, "text/plain;charset=utf-8");
}

async function resolveCitationsForExport(allCitationIds: string[]) {
  const { resources, fetchedChunks } = storeToRefs(useResourceStore());

  const uniqueIds = Array.from(new Set(allCitationIds));
  const detailsById = new Map<string, { title: string; page?: number; content: string }>();

  for (const id of uniqueIds) {
    let chunk = fetchedChunks.value.find((c) => c._id === id) as Chunk | undefined;

    if (!chunk) {
      // use the same route builder used elsewhere, but fetch silently
      const path = routes.resources.get.getChunk(id);
      const data = await fetchChunkSilently<Chunk>(path);
      if (!data) continue;
      chunk = data;
      fetchedChunks.value.push(chunk);
    }

    const title = resources.value.find((r) => r._id === chunk.resource)?.title ?? "Untitled";
    // @ts-expect-error: page_number exists for PDF chunks
    const page = (chunk as any).page_number as number | undefined;

    detailsById.set(id, { title, page, content: chunk.content });
  }

  return detailsById;
}

onMounted(async () => clearChat({ data: undefined }));
</script>

<template>
  <Transition name="slide-up" mode="out-in">
    <MessageList
      v-if="messages.length > 0"
      :ref="(el) => (messageList = el)"
      :messages="messages"
    />
    <WelcomeScreen v-else />
  </Transition>
  <!-- <MessageInput
    :disabled="streaming || loading || resourceStore.selectedResourceIds.size === 0"
    @submit="handleSubmit"
  /> -->
  <MessageInput
    :disabled="streaming || loading || resourceStore.selectedResourceIds.size === 0"
    :can-export="messages.length > 0 && !streaming && !loading"
    @export="handleExport"
    @submit="handleSubmit"
  />
</template>

<style scoped>
.slide-up-enter-active,
.slide-up-leave-active {
  transition:
    transform 0.25s ease,
    opacity 0.25s ease;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}
</style>
