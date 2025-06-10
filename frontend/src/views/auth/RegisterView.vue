<script setup lang="ts">
import { ref } from "vue";
import InputGroup from "primevue/inputgroup";
import InputText from "primevue/inputtext";
import InputGroupAddon from "primevue/inputgroupaddon";
import Password from "primevue/password";
import Button from "primevue/button";
import Divider from "primevue/divider";
import FloatLabel from "primevue/floatlabel";
import Message from "primevue/message";
import { Form, type FormSubmitEvent } from "@primevue/forms";
import { z } from "zod";
import { zodResolver } from "@primevue/forms/resolvers/zod";
import { useRouter } from "vue-router";
import type { CreateUserBody, TokensWithUser } from "@/types/api";
import { useThemeStore } from "@/stores/theme-store";
import { useApi } from "@/api/use-api";
import routes from "@/api/routes";
import { useSessionStore } from "@/stores/session-store";

const { breakpoints } = useThemeStore();
const isMobile = breakpoints.smaller("tablet");

const initialValues = ref({
  first_name: "",
  last_name: "",
  email: "",
  password: "",
  repeat_password: "",
});

const resolver = zodResolver(
  z.object({
    first_name: z.string().min(1).max(50),
    last_name: z.string().min(1).max(50),
    email: z.string().email(),
    password: z
      .string()
      .min(8)
      .max(50)
      .refine((value) => /[a-z]/.test(value), "Must have a lowercase letter.")
      .refine((value) => /[A-Z]/.test(value), "Must have an uppercase letter."),
    repeat_password: z.string().min(1),
  }),
);

const { post, loading } = useApi(routes.auth.post.register, true);
const router = useRouter();
const sessionStore = useSessionStore();

const onFormSubmit = async (e: FormSubmitEvent) => {
  if (!e.valid) return;

  const body: CreateUserBody = {
    first_name: e.values.first_name,
    last_name: e.values.last_name,
    email: e.values.email,
    password: e.values.password,
  };

  const response = await post<TokensWithUser, CreateUserBody>({
    data: body,
    successMessage: "User created successfully.",
  });

  if (!response?.data) return;

  sessionStore.storeSession(response.data);
  router.push("/");
};
</script>

<template>
  <div class="register-page">
    <Form
      class="form"
      :initial-values="initialValues"
      :resolver="resolver"
      validate-on-blur
      validate-on-submit
      :validate-on-value-update="false"
      @submit="onFormSubmit"
      v-slot="$form"
    >
      <div class="form-group" :class="{ 'form-group-mobile': isMobile }">
        <InputGroup>
          <InputGroupAddon>
            <i class="pi pi-id-card"></i>
          </InputGroupAddon>
          <FloatLabel variant="on">
            <InputText name="first_name" />
            <label for="first_name">First Name</label>
          </FloatLabel>
          <FloatLabel variant="on">
            <InputText name="last_name" />
            <label for="last_name">Last Name</label>
          </FloatLabel>
        </InputGroup>
        <Message v-if="$form.first_name?.invalid" severity="error" size="small" variant="simple">
          {{ $form.first_name.error.message }}
        </Message>
        <Message v-if="$form.last_name?.invalid" severity="error" size="small" variant="simple">
          {{ $form.last_name.error.message }}
        </Message>

        <InputGroup>
          <InputGroupAddon>
            <i class="pi pi-at"></i>
          </InputGroupAddon>
          <FloatLabel variant="on">
            <InputText name="email" />
            <label for="email">E-Mail</label>
          </FloatLabel>
        </InputGroup>
        <Message v-if="$form.email?.invalid" severity="error" size="small" variant="simple">
          {{ $form.email.error.message }}
        </Message>

        <InputGroup>
          <InputGroupAddon>
            <i class="pi pi-lock"></i>
          </InputGroupAddon>
          <FloatLabel variant="on">
            <Password name="password" :feedback="false" toggle-mask />
            <label for="password">Password</label>
          </FloatLabel>
        </InputGroup>
        <Message v-if="$form.password?.invalid" severity="error" size="small" variant="simple">
          {{ $form.password.error.message }}
        </Message>

        <InputGroup>
          <InputGroupAddon>
            <i class="pi pi-lock"></i>
          </InputGroupAddon>
          <FloatLabel variant="on">
            <Password name="repeat_password" :feedback="false" toggle-mask />
            <label for="repeat_password">Repeat Password</label>
          </FloatLabel>
        </InputGroup>
        <Message
          v-if="
            $form.repeat_password?.invalid || $form.repeat_password?.dirty
              ? $form.repeat_password?.value !== $form.password?.value
              : false
          "
          severity="error"
          size="small"
          variant="simple"
        >
          {{ $form.repeat_password?.error?.message || "Passwords do not match" }}
        </Message>
      </div>
      <Button
        :disabled="
          !$form.valid ||
          $form.first_name?.pristine ||
          $form.last_name?.pristine ||
          $form.email?.pristine ||
          $form.password?.pristine ||
          $form.repeat_password?.pristine ||
          $form.repeat_password?.value !== $form.password?.value
        "
        :loading="loading"
        fluid
        label="Register"
        type="submit"
      />
    </Form>
    <Divider style="margin: 0" />
    <Button as="router-link" fluid severity="secondary" label="Login" to="/auth/login" />
  </div>
</template>

<style scoped>
.register-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 30rem;
  align-self: center;
}

.form {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
</style>
