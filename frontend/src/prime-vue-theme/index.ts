import Aura from "@primeuix/themes/aura";
import { definePreset } from "@primeuix/themes";

import semantic from "@/prime-vue-theme/semantic";
import components from "@/prime-vue-theme/components";
import type { Preset } from "@primeuix/themes/types";

const presetExtension: Preset = {
  semantic,
  components,
};

const preset = definePreset(Aura, presetExtension);

export const DARK_MODE_CLASS = "dark-mode";

const options = { darkModeSelector: `.${DARK_MODE_CLASS}` };

export default { theme: { preset, options } };
