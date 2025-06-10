<script setup lang="ts">
import type { Message } from "@/types/resource-chat";
import AssistantCitation from "@/components/resource-chat/AssistantCitation.vue";
import { ProgressSpinner, Divider } from "primevue";
import VueMarkdown from "vue-markdown-render";
import { nextTick, useTemplateRef } from "vue";

const { messages } = defineProps<{ messages: Message[] }>();

const container = useTemplateRef("container");

const scrollToBottom = async () => {
  console.log("Scrolling to bottom");

  const el = container.value;
  if (!el) return;
  await nextTick();
  el.scroll({
    top: el.scrollHeight,
    behavior: "smooth",
  });
};

defineExpose({ scrollToBottom });
</script>

<template>
  <div ref="container" class="message-list">
    <div
      v-for="(m, i) in messages"
      :key="i"
      :class="m.role === 'user' ? 'user-message' : 'assistant-message'"
    >
      <span v-if="m.role === 'user'">{{ m.content }}</span>

      <div v-else-if="m.content.text === ''" class="loading-response">
        <ProgressSpinner
          style="width: 1rem; height: 1rem; margin: 0"
          strokeWidth="10"
          animationDuration=".3s"
        />
        <span>Reading your Resources...</span>
      </div>

      <template v-else>
        <VueMarkdown :source="m.content.text" />
        <template v-if="m.content.citations.length > 0">
          <Divider />
          <div class="citations">
            <h3>Sources:</h3>
            <AssistantCitation
              v-for="(id, index) in m.content.citations"
              :key="id"
              :chunk-id="id"
              :citation-number="index + 1"
            />
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<style scoped>
.message-list {
  display: flex;
  flex-direction: column;
  width: 100%;
  flex-grow: 1;
  gap: 1rem;
  overflow-y: auto;
  padding: 2rem 2rem 4rem 2rem;
}

.user-message {
  padding: 1rem;
  max-width: 80%;
  border-radius: var(--p-form-field-border-radius);
  background-color: var(--p-secondary-color);
  align-self: flex-end;
}

.assistant-message {
  padding: 1rem;
  width: 100%;
}

.loading-response {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.citations {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}
</style>
