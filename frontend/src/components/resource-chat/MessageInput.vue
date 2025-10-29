<script setup lang="ts">
import { InputText, Button, InputGroup, InputGroupAddon } from "primevue";
import { ref } from "vue";

// const { disabled } = defineProps<{ disabled: boolean }>();
const { disabled, canExport, exporting = false } = defineProps<{
  disabled: boolean;
  canExport: boolean;
  exporting?: boolean;
}>();

const messageInput = ref<string>("");
const emit = defineEmits<{
  submit: [message: string];
  export: [];
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
    <div class="bg"></div>
    <InputGroup class="message-input-group">
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

      <InputGroupAddon>
        <Button
          :disabled="disabled || !canExport || exporting"
          icon="pi pi-download"
          aria-label="Export conversation"
          @click="emit('export')"
        />
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
  padding: 2rem;
  padding-top: 0;
  position: absolute;
  bottom: 0;
}

.message-input-group {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  z-index: 1;
}

.bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 1rem;
  bottom: 0;
  background: var(--background-color);
}

.bg::before {
  content: "";
  position: absolute;
  top: -2rem;
  left: 0;
  right: 1rem;
  height: 2rem;
  background: linear-gradient(to bottom, transparent, var(--background-color));
}
</style>
