// React
import { useState } from "react";
import { Link } from "react-router-dom";

// Third Party
import { useQuery } from "@tanstack/react-query";
import { ExternalLink, Plus, Search, Shield } from "lucide-react";
import { useTranslation } from "react-i18next";

// AA Killstats
import {
  loadAlliancesOverview,
  loadCorporationsOverview,
  loadUserData,
} from "@/Api/ApiCalls";
import { queryKeys } from "@/Api/query";
import { ProjectName } from "@/App";
import { FetchingLoader } from "@/Components/Loader";

export interface OverviewPageProps {
  entityType: "corporation" | "alliance";
}

export function OverviewPage({ entityType }: OverviewPageProps) {
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState("");

  const isCorp = entityType === "corporation";

  // Load user data to check for admin permissions
  const { data: userData } = useQuery({
    queryKey: queryKeys.User,
    queryFn: () => loadUserData(),
    staleTime: 5 * 60 * 1000,
  });

  const isAdmin = Boolean(userData?.user?.is_admin);

  // Load entities
  const { data: entities = [], isLoading, error } = useQuery({
    queryKey: queryKeys.Overview(entityType),
    queryFn: () =>
      isCorp ? loadCorporationsOverview() : loadAlliancesOverview(),
  });

  const filteredEntities = entities.filter((item) =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.id.toString().includes(searchTerm)
  );

  const title = isCorp ? t("Corporation Overview") : t("Alliance Overview");
  const subtitle = isCorp
    ? t("Overview of all tracked corporations in Killstats.")
    : t("Overview of all tracked alliances in Killstats.");

  const addUrl = isCorp
    ? `/${ProjectName}/add_corp/`
    : `/${ProjectName}/add_alliance/`;
  const addLabel = isCorp ? t("Add Corporation") : t("Add Alliance");

  return (
    <div className="flex flex-col gap-6 text-gray-100 p-4 max-w-7xl mx-auto">
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-zinc-900/60 border-killstats p-6 rounded-xl shadow-sm backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl text-blue-400">
            <Shield className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-wide text-white m-0">
              {title}
            </h1>
            <p className="text-xs sm:text-sm text-zinc-400 m-0 mt-1">{subtitle}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {isAdmin && (
            <button
              type="button"
              onClick={() => window.location.href = addUrl}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg text-sm transition-all shadow-md shadow-blue-900/20"
            >
              <Plus className="w-4 h-4" />
              <span>{addLabel}</span>
            </button>
          )}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex items-center gap-3 bg-zinc-900/60 border-killstats px-4 py-3 rounded-xl shadow-sm backdrop-blur-md">
        <Search className="w-5 h-5 text-zinc-400" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder={t("Filter by name or ID...")}
          className="bg-transparent border-0 focus:outline-none text-white text-sm w-full placeholder-zinc-500"
        />
        {searchTerm && (
          <button
            onClick={() => setSearchTerm("")}
            className="text-xs text-zinc-400 hover:text-white px-2 py-1 bg-zinc-800 rounded border border-zinc-700 cursor-pointer"
          >
            {t("Clear")}
          </button>
        )}
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="bg-zinc-900/60 border-killstats rounded-xl p-12 flex items-center justify-center min-h-[300px] backdrop-blur-md">
          <FetchingLoader message={t("Loading overview...")} />
        </div>
      ) : error ? (
        <div className="bg-red-950/20 border-killstats rounded-xl p-8 text-center text-red-300">
          <p className="text-sm font-medium">
            {t("Failed to load overview data.")}
          </p>
        </div>
      ) : filteredEntities.length === 0 ? (
        <div className="bg-zinc-900/40 border-killstats rounded-xl p-12 text-center text-zinc-400">
          <p className="text-sm">{t("No entries found.")}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filteredEntities.map((item) => {
            const logoUrl = isCorp
              ? `https://images.evetech.net/corporations/${item.id}/logo?size=64`
              : `https://images.evetech.net/alliances/${item.id}/logo?size=64`;

            const killboardUrl = `/${ProjectName}/v2/${entityType}/${item.id}/`;

            return (
              <div
                key={item.id}
                className="bg-zinc-900/60 hover:bg-zinc-800/80 border-killstats hover:border-blue-500/50 transition-all rounded-xl p-5 flex flex-col justify-between group shadow-sm backdrop-blur-md"
              >
                <div className="flex items-center gap-3.5 mb-4">
                  <img
                    src={logoUrl}
                    alt={item.name}
                    className="w-12 h-12 rounded-lg bg-zinc-900 border-killstats object-cover shrink-0"
                    loading="lazy"
                  />
                  <div className="min-w-0 flex-1">
                    <h3 className="text-sm font-bold text-white group-hover:text-blue-400 transition-colors truncate m-0">
                      {item.name}
                    </h3>
                    <span className="text-xs text-zinc-500 font-mono">
                      ID: {item.id}
                    </span>
                  </div>
                </div>

                <Link
                  to={killboardUrl}
                  className="w-full flex items-center justify-center gap-1.5 py-2 px-3 bg-zinc-700/50 hover:bg-blue-600 text-zinc-200 hover:text-white rounded-lg text-xs font-semibold transition-all mt-auto"
                >
                  <span>{t("View Killboard")}</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </Link>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default OverviewPage;
