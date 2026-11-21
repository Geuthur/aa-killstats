// Third Party
import { apiErrorMessage } from "aa-geuthur-react";

// AA Killstats
import { apiClient } from "@/Api/Api";
import type { CombatSummaryResponse, HallResponse, KillmailListResponse, TopPilotsResponse } from "@/Api/schema";

/** Query keys of the killboard area: combat summary, top pilots, hall of fame/shame and killmails of one entity. */
export const killboardQueryKeys = {
  combatSummary: (
    year: number | "all",
    month: number | "all",
    entityType: string,
    entityId: number
  ) => ["combatSummary", year, month, entityType, entityId] as const,
  topAttackers: (
    year: number | "all",
    month: number | "all",
    entityType: string,
    entityId: number
  ) => ["topAttackers", year, month, entityType, entityId] as const,
  topVictims: (
    year: number | "all",
    month: number | "all",
    entityType: string,
    entityId: number
  ) => ["topVictims", year, month, entityType, entityId] as const,
  hallStats: (
    year: number | "all",
    month: number | "all",
    entityType: string,
    entityId: number
  ) => ["hallStats", year, month, entityType, entityId] as const,
  killmails: (
    year: number | "all",
    month: number | "all",
    entityType: string,
    entityId: number,
    mode: "all" | "kills" | "losses" = "all",
    page: number = 1,
    pageSize: number = 25
  ) => ["killmails", year, month, entityType, entityId, mode, page, pageSize] as const,
};

export async function fetchCombatSummary(
  year: number | "all",
  month: number | "all",
  entityType: string,
  entityId: number
): Promise<CombatSummaryResponse> {
  const query: Record<string, number> = {};
  if (year !== "all") query.year = year;
  if (month !== "all") query.month = month;

  const { data, error } = await apiClient.GET(
    "/killstats/api/stats/v2/summary/{entity_type}/{entity_id}/",
    {
      params: {
        path: {
          entity_type: entityType as "alliance" | "corporation" | "character",
          entity_id: entityId,
        },
        query,
      },
    }
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to fetch combat summary"));
  }
  return data as unknown as CombatSummaryResponse;
}

export async function fetchTopAttackers(
  year: number | "all",
  month: number | "all",
  entityType: string,
  entityId: number
): Promise<TopPilotsResponse> {
  const query: Record<string, number> = {};
  if (year !== "all") query.year = year;
  if (month !== "all") query.month = month;

  const { data, error } = await apiClient.GET(
    "/killstats/api/stats/v2/attackers/{entity_type}/{entity_id}/",
    {
      params: {
        path: {
          entity_type: entityType as "alliance" | "corporation" | "character",
          entity_id: entityId,
        },
        query,
      },
    }
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to fetch top attackers"));
  }
  return data as unknown as TopPilotsResponse;
}

export async function fetchTopVictims(
  year: number | "all",
  month: number | "all",
  entityType: string,
  entityId: number
): Promise<TopPilotsResponse> {
  const query: Record<string, number> = {};
  if (year !== "all") query.year = year;
  if (month !== "all") query.month = month;

  const { data, error } = await apiClient.GET(
    "/killstats/api/stats/v2/victims/{entity_type}/{entity_id}/",
    {
      params: {
        path: {
          entity_type: entityType as "alliance" | "corporation" | "character",
          entity_id: entityId,
        },
        query,
      },
    }
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to fetch top victims"));
  }
  return data as unknown as TopPilotsResponse;
}

export async function fetchHallStats(
  year: number | "all",
  month: number | "all",
  entityType: string,
  entityId: number
): Promise<HallResponse> {
  const query: Record<string, number> = {};
  if (year !== "all") query.year = year;
  if (month !== "all") query.month = month;

  const { data, error } = await apiClient.GET(
    "/killstats/api/hall/v2/{entity_type}/{entity_id}/",
    {
      params: {
        path: {
          entity_type: entityType as "alliance" | "corporation" | "character",
          entity_id: entityId,
        },
        query,
      },
    }
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to fetch hall stats"));
  }
  return data as unknown as HallResponse;
}

export async function fetchKillmails(
  year: number | "all",
  month: number | "all",
  entityType: string,
  entityId: number,
  mode: "all" | "kills" | "losses" = "all",
  page: number = 1,
  pageSize: number = 25
): Promise<KillmailListResponse> {
  const queryParams: Record<string, unknown> = {
    mode,
    page,
    page_size: pageSize,
  };
  if (year !== "all") {
    queryParams.year = year;
  }
  if (month !== "all") {
    queryParams.month = month;
  }

  const { data, error } = await apiClient.GET(
    "/killstats/api/killmails/{entity_type}/{entity_id}/",
    {
      params: {
        path: {
          entity_type: entityType as "alliance" | "corporation" | "character",
          entity_id: entityId,
        },
        query: queryParams,
      },
    }
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to fetch killmails"));
  }
  return data as unknown as KillmailListResponse;
}
