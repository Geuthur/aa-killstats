import { apiClient } from "@/Api/Api";
import type { components } from "@/Api/OpenApi";
import type { CombatStatsResponse, CombatSummaryResponse, HallResponse, KillmailListResponse, TopPilotsResponse  } from "@/Api/schema";
import { ProjectName } from "@/App";


export async function loadUserData(): Promise<{ user: components["schemas"]["UserData"] }> {
  const { data, error } = await apiClient.GET(`/${ProjectName}/api/user/`);
  if (error || !data) {
    throw new Error("Failed to load user data");
  }
  return { user: data };
}

export async function loadMenu(): Promise<components["schemas"]["MenuSchema"]> {
  const { data, error } = await apiClient.GET(`/${ProjectName}/api/menu/`);
  if (error || !data) {
    throw new Error("Failed to load menu");
  }
  return data;
}

export interface OverviewEntity {
  id: number;
  name: string;
}

export async function loadCorporationsOverview(): Promise<OverviewEntity[]> {
  const { data, error } = await apiClient.GET(`/${ProjectName}/api/killboard/corporation/admin/`);
  if (error || !data) {
    throw new Error("Failed to load corporation overview");
  }

  const entities: OverviewEntity[] = [];
  for (const item of data) {
    if (item.corporation) {
      for (const val of Object.values(item.corporation)) {
        const corp = val as { corporation_id?: number; corporation_name?: string };
        if (corp?.corporation_id && corp?.corporation_name) {
          entities.push({
            id: corp.corporation_id,
            name: corp.corporation_name,
          });
        }
      }
    }
  }

  return entities.sort((a, b) => a.name.localeCompare(b.name));
}

export async function loadAlliancesOverview(): Promise<OverviewEntity[]> {
  const { data, error } = await apiClient.GET(`/${ProjectName}/api/killboard/alliance/admin/`);
  if (error || !data) {
    throw new Error("Failed to load alliance overview");
  }

  const entities: OverviewEntity[] = [];
  for (const item of data) {
    if (item.alliance) {
      for (const val of Object.values(item.alliance)) {
        const alliance = val as { alliance_id?: number; alliance_name?: string };
        if (alliance?.alliance_id && alliance?.alliance_name) {
          entities.push({
            id: alliance.alliance_id,
            name: alliance.alliance_name,
          });
        }
      }
    }
  }

  return entities.sort((a, b) => a.name.localeCompare(b.name));
}

// ---------------------------------------------------------------------------
// Killboard Combat Stats & Summaries (OpenAPI)
// ---------------------------------------------------------------------------

export async function fetchCombatStats(
  year: number | "all",
  month: number | "all",
  entityType: string,
  entityId: number
): Promise<CombatStatsResponse> {
  const y = year === "all" ? 0 : year;
  const m = month === "all" ? 0 : month;
  const { data, error } = await apiClient.GET(
    "/killstats/api/stats/v2/year/{year}/month/{month}/{entity_type}/{entity_id}/",
    {
      params: {
        path: {
          year: y,
          month: m,
          entity_type: entityType as "alliance" | "corporation" | "character",
          entity_id: entityId,
        },
      },
    }
  );
  if (error || !data) {
    throw new Error("Failed to fetch combat stats");
  }
  return data as unknown as CombatStatsResponse;
}

export async function fetchCombatSummary(
  year: number | "all",
  month: number | "all",
  entityType: string,
  entityId: number
): Promise<CombatSummaryResponse> {
  const y = year === "all" ? 0 : year;
  const m = month === "all" ? 0 : month;
  const { data, error } = await apiClient.GET(
    "/killstats/api/stats/v2/summary/year/{year}/month/{month}/{entity_type}/{entity_id}/",
    {
      params: {
        path: {
          year: y,
          month: m,
          entity_type: entityType,
          entity_id: entityId,
        },
      },
    }
  );
  if (error || !data) {
    throw new Error("Failed to fetch combat summary");
  }
  return data as unknown as CombatSummaryResponse;
}

export async function fetchTopAttackers(
  year: number | "all",
  month: number | "all",
  entityType: string,
  entityId: number
): Promise<TopPilotsResponse> {
  const y = year === "all" ? 0 : year;
  const m = month === "all" ? 0 : month;
  const { data, error } = await apiClient.GET(
    "/killstats/api/stats/v2/attackers/year/{year}/month/{month}/{entity_type}/{entity_id}/",
    {
      params: {
        path: {
          year: y,
          month: m,
          entity_type: entityType,
          entity_id: entityId,
        },
      },
    }
  );
  if (error || !data) {
    throw new Error("Failed to fetch top attackers");
  }
  return data as unknown as TopPilotsResponse;
}

export async function fetchTopVictims(
  year: number | "all",
  month: number | "all",
  entityType: string,
  entityId: number
): Promise<TopPilotsResponse> {
  const y = year === "all" ? 0 : year;
  const m = month === "all" ? 0 : month;
  const { data, error } = await apiClient.GET(
    "/killstats/api/stats/v2/victims/year/{year}/month/{month}/{entity_type}/{entity_id}/",
    {
      params: {
        path: {
          year: y,
          month: m,
          entity_type: entityType,
          entity_id: entityId,
        },
      },
    }
  );
  if (error || !data) {
    throw new Error("Failed to fetch top victims");
  }
  return data as unknown as TopPilotsResponse;
}

export async function fetchHallStats(
  year: number | "all",
  month: number | "all",
  entityType: string,
  entityId: number
): Promise<HallResponse> {
  const y = year === "all" ? 0 : year;
  const m = month === "all" ? 0 : month;
  const { data, error } = await apiClient.GET(
    "/killstats/api/hall/v2/year/{year}/month/{month}/{entity_type}/{entity_id}/",
    {
      params: {
        path: {
          year: y,
          month: m,
          entity_type: entityType as "alliance" | "corporation" | "character",
          entity_id: entityId,
        },
      },
    }
  );
  if (error || !data) {
    throw new Error("Failed to fetch hall stats");
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
  const y = year === "all" ? 0 : year;
  const m = month === "all" ? 0 : month;
  const { data, error } = await apiClient.GET(
    "/killstats/api/killmails/v2/year/{year}/month/{month}/{entity_type}/{entity_id}/",
    {
      params: {
        path: {
          year: y,
          month: m,
          entity_type: entityType as "alliance" | "corporation" | "character",
          entity_id: entityId,
        },
        query: {
          mode,
          page,
          page_size: pageSize,
        },
      },
    }
  );
  if (error || !data) {
    throw new Error("Failed to fetch killmails");
  }
  return data as unknown as KillmailListResponse;
}
