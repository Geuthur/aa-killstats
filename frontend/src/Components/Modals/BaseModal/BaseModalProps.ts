import type { components } from "@/Api/OpenApi";

export const ModalSize = {
  small: "sm",
  medium: undefined, // Bootstrap Standardgröße
  large: "lg",
  extraLarge: "xl",
} as const;

export type ModalSize = (typeof ModalSize)[keyof typeof ModalSize];
export type ModalData = components['schemas']['ModalSchema']
