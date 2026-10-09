// React
import ReactDOM from "react-dom";

// Third Party
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";

import { loadMenu, loadUserData } from "@/Api/ApiCalls";
import { queryKeys } from "@/Api/query";
import AuthLeftMenu from "@/Menu/AuthLeftMenu";
import type { MenuLinkItem } from "@/Menu/BaseMenu";

const AuthLeftMenuAsync = () => {
  const { t } = useTranslation();
  const menuRoot =
    typeof document !== "undefined" ? document.getElementById("nav-left") : null;

  const {
    isLoading: isUserLoading,
    error: userError,
    data: userData,
  } = useQuery({
    queryKey: queryKeys.User,
    queryFn: () => loadUserData(),
    staleTime: 5 * 60 * 1000,
  });

  const { data: menuData } = useQuery({
    queryKey: queryKeys.Menu,
    queryFn: () => loadMenu(),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  if (!menuRoot) {
    return <></>;
  }

  let links: MenuLinkItem[] = [];

  if (userData?.user) {
    const user = userData.user;
    if (user.corporation_id) {
      links.push({
        name: user.corporation_name || t("Corporation"),
        link: `/v2/corporation/${user.corporation_id}/`,
        is_external: false,
      });
    }

    if (user.alliance_id) {
      links.push({
        name: user.alliance_name || t("Alliance"),
        link: `/v2/alliance/${user.alliance_id}/`,
        is_external: false,
      });
    }

    links.push({
      name: t("Corporation Overview"),
      link: "/overview/corporations/",
      is_external: false,
    });

    if (user.alliance_id || user.is_admin) {
      links.push({
        name: t("Alliance Overview"),
        link: "/overview/alliances/",
        is_external: false,
      });
    }
  } else if (menuData?.left_links) {
    links = menuData.left_links;
  }

  if (links.length === 0 && isUserLoading) {
    return <></>;
  }

  return ReactDOM.createPortal(
    <AuthLeftMenu
      error={Boolean(userError)}
      isLoading={isUserLoading}
      data={links}
    />,
    menuRoot,
  );
};

export default AuthLeftMenuAsync;
