<script setup lang="ts">
import { ref } from "vue";
import InputGroup from "primevue/inputgroup";
import InputText from "primevue/inputtext";
import InputGroupAddon from "primevue/inputgroupaddon";
import Password from "primevue/password";
import Button from "primevue/button";
import Divider from "primevue/divider";
import { Form, type FormSubmitEvent } from "@primevue/forms";
import { z } from "zod";
import { zodResolver } from "@primevue/forms/resolvers/zod";
import { useRouter } from "vue-router";
import { useApi } from "@/api/use-api";
import routes from "@/api/routes";
import type { TokensWithUser } from "@/types/api";
import { useSessionStore } from "@/stores/session-store";

const initialValues = ref({
  email: "",
  password: "",
});

const resolver = zodResolver(
  z.object({
    email: z.string().email(),
    password: z.string().min(1),
  }),
);

const router = useRouter();
const sessionStore = useSessionStore();

const { post, loading } = useApi(routes.auth.post.login, true);

const onFormSubmit = async (e: FormSubmitEvent) => {
  if (!e.valid) return;

  const form = new FormData();
  form.append("username", e.values.email);
  form.append("password", e.values.password);

  const response = await post<TokensWithUser, FormData>({
    data: form,
    successMessage: "Welcome back!",
  });

  if (!response) return;

  sessionStore.storeSession(response.data);
  router.push("/");
};
</script>

<template>
  <div class="login-page">
    <Form
      class="form"
      :initial-values="initialValues"
      :resolver="resolver"
      @submit="onFormSubmit"
      v-slot="$form"
    >
      <InputGroup>
        <InputGroupAddon>
          <i class="pi pi-at"></i>
        </InputGroupAddon>
        <InputText name="email" placeholder="E-Mail" />
      </InputGroup>

      <InputGroup>
        <InputGroupAddon>
          <i class="pi pi-lock"></i>
        </InputGroupAddon>
        <Password name="password" :feedback="false" toggle-mask placeholder="Password" />
      </InputGroup>

      <Button
        :disabled="!$form.valid || $form.email?.pristine || $form.password?.pristine"
        :loading="loading"
        fluid
        label="Login"
        type="submit"
      />
    </Form>

    <Divider style="margin: 0" />
    <Button as="router-link" fluid severity="secondary" label="Register" to="/auth/register" />
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 20rem;
  align-self: center;
}

.form {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 1rem;
}
</style>
