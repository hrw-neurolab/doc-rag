<script setup lang="ts">
import { InputText, Button, InputGroup, InputGroupAddon } from "primevue";
import { ref } from "vue";

const { disabled } = defineProps<{ disabled: boolean }>();

const messageInput = ref<string>("");
const emit = defineEmits<{
  submit: [message: string];
}>();

const handleSubmit = () => {
  const message = messageInput.value.trim();
  if (!message) return;

  emit("submit", message);
  messageInput.value = "";
};
</script>

<template>
  <div class="message-input">
    <InputGroup>
      <InputText
        :disabled="disabled"
        :style="{ flexGrow: 1 }"
        v-model="messageInput"
        placeholder="Ask something..."
        @keyup.enter="handleSubmit"
      />
      <InputGroupAddon>
        <Button :disabled="disabled" icon="pi pi-send" @click="handleSubmit" />
      </InputGroupAddon>
    </InputGroup>
  </div>
</template>

<style scoped>
.message-input {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
  max-width: 800px;
  padding: 2rem;
  padding-top: 0;
  position: relative;
  margin: 0 auto;
}

.message-input::after {
  content: "";
  position: absolute;
  top: -4rem;
  left: 0;
  width: 98%;
  height: 4rem;
  background: linear-gradient(to bottom, transparent, var(--background-color));
}
</style>
