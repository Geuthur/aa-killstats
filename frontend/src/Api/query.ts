// Third Party
import { queryKeys as baseQueryKeys } from "aa-geuthur-react";

// `Menu`, `User` and `UserSettings` come from the package, so its hooks and the app share them.
export const queryKeys = {
  ...baseQueryKeys,
  Overview: (entityType: string) => ["overview", entityType] as const,
  CombatSummary: (
    year: number | "all",
    month: number | "all",
    entityType: string,
    entityId: number
  ) => ["combatSummary", year, month, entityType, entityId] as const,
  TopAttackers: (
    year: number | "all",
    month: number | "all",
    entityType: string,
    entityId: number
  ) => ["topAttackers", year, month, entityType, entityId] as const,
  TopVictims: (
    year: number | "all",
    month: number | "all",
    entityType: string,
    entityId: number
  ) => ["topVictims", year, month, entityType, entityId] as const,
  HallStats: (
    year: number | "all",
    month: number | "all",
    entityType: string,
    entityId: number
  ) => ["hallStats", year, month, entityType, entityId] as const,
  Killmails: (
    year: number | "all",
    month: number | "all",
    entityType: string,
    entityId: number,
    mode: "all" | "kills" | "losses" = "all",
    page: number = 1,
    pageSize: number = 25
  ) => ["killmails", year, month, entityType, entityId, mode, page, pageSize] as const,
};
