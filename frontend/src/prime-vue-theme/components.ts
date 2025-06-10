import type { ComponentsDesignTokens } from "@primeuix/themes/types";

const components: ComponentsDesignTokens = {
  tag: {
    colorScheme: {
      light: {
        primary: {
          background: "{primary.color}",
          color: "{primary.contrastColor}",
        },
      },
      dark: {
        primary: {
          background: "{primary.color}",
          color: "{primary.contrastColor}",
        },
      },
    },
  },
  inputtext: {
    colorScheme: {
      light: {
        root: {
          borderColor: "{zinc.400}",
          color: "{zinc.900}",
          placeholderColor: "{zinc.500}",
          focusBorderColor: "{primary.color}",
          disabledColor: "{zinc.300}",
          disabledBackground: "{zinc.100}",
          invalidBorderColor: "{red.500}",
        },
      },
      dark: {
        root: {
          borderColor: "{zinc.600}",
          color: "{zinc.100}",
          placeholderColor: "{zinc.500}",
          focusBorderColor: "{primary.color}",
          disabledColor: "{zinc.300}",
          disabledBackground: "{zinc.800}",
          invalidBorderColor: "{red.500}",
        },
      },
    },
  },
  progressspinner: {
    colorScheme: {
      light: {
        root: {
          colorOne: "{primary.color}",
          colorTwo: "{primary.color}",
          colorThree: "{primary.color}",
          colorFour: "{primary.color}",
        },
      },
      dark: {
        root: {
          colorOne: "{primary.color}",
          colorTwo: "{primary.color}",
          colorThree: "{primary.color}",
          colorFour: "{primary.color}",
        },
      },
    },
  },
  chip: {
    root: {
      borderRadius: "0.25rem",
    },
  },
  button: {
    colorScheme: {
      light: {
        root: {
          primary: {
            background: "{primary.color}",
            color: "{primary.contrastColor}",
            hoverBackground: "{primary.hoverColor}",
            hoverColor: "{primary.contrastColor}",
            activeBackground: "{primary.activeColor}",
            activeColor: "{primary.contrastColor}",
          },
          secondary: {
            background: "{secondary.color}",
            color: "{secondary.contrastColor}",
            hoverBackground: "{secondary.hoverColor}",
            hoverColor: "{secondary.contrastColor}",
            activeBackground: "{secondary.activeColor}",
            activeColor: "{secondary.contrastColor}",
          },
        },
        text: {
          primary: {
            hoverBackground: "{surface.200}",
          },
        },
      },
      dark: {
        root: {
          primary: {
            background: "{primary.color}",
            color: "{primary.contrastColor}",
            hoverBackground: "{primary.hoverColor}",
            hoverColor: "{primary.contrastColor}",
            activeBackground: "{primary.activeColor}",
            activeColor: "{primary.contrastColor}",
          },
          secondary: {
            background: "{secondary.color}",
            color: "{secondary.contrastColor}",
            hoverBackground: "{secondary.hoverColor}",
            hoverColor: "{secondary.contrastColor}",
            activeBackground: "{secondary.activeColor}",
            activeColor: "{secondary.contrastColor}",
          },
        },
      },
    },
  },
};

export default components;
