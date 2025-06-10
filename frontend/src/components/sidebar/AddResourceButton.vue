<script setup lang="ts">
import routes from "@/api/routes";
import { useApi } from "@/api/use-api";
import { useResourceStore } from "@/stores/resource-store";
import type { Resource } from "@/types/api";
import { useDropZone } from "@vueuse/core";
import { storeToRefs } from "pinia";
import { Button, Dialog } from "primevue";
import { ref, useTemplateRef } from "vue";

const visible = ref(false);
const file = ref<File | null>(null);
const dropzone = useTemplateRef("dropzone");

const { post: createPdfResource, loading } = useApi(routes.resources.post.createPdfResource);
const resourceStore = useResourceStore();
const { resources, selectedResourceIds } = storeToRefs(resourceStore);

const onSubmit = async () => {
  if (loading.value) return;
  if (!file.value) return;

  const formData = new FormData();
  formData.append("file", file.value);

  const response = await createPdfResource<Resource, FormData>({
    data: formData,
    successMessage: "Resource added successfully!",
  });
  if (!response) return;

  resources.value.push(response.data);
  selectedResourceIds.value.add(response.data._id);

  visible.value = false;
};

const onDrop = (droppedFiles: File[] | null) => {
  if (!droppedFiles || droppedFiles.length === 0) return;
  file.value = droppedFiles[0];
};

const { isOverDropZone } = useDropZone(dropzone, {
  onDrop,
  dataTypes: ["application/pdf"],
  multiple: false,
});

const handleClose = () => {
  file.value = null;
};
</script>

<template>
  <Button fluid icon="pi pi-plus" label="Add Resource" @click="visible = true" />

  <Dialog
    v-model:visible="visible"
    modal
    header="Add Resource"
    :style="{ width: '25rem' }"
    @after-hide="handleClose"
  >
    <div class="dialog-content">
      <p>Add a Resource to include it in your Chats. Currently, only PDF files are supported.</p>
      <div ref="dropzone" class="dropzone" :class="{ 'dropzone-dragover': isOverDropZone }">
        <div class="dropzone-content" v-if="!file && !isOverDropZone">
          <i class="pi pi-file" style="font-size: 3rem"></i>
          <h3>Drop a file here</h3>
        </div>

        <div class="dropzone-content" v-if="isOverDropZone">
          <i class="pi pi-file-plus" style="font-size: 3rem"></i>
          <h3>Drop a file here</h3>
        </div>

        <div class="dropzone-content" v-else-if="file">
          <i class="pi pi-file-check" style="font-size: 3rem"></i>
          <h3>{{ file.name }}</h3>
          <p>{{ (file.size / 1024 / 1024).toFixed(2) }} MB</p>
        </div>
      </div>
      <Button label="Submit" :disabled="!file || loading" :loading="loading" @click="onSubmit" />
    </div>
  </Dialog>
</template>

<style scoped>
.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.dropzone {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 12rem;
  border: 2px dashed var(--p-text-muted-color);
  border-radius: 0.5rem;
  color: var(--p-text-muted-color);
  transition:
    background-color 0.2s ease,
    color 0.2s ease,
    border-color 0.2s ease;
}

.dropzone-dragover {
  background-color: var(--p-surface-900);
  color: var(--p-text-color);
  border-color: var(--p-text-color);
}

.dropzone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}
</style>
