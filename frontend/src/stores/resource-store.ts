import routes from "@/api/routes";
import { useApi } from "@/api/use-api";
import type { Chunk, Resource } from "@/types/api";
import { defineStore } from "pinia";
import { ref } from "vue";

export const useResourceStore = defineStore("resources", () => {
  const resources = ref<Resource[]>([]);
  const selectedResourceIds = ref<Set<string>>(new Set());
  const fetchedChunks = ref<Chunk[]>([]);

  const { get } = useApi(routes.resources.get.getResources);

  const fetchResources = async (query?: string) => {
    const response = await get<Resource[]>({
      config: { params: { query } },
    });

    if (!response) return;

    resources.value = response.data;
    response.data.forEach((r) => selectedResourceIds.value.add(r._id));
  };

  return { resources, selectedResourceIds, fetchedChunks, fetchResources };
});
